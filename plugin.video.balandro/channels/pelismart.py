# -*- coding: utf-8 -*-

import re, time

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://pelismart.tv/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)

def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'genero/estrenos/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'DC Comics', action = 'list_all', url = host + 'genero/dc-comics/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'genero/marvel/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>CATEGORIAS<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if 'genero/estrenos/' in url: continue
        elif 'genero/dc-comics/' in url: continue
        elif 'genero/marvel/' in url: continue

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    itemlist.append(item.clone( action ='list_all', title ='Categoria', url= host + 'genero/categoria/' ))
    itemlist.append(item.clone( action ='list_all', title ='Suspense', url= host + 'genero/suspense/' ))
    itemlist.append(item.clone( action ='list_all', title ='Terror', url= host + 'genero/terror/' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1968, -1):
        url = host + 'Pelicula/year_relase/' + str(x) + '/'

        itemlist.append(item.clone( title=str(x), url = url, action='list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '<h3>' in data:
        bloque = scrapertools.find_single_match(data, '<h3>(.*?)</section>')
    else:
        bloque = scrapertools.find_single_match(data, '<h1>(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="col-mt-5(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if len(itemlist) == 20:
        if '<div class="pagenavi">' in data:
            next_page = scrapertools.find_single_match(data, '<span class="current">.*?<a href="(.*?)"')
            if next_page:
               itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral'))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '(?is)#embed.*?src="([^"]+).*?(?is)class="([^"]+)')

    for url, idioma in matches:
        if 'Latino' in idioma: lang = 'Lat'
        elif 'Español' in idioma: lang = 'Esp'
        elif 'Subtitulado' in idioma: lang = 'Vose'
        else:
           lang = idioma

        servidor = 'directo'

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = lang ))

    return itemlist


def resuelve_dame_toma(dame_url):
    data = do_downloadpage(dame_url)

    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
    if not url:
        checkUrl = dame_url.replace('embed.html#', 'details.php?v=')
        data = do_downloadpage(checkUrl, headers={'Referer': dame_url})
        url = scrapertools.find_single_match(data, '"file":\s*"([^"]+)').replace('\\/', '/')

    return url


def play(item):
    logger.info()
    itemlist = []

    url = httptools.downloadpage(item.url, follow_redirects=False).headers.get('location', '')

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if '/hqq.' in url or '/waaw.' in url or '/netu' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if '/damedamehoy.' in url or '//tomatomatela.' in url:
            url = resuelve_dame_toma(url)

            if url:
                itemlist.append(item.clone(url=url , server='directo'))
                return itemlist

        elif "peliscloud" in url:
            dom = '/'.join(url.split('/')[:3])
            vid = scrapertools.find_single_match(url, 'id=([^&]+)$')
            if not dom or not vid: return itemlist

            url = dom + '/playlist/' + vid + '/' + str(int(time.time() * 1000))
            data = httptools.downloadpage(url).data

            matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+)\s*(.*?\.m3u8)')
            if matches:
                for res, url in sorted(matches, key=lambda x: int(x[0]), reverse=True):
                    itemlist.append(item.clone(url = dom + url, server = 'm3u8hls'))
                    break

                return itemlist

        elif servidor == 'zplayer':
            url += '|%s' % item.url

        if url:
            itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

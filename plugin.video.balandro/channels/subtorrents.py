# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, os

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www.subtorrents.do/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.subtorrents.nl/', 'https://www.subtorrents.ch/', 'https://www.subtorrents.nz/', 
                 'https://www.subtorrents.in/', 'https://www.subtorrents.li/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ 2021-12-12  SIN PROXIES
	# ~ resp.code == 404
    timeout = 30
    raise_weberror = False

    # ~ resp = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror)
    resp = httptools.downloadpage_proxy('subtorrents', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror)

    data = ''
    if resp.data: data = resp.data

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data
    # ~ data = httptools.downloadpage_proxy('subtorrents', url, post=post, headers=headers, timeout=timeout, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', url = host, search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-subtituladas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Catálogo subtitulado', action = 'list_all',
                                url = host + 'peliculas-subtituladas/?filtro=audio-latino', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas-subtituladas/?filtro=estrenos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos subtitulado', action = 'list_all',
                               url = host + 'peliculas-subtituladas/?filtro=estrenos&filtro2=audio-latino', search_type = 'movie', ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_series', url = host + 'series-2/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action='alfabetico', search_type = 'tvshow' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En DVD', action = 'list_search', url = host + 'calidad/dvd-full/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 3D', action = 'list_search', url = host + 'peliculas-3d/', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<td class="vertThseccion">.*?<img src="(.*?)".*?<a href="(.*?)".*?title="(.*?)".*?<td>.*?<td>(.*?)</td>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for lang, url, title, qlty in matches:
        if not url or not title: continue

        title = title.split("(")[0]
        if "3D" in title: title = title.split("3D")[0]

        if lang.endswith("1.png"): lang = "Esp"
        elif lang.endswith("2.png"): lang = "VO"
        elif lang.endswith("4.png"): lang = "Fr"   
        elif lang.endswith("8.png"): lang = "It"
        elif lang.endswith("512.png"): lang = "Lat"
        else: lang = "Vose"

        itemlist.append(item.clone( action='findvideos', url=url, title=title, qualities=qlty, languages=lang,
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, "<span class='current'>\d+<\/span><a href='([^']+)'")
        if '/page/' in next_url:
            itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def list_series(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<table class="tablaseries2">(.*?)</table>')

    matches = re.compile('<td>.*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)"', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    for url, title, thumb in matches:
        if not url or not title: continue

        title = title.split("(")[0]

        if not host in url: url = host + url

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail = thumb,
                                    contentType='tvshow', contentSerieName=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, "<span class='current'>.*?<a href='([^']+)'")
        if '/page/' in next_url:
            itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_series', text_color='coral' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': url_letra = host + 'peliculas-subtituladas/?s=letra-'
    else: url_letra = host + 'series-2/?s=letra-'

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#':
        title = letra
        if letra == '#': letra = '0'

        url = url_letra + letra.lower()

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = "list_all", title = title, url = url))
        else:
            itemlist.append(item.clone( action = "list_series", title = title, url = url))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, r'">Temporada (\d+)<')

    for tempo in sorted(matches):
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url=item.url, contentType = 'season', contentSeason = int(tempo) ))

    return itemlist    


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)"[^>]+><a[^>]*title="[^"]+"'
    patron += '>\s*([^<]*)<\/a>\s*<\/td>\s*<td\s*class="capitulodescarga">\s*<a[^>]*href="([^"]+)"()()()'

    if not scrapertools.find_single_match(data, patron):
        patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)[^>]+>(?:<a\s*href="[^>]+>)?'
        patron += '(.*?)<\/a>\s*<\/td>\s*<td\s*class="capitulodescarga">\s*<a\s*href="([^"]+)[^>]+>'
        patron += '.*?(?:<td\s*class="capitulofecha">.*?(\d{4})?.*?<\/td>)?'
        patron += '(?:<td\s*class="capitulosubtitulo">\s*<a\s*href="([^"]+)[^>]+>.*?<\/td>)?'

        if not scrapertools.find_single_match(data, patron):
            patron = '<td\s*class="capitulonombre">\s*<img\s*src="([^"]+)[^>]+><a\s*'
            patron += '(?:target="[^"]*"\s*)?href="[^>]*title="([^"]+)">[^<]*<\/a>\s*<\/td>'
            patron += '\s*<td\s*class="capitulodescarga">\s*<a\s*(?:target="[^"]*"\s*)?'
            patron += 'href="([^"]+)"[^>]+>.*?(?:<td\s*class="capitulofecha">.*?(\d{4})?.*?<\/td>)?'
            patron += '.*?(?:<td\s*class="capitulosubtitulo">\s*<a\s*href="([^"]+)[^>]+>.*?<\/td>)?'
            patron += '.*?(?:<td\s*class="capitulodescarga">\s*<a\s*(?:target="[^"]*"\s*)?href="([^"]+)")?'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for lang, title, url, year, sub_tit, url_2 in matches:
        if not title: continue

        s_e = scrapertools.get_season_and_episode(title)

        season = int(s_e.split("x")[0])
        episode = s_e.split("x")[1]

        if not item.contentSeason: continue
        elif not str(item.contentSeason) == str(season): continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

    return sorted(itemlist, key=lambda x: x.contentEpisodeNumber)


def findvideos(item):
    logger.info()
    itemlist = []

    if item.contentType == "movie":
        data = do_downloadpage(item.url)
        url_torrent = scrapertools.find_single_match(data, '<a target="_blank".*?href="(.*?)"')
    else:
        url_torrent = item.url

    if url_torrent:
         itemlist.append(Item( channel = item.channel, action='play', title='', url=url_torrent, server='torrent',
                               quality=item.qualityes, language=item.languages))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if not item.url.endswith('.torrent'):
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'): item.url = url_base64

    if item.url.endswith('.torrent'):
        from platformcode import config

        if config.get_setting('proxies', item.channel, default=''):
            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, 'subtorrents')
            else:
                data = do_downloadpage(item.url)

            if data:
                try:
                   if 'Página no encontrada</title>' in str(data):
                       platformtools.dialog_ok('Subtorrents', '[COLOR yellow]Archivo no encontrado[/COLOR]')
                       return itemlist
                except:
                   pass

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))
        else:
            itemlist.append(item.clone( url = item.url, server = 'torrent' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<table class="searchResult">(.*?)</table>')
    matches = re.compile('<td class="vertThseccion">(.*?)</tr>', re.DOTALL).findall(bloque)

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="([^"]+)"')
        title = scrapertools.find_single_match(match, 'href=".*?title="([^"]+)"')
        if not url or not title: continue

        year = scrapertools.find_single_match(match, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(match, '<span>(\d{4})</span>')
        if not year: year = scrapertools.find_single_match(title, '\((\d{4})\)')

        if year:
            title = title.replace('(%s)' % year, '').strip()
        else:
            year = '-'

        title_clean = re.sub('\([^\)]+\)', '', title).strip()

        tipo = 'tvshow' if '/series/' in url else 'movie'

        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title_clean, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title_clean, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, "<span class='current'>.*?<a href='(.*?)'")
    if next_page:
       itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_search', text_color='coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []
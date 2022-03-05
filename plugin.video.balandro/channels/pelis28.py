# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pelis28.vip/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/fecha-estreno/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'news', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Amazon prime video', action = 'list_all', url = host + 'categoria/amazon-prime-video/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'categoria/netflix/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Sagas', action = 'sagas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def news(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    url = scrapertools.find_single_match(data, host + 'categoria/estrenos(.*?)">')

    if url:
        item.url = host + 'categoria/estrenos' + url
        return list_all(item)

    return itemllist


def sagas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'SAGAS(.*?)</ul>')
    matches = scrapertools.find_multiple_matches(bloque, '<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque1 = scrapertools.find_single_match(data, '<ul id="menu-menu"(.*?)</ul>')
    matches1 = scrapertools.find_multiple_matches(bloque1, '<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>')

    bloque2 = scrapertools.find_single_match(data, 'PELIS28</a>(.*?)</ul>')
    matches2 = scrapertools.find_multiple_matches(bloque2, '<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>')

    matches = matches1 + matches2

    for url, title in matches:
        if 'ESTRENOS' in title: continue
        elif 'GÉNEROS' in title: continue
        elif 'Netflix' in title: continue
        elif 'Amazon Prime Video' in title: continue
        elif 'Próximos Estrenos' in title: continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1969, -1):
        url = host + 'ver-pelicula/fecha-estreno/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'id="mt-(.*?)</div><div')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if '[' in title:
            title = title.replace('[', '{').replace(']', '}')
            title = scrapertools.find_single_match(title, '(.*?){').strip()

        qlty = scrapertools.find_single_match(match, '<span class="calidad2">(.*?)</span>')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        thumb = scrapertools.find_single_match(match, '<noscript>.*?<img style=".*?src="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=(qlty),
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')
        if next_url:
            if '/page/' in next_url:
               itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    _id = scrapertools.find_single_match(data, '<div class="movieplay">.*?data-lazy-src="(.*?)"')

    if not _id: return itemlist

    headers = {'Referer': host}

    data = do_downloadpage(_id, headers = headers)

    matches = scrapertools.find_multiple_matches(data, '<li onclick="go_to_player(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        url = scrapertools.find_single_match(match, "'(.*?)'")
        if not url: continue

        lang = scrapertools.find_single_match(match, '<p>(.*?)</p>').strip()

        if 'latino' in lang.lower(): lang = 'Lat'
        elif 'espanol' in lang.lower() or 'español' in lang.lower(): lang = 'Esp'
        elif 'subtitulado' in lang.lower() or 'vose' in lang.lower(): lang = 'Vose'
        else: '?'

        servidor = scrapertools.find_single_match(match, '<span>(.*?)</span>').lower()

        if servidor == 'pouvideo': continue
        elif servidor == 'stemplay': continue

        if servidor == 'dood': servidor = 'doodstream'

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if '?h=' in item.url:
        h =  scrapertools.find_single_match(item.url, '.*?h=(.*?)$')
        post = {'h': h}

        resp = httptools.downloadpage('https://pelisflix.link/sc/r.php', post = post, follow_redirects=False, only_headers=True)
        url = resp.headers['location']

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

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


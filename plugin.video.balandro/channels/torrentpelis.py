# -*- coding: utf-8 -*-

import re, base64

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www1.torrentpelis.com/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://torrentpelis.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Tendencias', action = 'list_all', url = host + 'tendencias/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'genero/netflix/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, 'GENEROS</a>(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if 'Añadido recientemente' in data:
        bloque = scrapertools.find_single_match(data, 'Añadido recientemente(.*?)<div class="sidebar')
    else:
        bloque = scrapertools.find_single_match(data, 'Tendencias(.*?)<div class="sidebar')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="imdb">.*?<span>(.*?)</span>')
        if not year: year = '-'

        plot = scrapertools.find_single_match(match, '<div class="texto">(.*?)</div>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pagination">' in data:
           next_url = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "<a href='(.*?)'")

           if next_url:
               if '/page/' in next_url:
                   itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Dual-LAT': 'Lat (dual)', 'Español latino': 'Lat', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, "<tr id='link-.*?<a href='(.*?)'.*?<strong class='quality'>(.*?)</strong>.*?<td>(.*?)</td>.*?<td>(.*?)</td>")

    for url, qlty, lang, size in links:
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent',
                              language = IDIOMAS.get(lang, lang), quality = qlty, other = size))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    urlb64 = scrapertools.find_single_match(url, 'urlb64=(.*?)$')

    if urlb64:
        urlb64 = base64.b64decode(urlb64).decode('utf-8')

        if '/enlaces/' in urlb64:
            resp = httptools.downloadpage(urlb64, follow_redirects=False, only_headers=True)
            if 'location' in resp.headers: url = resp.headers['location']
        else:
            data = do_downloadpage(urlb64)
            url = scrapertools.find_single_match(data, '<a id="link".*?href="(.*?)"')

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if url_base64.startswith('magnet:'):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

        elif url_base64.endswith(".torrent"):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, r'Has realizado una búsqueda(.*?)</table>')

    matches = scrapertools.find_multiple_matches(bloque, r"href='(.*?)'.*?>(.*?)</a>.*?'>(.*?)<.*?<td.*?>(.*?)<")

    for url, title, qlty, type in matches:
        qlty = qlty.replace('(', '').replace(')', '').strip()

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = qlty, fmt_sufijo = sufijo,
                                    contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))

    if itemlist:
         itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action='list_search', text_color='coral' ))

    tmdb.set_infoLabels(itemlist)

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

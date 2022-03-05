# -*- coding: utf-8 -*-

import re, base64

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://elifilms.net/'


def do_downloadpage(url, post=None, headers=None):
    raise_weberror = False if '/year/' in url else True

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En 4K UHD', action = 'list_all', url = host + '4k-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1993, -1):
        itemlist.append(item.clone( title=str(x), url= host + '/year/' + str(x) + '/', action='list_all', any = str(x) ))

    return itemlist

def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="short_header">(.*?)</div>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = '-'
        if item.any: year = item.any

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="(.*?)"')
        if next_url:
            if '/page/' in next_url:
               itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<ul class="server-list">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'data-id="(.*?)">(.*?)</a>')

    ses = 0

    for dvid, srv in matches:
        ses += 1

        srv = srv.replace('.com', '').replace('.co', '').replace('.live', '').replace('.nz', '').replace('.to', '').replace('v2.', '').lower().strip()

        if 'trailer' in srv: continue

        elif 'hqq' in srv or 'waaw' in srv or 'netu' in srv: continue
        elif 'embed.mystream' in srv: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', dvid = dvid,
                              language = 'Lat', other = srv.capitalize() ))

    # Descarga y Torrents
    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')

    matches = scrapertools.find_multiple_matches(bloque, 'data-href="(.*?)".*?<img src=.*?/dw/(.*?).png".*?<td>(.*?)</td>.*?<span>(.*?)</span>')

    for dvid, srv, lng, qlty in matches:
        ses += 1

        srv = srv.lower()

        lng = lng.replace('Latino', 'Lat').strip()

        if not lng: lng = 'Lat'

        if '1fichier' in srv: continue
        elif 'mediafire' in srv: continue
        elif 'google drive' in srv: continue
        elif 'turbobit' in srv: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', dvid = dvid,
                              quality = qlty, language = lng, other = srv.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = base64.b64decode(item.dvid).decode("utf-8")

    if item.other.lower() == 'torrent':
        itemlist.append(item.clone( url = url, server = 'torrent' ))

        return itemlist

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


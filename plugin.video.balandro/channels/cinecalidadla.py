# -*- coding: utf-8 -*-

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ww3.cinecalidad.do/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://cinecalidad.la/', 'https://cinecalidad.fo/', 'https://ww22.cinecalidad.fo/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    raise_weberror = True
    if '/fecha/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más destacadas', action = 'destacadas', url = host, search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 4K', action = 'list_all', url = host + 'calidad/4k-ultra-hd-hdr/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action='generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action='anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="custom-menu-class">(.*?)</div></div>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        if '#' in url: continue

        if title == '4K Ultra': continue
        elif title == 'Películas por año': continue

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1999, -1):
        url = host + 'fecha/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="home_post_cont post_box">(.*?)</a></div>')

    for match in matches:
        title = scrapertools.find_single_match(match, '<h2>.*?">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        if '-1-ano' in url: continue

        if not url or not title: continue

        plot = scrapertools.find_single_match(match, '<p>.*?">(.*?)</p>').strip()
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        m = re.match(r"^(.*?)\((\d+)\)$", title)
        if m:
            title = m.group(1).strip()
            year = m.group(2)
        else:
            year = '-'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<span class="pages">.*?class="current">.*?href="(.*?)"')
        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def destacadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Destacadas<(.*?)>Herramientas')

    matches = scrapertools.find_multiple_matches(bloque, '<a(.*?)</li>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="(.*?)"')
        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        m = re.match(r"^(.*?)\((\d+)\)$", title)
        if m:
            title = m.group(1).strip()
            year = m.group(2)
        else:
            year = '-'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'subtitulado': 'Vose'}

    lang = 'Lat'

    data = do_downloadpage(item.url)

    ses = 0

    if '>VER ONLINE<' in data:
        bloque = scrapertools.find_single_match(data, '>VER ONLINE<(.*?)>DESCARGAR<')

        matches = scrapertools.find_multiple_matches(bloque, 'class="link onlinelink play".*?data-src="(.*?)".*?data-domain="(.*?)"')

        for data_url, servidor in matches:
            ses += 1

            if 'netu' in servidor or 'waaw' in servidor or 'hqq' in servidor: continue
            elif 'tubesb' in servidor: continue
            elif 'youtube' in servidor: continue

            if servidor == 'ok': servidor = 'okru'

            qlty = '1080'

            itemlist.append(Item (channel = item.channel, action = 'play', server = servidor, title = '', url = item.url, data_url = data_url,
                                  quality = qlty, language = lang ))

    if '>DESCARGAR<' in data:
        bloque = scrapertools.find_single_match(data, '>DESCARGAR<(.*?)<div id="player">')

        matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?service="(.*?)"')

        for url, servidor in matches:
            ses += 1

            if url == '#':
                ses = ses - 1
                continue
            elif not servidor:
                ses = ses - 1
                continue
            elif '<div class="episodiotitle">' in servidor:
                ses = ses - 1
                continue

            if '<span' in servidor: servidor = scrapertools.find_single_match(servidor, '(.*?)<span')

            servidor = servidor.lower().strip()

            qlty = '1080'

            if '4k' in servidor or '4K' in servidor:
               qlty = '4K'
               servidor = servidor.replace('4k', '').replace('4K', '').strip()

            if 'subtítulo' in servidor: continue
            elif 'forzado' in servidor: continue

            elif servidor == '1fichier': continue
            elif servidor == 'turbobit': continue
            elif servidor == 'mediafire': continue

            elif servidor == 'utorrent': servidor = 'torrent'
            elif 'torrent' in servidor: servidor = 'torrent'

            elif servidor == 'google': servidor = 'gvideo'

            itemlist.append(Item (channel = item.channel, action = 'play', server = servidor, title = '', url = url, quality = qlty, language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    servidor = item.server

    if item.data_url:
        url_play = base64.b64decode(item.data_url).decode("utf-8")

        url = item.url + '?playnow=' + url_play

        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

        if not url: return itemllist

        if url.startswith('//'): url = 'https:' + url

    if '/protect/' in item.url:
            data = do_downloadpage(item.url)

            url = scrapertools.find_single_match(data, 'value="(.*?)"')

            if servidor == 'mega':
                if url.startswith('#'): url = 'https://mega.nz/' + url
                elif not url.startswith('http'): url = 'https://mega.nz/file/' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

    if url:
        if url.endswith('.torrent'):
            itemlist.append(item.clone( url = url, server = 'torrent' ))
            return itemlist

        elif 'magnet:?' in url:
            itemlist.append(item.clone( url = url, server = 'torrent' ))
            return itemlist

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(url = url, servidor = servidor))

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

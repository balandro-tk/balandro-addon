# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True


import re

from platformcode import logger, config
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://pasateatorrent.org/'

# ~  03/2022 algunas series No hay enlaces
# ~  04/2022 algunas pelis salta Recaptcha


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://pasateatorrent.net/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host}

    if '/categoria/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = {
        'accion': 'Acción',
        'animacion': 'Animación',
        'aventura': 'Aventura',
        'biografia': 'Biografía',
        'ciencia-ficcion': 'Ciencia ficción',
        'comedia': 'Comedia',
        'crimen': 'Crimen',
        'deporte': 'Deporte',
        'documental': 'Documental',
        'drama': 'Drama',
        'familia': 'Familia',
        'fantasia': 'Fantasía',
        'guerra': 'Guerra',
        'historia': 'Historia',
        'misterio': 'Misterio',
        'musica': 'Música',
        'romance': 'Romance',
        'suspense': 'Suspense',
        'terror': 'Terror',
        'western': 'Western'
        }

    for opc in sorted(opciones):
        itemlist.append(item.clone( title=opciones[opc], url=host + 'categoria/' + opc + '/', action='list_all' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1949, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'categoria/' + str(x) + '/', action = 'list_all' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='En 4K', url=host + 'categoria/4k-2/', action='list_all' ))
    itemlist.append(item.clone( title='En BluRay', url=host + 'categoria/BluRay-1080p/', action='list_all' ))
    itemlist.append(item.clone( title='En Dvd Rip', url=host + 'categoria/dvdrip/', action='list_all' ))
    itemlist.append(item.clone( title='En HD Rip', url=host + 'categoria/HDRip-2/', action='list_all' ))
    itemlist.append(item.clone( title='En Micro HD', url=host + 'categoria/MicroHD-1080p/', action='list_all' ))
    itemlist.append(item.clone( title='En 3D', url=host + 'categoria/3D/', action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="imagen-post">(.*?)<div class="bloque-date">')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, '<div class="bloque-inferior">(.*?)</div>').strip()

        if not url or not title: continue

        tipo = 'tvshow' if '/series/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        if not '/?s=' in item.url:
            year = scrapertools.find_single_match(match, '<div class="releaseDate".*?title=".*? .*? (.*?)</span>').strip()
            if not year: year = scrapertools.find_single_match(match, '<div class="releaseDate".*?title=".*? .*? (.*?)">').strip()
        else: year = scrapertools.find_single_match(match, '<div class="genres">(.*?), </div>').strip()

        if not year: year = '-'

        lang = scrapertools.find_single_match(match, '<div class="language".*?title="(.*?)">')
        if lang == 'Spanish': lang = 'Esp'

        qlty = scrapertools.find_single_match(match, '<div class="quality yellow".*?">(.*?)</div>')
        if not qlty: qlty = scrapertools.find_single_match(match, '<div class="hdAudio"></div><div class="(.*?)">')

        if '/series/' in url:
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = lang, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))
        else:
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, languages = lang, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<nav class="navigation pagination".*?class="page-numbers current">.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lang = 'Esp'

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<tbody>.*?</td>.*?</td>.*?<td>(.*?)</td>.*?href="(.*?)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for peso, url in matches:
        if not url.startswith('http'): url = host[:-1] + url

        other = peso.strip()

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = lang, other = other ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if PY3:
        from core import requeststools
        data = requeststools.read(item.url, '')
    else:
        data = do_downloadpage(item.url)

    if data:
        if '<meta name="captcha-bypass" id="captcha-bypass"' in str(data):
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
            return 'Archivo [COLOR red]Inexistente[/COLOR]'

        import os

        file_local = os.path.join(config.get_data_path(), "temp.torrent")
        with open(file_local, 'wb') as f: f.write(data); f.close()

        itemlist.append(item.clone( url = file_local, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.search_type == 'tvshow':
            item.url = host + '/series/?s=' + texto.replace(" ", "+")
        else:
            item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

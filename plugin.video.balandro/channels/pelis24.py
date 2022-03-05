# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://pelis24.in/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    logger.info()
    itemlist = []

    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Recomendadas (al azar)', action = 'list_all', url = host + 'peliculas/', group = 'azar', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('animacion', 'Animación'),
       ('aventura', 'Aventura'),
       ('belica', 'Bélica'),
       ('ciencia-ficcion', 'Ciencia ficción'),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('historia', 'Historia'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('Película de TV', 'pelicula-de-tv'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('suspense', 'Suspense'),
       ('terror', 'Terror'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'category/' + opc + '/', action = 'list_all' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1922, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title=str(x), url= url, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '</h1>(.*?)>Recomendamos<')

    if item.group == 'azar':
         bloque = scrapertools.find_single_match(data, '>Recomendamos<(.*?)>Series Recomendadas<')

    matches = re.compile('(?s)<article class="post dfx fcl movies">(.*?)</article>').findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, 'href="([^"]+)"')

        title = scrapertools.find_single_match(article, '<h2[^>]+>([^<]+)')
        thumb = scrapertools.find_single_match(article, '<img.*?src="([^"]+)"\Wclass')
        qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)')

        langs = []
        if 'Spain.png' in article: langs.append('Esp')
        if 'Mexico.png' in article: langs.append('Lat')
        if '/United-States-Minor-Outlying.png' in article: langs.append('Vose')

        itemlist.append(item.clone( action='findvideos', url=url, title = title, thumbnail = thumb, qualities=qlty, languages=', '.join(langs),
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if not item.group == 'azar':
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)">SIGUIENTE')
        if next_page:
            itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Sub Español': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'id="options-(.*?)".*?<iframe .*?src="(.*?)"')

    i = 0

    for opt, url in matches:
        i += 1
        srv, lang = scrapertools.find_single_match(data, 'href="#options-' + str(opt)+ '">.*?<span class="server">(.*?)-(.*?)</span>')

        srv = srv.lower().strip()

        lang = lang.strip()
        if '</td>' in lang: lang = scrapertools.find_single_match(lang, '(.*?)</td>')

        idioma = IDIOMAS.get(lang, lang)

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        other = ''
        if servidor:
           if srv == 'streamz':
               servidor = srv
           elif srv == 'streamcrypt':
               other = srv + '-' + str(i)
           else:
               other = srv.lower() + '-' + str(i)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, other = other, language = idioma ))

    # ~ downloads recatpcha

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')
    item.url = item.url.replace('amp;#038;', '&').replace('#038;', '&').replace('amp;', '&')

    url = item.url

    if item.url.startswith(host):
        data = do_downloadpage(item.url)
        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

    if url.startswith('https://streamcrypt.net/'):
        url = httptools.downloadpage(url, follow_redirects=False).headers.get('location', '')
        if url:
            url = url.replace('?id=', '?p=2&id=')
            url = httptools.downloadpage(url, follow_redirects=False).headers.get('location', '')
        else:
            data = do_downloadpage(url)
            url = scrapertools.find_single_match(data, "window.open.*?'(.*?)'")

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))

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

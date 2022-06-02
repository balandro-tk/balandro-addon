# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://mejortorrent.wtf'


perpage = 30


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://mejortorrent.app']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post).data
    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
    itemlist.append(item.clone( title = 'Documentales', action = 'mainlist_documentales', text_color = 'cyan' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_list', url = host + '/torrents/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_list', url = host + '/busqueda/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/peliculas-hd/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 4K', action = 'list_all', url = host + '/peliculas-4k/', search_type = 'movie' ))

    itemlist.append(item.clone( action = 'calidades', title = 'Por calidad', search_type = 'movie' ))
    itemlist.append(item.clone( action = 'generos', title = 'Por género', search_type = 'movie' ))
    itemlist.append(item.clone( action = 'anios', title = 'Por año', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_list', url = host + '/torrents/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_list', url = host + '/busqueda/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/series-hd/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def mainlist_documentales(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'tvshow', text_color = 'cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/documentales/', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_list', url = host + '/torrents/', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_list', url = host + '/busqueda/', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'documentary' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 4K', action = 'list_list', url = host + '/peliculas/quality/4k/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En BDremux 1080', action = 'list_list', url = host + '/peliculas/quality/bdremux-1080p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En BluRay 720', action = 'list_list', url = host + '/peliculas/quality/bluray-7200p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En BluRay 1080', action = 'list_list', url = host + '/peliculas/quality/bluray-1080p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En DVDrip', action = 'list_list', url = host + '/peliculas/quality/dvdrip/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En HDrip', action = 'list_list', url = host + '/peliculas/quality/hdrip/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En MIcroHD 720', action = 'list_list', url = host + '/peliculas/quality/microhd-720p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En MicroHD 1080', action = 'list_list', url = host + '/peliculas/quality/microhd-1080p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En Screener', action = 'list_list', url = host + '/peliculas/quality/screener/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En VHSrip', action = 'list_list', url = host + '/peliculas/quality/vhsrip/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En VHSscreener', action = 'list_list', url = host + '/peliculas/quality/vhsscreener/', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
        ('Acción', 'accion'),
        ('Animación', 'animacion'),
        ('Aventuras', 'aventuras'),
        ('Bélica', 'belica'),
        ('Biográfica', 'biografica'),
        ('Ciencia Ficción', 'ciencia-ficcion'),
        ('Cine Negro', 'cine-negro'),
        ('Comedia', 'comedia'),
        ('Crimen', 'crimen'),
        ('Documental', 'documental'),
        ('Drama', 'drama'),
        ('Fantasía', 'fantasia'),
        ('Intriga', 'intriga'),
        ('Músical', 'musical'),
        ('Romántica', 'romantica'),
        ('Suspense', 'suspense'),
        ('Terror', 'terror'),
        ('Thriller', 'thriller'),
        ('Western', 'western')
        ]

    for opc in opciones:
        title = opc[0]
        url = host + '/peliculas/genre/' + opc[1]

        itemlist.append(item.clone( title = title, url = url, action = 'list_list' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1919, -1):
        url = host + '/peliculas/year/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_list' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': url_alfa = host + '/peliculas/letter/'
    elif item.search_type == 'tvshow': url_alfa = host + '/series/letter/'
    else: url_alfa = host + '/documentales/letter/'

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
         url = url_alfa + letra.lower() + '/'

         itemlist.append(item.clone( title = letra, action = 'list_list', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class=""><span class="bg-mejortorrent-card-(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, r'href="([^"]+)">([^<]+)</a>.*?<b>(.*?)<')

    num_matches = len(matches)

    for url, title, qlty in matches[item.page * perpage:]:
        title = title.replace('-', ' ')

        if '4K' in title: title = title.replace('[4K]', '').replace('4K', '').strip()
        elif '3D' in title: title = title.replace('[3D]', '').replace('3D', '').strip()

        qlty = qlty.replace('(', '').replace(')', '').strip()

        thumb = scrapertools.find_single_match(data, url + '.*?<img src="(.*?)"')

        url = host + url

        if item.search_type == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
        else:
            titulo = title.replace('Temporada', '').strip()

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='tvshow', contentSerieName=titulo, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<span aria-current="page">.*?<a href="(.*?)"')
            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', page = 0, action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def list_list(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '</aside>(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="flex flex-row mb-2">(.*?)</div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<a href=.*?">.*?>(.*?)<strong>')

        if not url or not title: continue

        if '4K' in title: title = title.replace('[4K]', '').replace('4K', '').strip()
        elif '3D' in title: title = title.replace('[3D]', '').replace('3D', '').strip()

        qlty = scrapertools.find_single_match(match, '<strong>(.*?)</strong>')

        qlty = qlty.replace ('(', '').replace (')', '').strip()

        year = '-'
        if '/year/' in item.url: year = scrapertools.find_single_match(item.url, '/year/(.*?)/')
        if not year: year = '-'

        type = scrapertools.find_single_match(match, 'capitalize">(.*?)</span>')

        if not type == 'peliculas' and not type == 'series' and not type == 'documentales': continue

        if item.search_type != 'all':
            if item.search_type == 'movie':
                if type == 'series': continue
                elif type == 'documentales': continue
            else:
                if type == 'peliculas': continue

        sufijo = ''

        if item.search_type == 'all':
            if type == 'peliculas': sufijo = 'movie'
            elif type == 'series': sufijo = 'tvshow'
            else: sufijo = '[COLOR yellow]Documental[/COLOR]'

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = qlty, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))
        else:
            itemlist.append(item.clone( action='episodios', url = url, title = title, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_list', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            next_page = scrapertools.find_single_match(data, '<span aria-current="page">.*?<a href="(.*?)"')
            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone( title='Siguientes ...', page = 0, action='list_list', url=next_page, text_color='coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '>Episodios:(.*?)</tbody>')

    season = scrapertools.find_single_match(bloque, '-Temporada-(.*?)-')
    if not season: season = 0

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)"')

    i = 0

    for url in matches:
        i += 1

        title = str(season) + 'x' + str(i)

        itemlist.append(item.clone( action='findvideos', url = url, title = title,
                                    contentType='episode', contentSeason = season, contentEpisodeNumber = i ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lang = 'Esp'

    url = ''

    if item.search_type == 'movie':
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '>Torrent:<.*?<a href="(.*?)"')

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent', language = lang ))

        return itemlist

    itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server = 'torrent', language = lang ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/busqueda?q=' + texto.replace(" ", "+")
        return list_list(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb


host = 'https://peliculaspremium.com/'

perpage = 24


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    headers = {'Referer': host}

    if '/release/' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas?get=movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if item.search_type == 'tvshow':
            if title == 'Documental': continue
            elif title == 'Película de TV': continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url ))

    if item.search_type == 'movie':
        itemlist.append(item.clone( action = 'list_all', title = 'Accion', url = host + 'genero/accion.html' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        url = host + 'release/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    productoras = [
        ('abc', 'ABC'),
        ('amazon', 'Amazon'),
        ('amc', 'AMC'),
        ('antena-3', 'Antena 3'),
        ('apple-tv', 'Apple Tv+'),
        ('cbs', 'CBS'),
        ('dc-universe', 'Dc Universe'),
        ('disney', 'Disney +'),
        ('fox', 'FOX'),
        ('fx', 'FX'),
        ('hbo', 'HBO'),
        ('hbo-max', 'HBO Max'),
        ('history', 'History'),
        ('lifetime', 'Lifetime'),
        ('nbc', 'NBC'),
        ('netflix', 'Netflix'),
        ('showtime', 'Showtime'),
        ('the-cw', 'The Cw'),
        ('the-wb', 'the Wb'),
        ('univision', 'Univision'),
        ('usa-network', 'Usa Network')
        ]

    for opc, tit in productoras:
        url = host + 'network/' + opc + '/'

        itemlist.append(item.clone( title = tit, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    if '>Tendencias<' in data:
        bloque = scrapertools.find_single_match(data, '<h1>(.*?)>Géneros<')
    else:
        bloque = scrapertools.find_single_match(data, '<h2>Añadido recientemente(.*?)>Géneros<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')

        tipo = 'movie' if 'class="item movies">' in match else 'tvshow'

        if item.search_type == 'movie':
            if tipo == 'tvshow':
                num_matches = (num_matches -1)
                continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

        if item.search_type == 'tvshow':
            if tipo == 'movie':
                num_matches = (num_matches -1)
                continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if '<div class="pagination">' in data:
                next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + "href='(.*?)'")

                if next_page:
                    if '/page/' in next_page:
                        itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, page = 0, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<span class='title'>Temporada(.*?)<i>")

    for nro_season in matches:
        nro_season = nro_season.strip()
        title = 'Temporada ' + nro_season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = nro_season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = nro_season ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    season = scrapertools.find_single_match(data, "<span class='se-t.*?>" + str(item.contentSeason) + '</span>(.*?)</div></div>')

    matches = scrapertools.find_multiple_matches(season, "<img src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>")

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PeliculasPremium', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for thumb, temp_epis, url, title in matches[item.page * item.perpage:]:
        nro_epi = scrapertools.find_single_match(temp_epis, '.*?-(.*?)$').strip()

        titulo = temp_epis.replace(' ', '').replace('-', 'x') + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = nro_epi ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'LA': 'Lat', 'ES': 'Esp', 'SB': 'Vose', 'EN': 'Vo'}

    data = do_downloadpage(item.url)

    jurl = scrapertools.find_single_match(data, '<div class="iframex">.*?src="(.*?)"')

    if not jurl: return itemlist

    jurl = jurl.replace('.html', '.json')

    data = do_downloadpage(jurl)

    jdata = jsontools.load(data)

    ses = 0

    for elem in jdata:
        ses += 1

        lang = elem['lang']
        links = elem['links']

        for vdata in links:
            url = vdata['enlace']

            if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
            elif '.mystream.' in url: continue
            elif 'openload' in url: continue
            elif 'powvideo' in url: continue
            elif 'streamplay' in url: continue
            elif 'rapidvideo' in url: continue
            elif 'streamango' in url: continue
            elif 'verystream' in url: continue
            elif 'vidtodo' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article>(.*?)</article>')

    for match in matches:
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        url = scrapertools.find_single_match(match, ' href="([^"]+)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')

        year =  scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        plot =  scrapertools.find_single_match(match, '<p>(.*?)<p/>')

        tipo = 'movie' if '<span class="movies">Película</span>' in match else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

        if tipo == 'tvshow':
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year, 'plot': plot} ))

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


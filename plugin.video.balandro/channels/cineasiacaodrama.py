# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://caodrama.com/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Buscar dorama ...', action = 'search', search_type = 'tvshow', text_color = 'firebrick' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'archivos/peliculas/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Estrenos', action = 'list_all', url = host + 'archivos/estrenos/', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'En latino', action = 'list_all', url = host + 'lenguaje/latino/' ))
    itemlist.append(item.clone ( title = 'Subtituladas', action = 'list_all', url = host + 'lenguaje/subtitulado/' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Series por Año<(.*?)</div>')
    matches = scrapertools.find_multiple_matches(bloque, '<option value="(.*?)"')

    for anio in matches:
        url = host + 'fecha-estreno/' + anio + '/'

        itemlist.append(item.clone( title = anio, url = url, action = 'list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<h3><a href="([^"]+)">([^<]+)<.*?src="([^"]+)".*?<a rel="tag">(.*?)<.*?<a rel="tag">(.*?)<'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, title, thumb, year, qlty in matches:
        title = title.replace('audio latino', '').strip()

        title = re.sub(r' \((\d{4})\)$', '', title)

        if not year: year = '-'

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, qualities=qlty, 
                                    contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<span class='current'>" + '.*?href="(.*?)"')
        if next_page:
            itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    # ~ No hay temporadas
    title = 'Temporada 1'

    platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
    item.page = 0
    item.contentType = 'season'
    item.contentSeason = 1
    itemlist = episodios(item)
    return itemlist


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    if item.page == 0: episode = 1
    else: episode = (item.page * item.perpage) + 1

    matches = re.compile('<p><a href="(.*?)"', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('CineAsiaCaodrama', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url in matches[item.page * item.perpage:]:
        episode += 1

        title = str(item.contentSeason) + 'x' + str(episode) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = item.url, title = title, link = url, orden = episode,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    bloque = scrapertools.find_single_match(data, '<ul class="tabs">(.*?)<div id="clear">')

    url = scrapertools.find_single_match(bloque, '<div id="tab.*?src="(.*?)"')

    if url:
        title = str(item.contentSeason) + 'x1 ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = item.url, title = title, link = url, orden = 1,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = 1 ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage,
                                        text_color='coral', orden = '10000' ))

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose', 'Subitulado': 'Vose'}

    data = do_downloadpage(item.url)

    lang = scrapertools.find_single_match(data, '<p>Idioma.*?href=.*?rel="tag">(.*?)</a>').capitalize()


    if item.link:
        url = item.link

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: url = ''
        elif '/gounlimited' in url: url = ''
        elif '/oogly.' in url: url = ''

        if url:
            idioma = IDIOMAS.get(lang, lang)

            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, language = idioma ))

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

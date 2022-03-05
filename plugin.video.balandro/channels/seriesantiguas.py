# -*- coding: utf-8 -*-

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.seriesantiguas.com/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    url = url.replace('www.seriesantiguas.net', 'www.seriesantiguas.com')

    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'search/label/ESTRENO' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'search/label/POPULARES' ))

    itemlist.append(item.clone( title = "Las de los 80's", action = 'list_all', url = host + 'search/label/80s' ))
    itemlist.append(item.clone( title = "Las de los 90's", action = 'list_all', url = host + 'search/label/90s' ))
    itemlist.append(item.clone( title = "Las de los 00's", action = 'list_all', url = host + 'search/label/00s' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<div class='post hentry'>(.*?)</h2>")

    num_matches = len(matches)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        if not url: url = scrapertools.find_single_match(match, "<a href='(.*?)'")

        title = scrapertools.find_single_match(match, "<img alt='(.*?)'")
        if not title: title = scrapertools.find_single_match(match, "<img alt='(.*?)'")

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(match, "src='(.*?)'")

        year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if num_matches >= 6:
        if "<span id='blog-pager-older-link'>" in data:
            block = scrapertools.find_single_match(data, "<span id='blog-pager-older-link'>(.*?)</a>")

            next_page = scrapertools.find_single_match(block, "<a class='blog-pager-older-link'" + '.*?href="(.*?)"')
            if not next_page: next_page = scrapertools.find_single_match(block, "<a class='blog-pager-older-link'" + ".*?href='(.*?)'")

            if next_page:
                next_page = next_page.replace('&max-results=6', '&max-results=20')

                itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    url_serie = scrapertools.find_single_match(data, "<div class='post-body entry-content'>.*?title=.*?" + '<a href="(.*?)"')

    data = do_downloadpage(url_serie)

    bloque = scrapertools.find_single_match(data, '>Temporadas<(.*?)</ul></li>')
    matches = scrapertools.find_multiple_matches(bloque, "<a href='(.*?)'>Temp (.*?)</a>")

    # cuantas temporadas
    tot_temp = 0

    for url, numtempo in matches:
        tot_temp += 1
        if tot_temp > 1: break

    for url, numtempo in matches:
        title = 'Temporada ' + numtempo

        url = url + '?max-results=100'

        if tot_temp == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = url
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist


        itemlist.append(item.clone( action = 'episodios', title = title, url = url, contentType = 'season', contentSeason = numtempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<div class='post hentry'>(.*?)</h2>")

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('SeriesAntiguas', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for epis in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(epis, '<a href="([^"]+)"')

        episode = scrapertools.find_single_match(epis, "<img alt=.*?Temporada.*?x (.*?)'")
        episode = episode.replace(')', '')

        if not url or not episode: continue

        title = scrapertools.find_single_match(epis, "<img alt='(.*?)'")
        title = title.split('(')[0]
        title = title.strip()

        title = str(item.contentSeason) + 'x' + episode + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<div class='post-body entry-content'>(.*?)<div class='post-footer'>")

    matches = scrapertools.find_multiple_matches(bloque, '<iframe.*?src="(.*?)"')

    for url in matches:
        if url.startswith('//'): url = 'https:' + url
        url = url.replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Lat' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '/search/?q=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

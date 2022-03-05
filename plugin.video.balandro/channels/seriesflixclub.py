# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

host = 'https://seriesflix.club/'


def do_downloadpage(url, post=None, headers=None):
    headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tvshows/' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'plataformas', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    productoras = [
        ['abc', 'ABC'],
        ['adult-swim', 'Adult Swim'],
        ['amazon', 'Amazon'],
        ['amc', 'AMC'],
        ['apple-tv', 'Apple TV+'],
        ['bbc-one', 'BBC One'],
        ['bbc-two', 'BBC Two'],
        ['bs11', 'BS11'],
        ['cbc', 'CBC'],
        ['cbs', 'CBS'],
        ['comedy-central', 'Comedy Central'],
        ['dc-universe', 'DC Universe'],
        ['disney', 'Disney+'],
        ['disney-xd', 'Disney XD'],
        ['espn', 'ESPN'],
        ['fox', 'FOX'],
        ['fx', 'FX'],
        ['hbc', 'HBC'],
        ['hbo', 'HBO'],
        ['hbo-espana', 'HBO España'],
        ['hbo-max', 'HBO Max'],
        ['hulu', 'Hulu'],
        ['kbs-kyoto', 'KBS Kyoto'],
        ['la-1', 'La 1'],
        ['mbs', 'MBS'],
        ['nbc', 'NBC'],
        ['netflix', 'Netflix'],
        ['nickelodeon', 'Nickelodeon'],
        ['paramount', 'Paramount+'],
        ['showtime', 'Showtime'],
        ['sky-atlantic', 'Sky Atlantic'],
        ['stan', 'Stan'],
        ['starz', 'Starz'],
        ['syfy', 'Syfy'],
        ['tbs', 'TBS'],
        ['telemundo', 'Telemundo'],
        ['the-cw', 'The CW'],
        ['tnt', 'TNT'],
        ['tokyo-mx', 'Tokyo MX'],
        ['tv-tokyo', 'TV Tokyo'],
        ['usa-network', 'USA Network'],
        ['youtube-premium', 'YouTube Premium'],
        ['zdf', 'ZDF']
        ]

    url = host + 'network/'

    for x in productoras:
        itemlist.append(item.clone( title = x[1], url = url + str(x[0]) + '/', action = 'list_all' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>GÉNEROS<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, tit in matches:
        itemlist.append(item.clone( title = tit, url = url, action = 'list_all' ))

    itemlist.append(item.clone( action='list_all', title='Western', url=host + 'genre/western/' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '<div class="pagination"' in data:
        bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)<div class="pagination"')
    else:
        bloque = scrapertools.find_single_match(data, '>Añadido recientemente<(.*?)<div class="sidebar')
	
    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' alt="(.*?)"').strip()
        if not url or not title: continue

        title = title.replace('Ver ', '').replace('Completas', '').replace('HD', '').replace('Online Gratis', '').strip()

        thumb = scrapertools.find_single_match(article, '<img src="(.*?)"')
        year = scrapertools.find_single_match(article, '<span class="imdb">.*?<span>(.*?)</span>')

        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    if '<nav class="wp-pagenavi">' in data:
        next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><i class="fa-arrow-right"></i></a>')
        if next_page:
           itemlist.append(item.clone (url = next_page, page=0, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<span class='se-t.*?'>(.*?)</span>")

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo ))

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

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "(.*?)</div></div></div></div></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<li class='mark-(.*?)</li>")

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('SeriesFlixClub', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for data_epi in matches[item.page * item.perpage:]:
        url = scrapertools.find_single_match(data_epi, "<a href='(.*?)'")

        temp_epis = scrapertools.find_single_match(data_epi, "<div class='numerando'>(.*?)</div>")

        if not url or not temp_epis: continue

        episode = scrapertools.find_single_match(temp_epis, ".*?-(.*?)$").strip()
        if not episode: continue

        title = str(item.contentSeason) + 'x' + episode + ' ' + item.contentSerieName

        thumb = scrapertools.find_single_match(data_epi, "<img src='(.*?)'")

        fecha = scrapertools.find_single_match(data_epi, "<span class='date'>(.*?)</span>")
        if fecha: title = title + ' [COLOR gray](' + fecha + ')[/COLOR]'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'embed': return 'mystream'
    if servidor == 'flixplayer': return 'directo'
    return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    lang = '?'
    if '>LATINO' in data: lang = 'latino'
    elif '>CASTELLANO' in data: lang = 'castellano'
    elif '>SUBTITULADA' in data: lang = 'subtitulado'

    patron = "<li id='player-option-.*?class='dooplay_player_option'.*?data-type='(.*?)'.*?data-post='(.*?)'.*?data-nume='(.*?)'"

    matches = scrapertools.find_multiple_matches(data, patron)

    ses = 0

    for options in matches:
        ses += 1

        data = do_downloadpage(host + 'wp-json/dooplayer/v2/' + options[1] + '/' + options[0] + '/' + options[2])

        lang = IDIOMAS.get(lang.lower(), lang)

        data = data.replace('\\/', '/')
        data = data.replace('=\\', '=').replace('\\"', '/"')

        url = scrapertools.find_single_match(data, 'src="(.*?)"')
        if '.html' in url:
            url = scrapertools.find_single_match(url, '(.*?).html')

        if not url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

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

    matches = re.compile('<div class="result-item">(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        title = title.replace('Ver', '').replace('Online Gratis Completas HD', '').strip()

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        if not year:
            year = '-'

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                    contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

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

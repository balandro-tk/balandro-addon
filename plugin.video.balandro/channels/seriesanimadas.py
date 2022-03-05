# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = "https://seriesanimadas.org/"


def mainlist(item):
    return mainlist_anime(item)

def mainlist_series(item):
    return mainlist_anime(item)


def mainlist_anime(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'series/estrenos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + 'series/populares', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + '/tvgenero/'

    data = httptools.downloadpage(host + 'series').data

    matches = scrapertools.find_multiple_matches(data, '/tvgenero/(.*?)".*?>(.*?)</a>')

    for genre, title in matches:
        url = url_genre + genre

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, ' title="(.*?)"')

        if not url or not title: continue

        title = title.replace('Online', '').strip()

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<ul class="pagination">.*?Previous.*?href="(.*?)"')
        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="card-episodie shadow-sm">.*?<a href="(.*?)".*?title="(.*?)".*?src="(.*?)".*?</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, thumb in matches:
        c_title, epis, lang = scrapertools.find_single_match(title, r'^(.*?)\s*(?:Episodio)?\s*(\d+)\s*(.*)')

        if c_title == 'ver': c_title = title

        c_title = c_title.replace('ver ', '').strip()

        titulo = '1x%s %s' % (epis, c_title)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
									contentSerieName = title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epis ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = re.compile('<div id="season-(.*?)"', re.DOTALL).findall(data)

    if not matches:
        itemlist = episodios(item)
        return itemlist

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    if not item.contentSeason:
        item.contentSeason = 1
        patron = '<a class="episodie-list" href="([^"]+)" .*?</i> Episodio (\d+).*?</span>'
    else:
        patron = 'class="episodie-list" href="([^"]+)" title=".*?Temporada %s .*?pisodio (\d+).*?">' % str(item.contentSeason)

    matches = re.compile(patron, re.DOTALL).findall(data)

    if not matches:
        patron = 'class="episodie-list" href="([^"]+)" title=".*?pisodio (\d+).*?">'
        matches = re.compile(patron, re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('SeriesAnimadas', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, epis in matches[item.page * item.perpage:]:
        titulo = '%sx%s - Episodio %s' % (item.contentSeason, epis, epis)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, 
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'audio latino': 'Lat', 'español': 'Esp', 'audio español': 'Esp', 'sub español': 'Vose', 'subtitulado': 'Vose'}

    data = httptools.downloadpage(item.url).data

    matches = re.compile('video\[(\d+)\] = .*?src="([^"]+)".*?;', re.DOTALL).findall(data)

    ses = 0

    for option, url in matches:
        ses += 1

        lang = scrapertools.find_single_match(data, '"#option%s".*?<span>(.*?)</span>' % str(option))
        lang = lang.strip().lower()

        if 'redirect' in url:
            url_data = httptools.downloadpage(url).data
            url = scrapertools.find_single_match(url_data,'var redir = "([^"]+)";')
            if not url:
                url = scrapertools.find_single_match(url_data,'window.location.href = "([^"]+)";')

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: url = ''
        elif '/badshare.io/' in url: url = ''

        if url:
            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor == 'directo': continue

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "search?s=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

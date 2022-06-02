# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://srnovelas.com/'


perpage = 20


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www.srnovelas.cc/'] 

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if not headers: headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'series/', group = 'onair' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    if item.group == 'onair': bloque = scrapertools.find_single_match(data, '>Series en Emisión<(.*?)>Mas Series<')
    else: bloque = scrapertools.find_single_match(data, '>Mas Series<(.*?)>Últimos Capítulos Agregados<')

    matches = scrapertools.find_multiple_matches(bloque, '<p class="pt-cv-title">(.*?)/div></div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, ' >(.*?)</a>')

        if not url or not title: continue

        ref_serie = url

        year = '-'

        try:
           name = title.split(" (")[0]
           year = title.split(" (")[1]
           if ')' in year: year = year.split(")")[0]
           elif '-' in year: year = year.split("-")[0]

           if year: title = name
        except:
            name = title

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, ref_serie = ref_serie,
                                    contentType = 'tvshow', contentSerieName = name, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    seasons = scrapertools.find_multiple_matches(data, '<span class="su-spoiler-icon">.*?Temporada(.*?)</div>')

    if not seasons:
        platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas[/COLOR]')
        item.contentType = 'season'
        item.contentSeason = 1
        itemlist = episodios(item)
        return itemlist

    for title in seasons:
        tempo = title.strip()

        title = 'Temporada ' + title.strip()

        if len(seasons) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo ))

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

    if '<span class="su-spoiler-icon">' in data:
        bloque = scrapertools.find_single_match(data, '<span class="su-spoiler-icon">.*?Temporada ' + str(item.contentSeason) + '(.*?)</div></div>')
    else:
        bloque = scrapertools.find_single_match(data, '<ul class="su-posts su-posts-list-loop ">(.*?)</ul>')

    episodes = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?>(.*?)</a>')

    if item.page == 0:
        sum_parts = len(episodes)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('SrNovelas', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, title, in episodes[item.page * item.perpage:]:
        epis = scrapertools.find_single_match(title, '.*?Capitulo (.*?) ').strip()
        if not epis: epis = scrapertools.find_single_match(title, '.*?Capitulo (.*?)$').strip()

        epis = epis.replace('|', '').strip()

        if not epis: epis = '1'

        titulo = str(item.contentSeason) + 'x' + epis + ' ' + item.contentSerieName

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(episodes) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    logger.info()
    itemlist = []

    IDIOMAS = {'mx': 'Lat', 'es': 'Esp'}

    data = do_downloadpage(item.url)

    # embeds
    matches = scrapertools.find_multiple_matches(data, 'data-title="Opción.*?src="(.*?)"')

    for url in matches:
        url = url.strip()
        ref = item.url

        #url = url.replace('&', '').strip()

        lang = 'Lat'

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, ref = ref, ref_serie = item.ref_serie, language = lang ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    CUSTOM_HEADERS = {}
    CUSTOM_HEADERS['Cookie'] = 'w3tc_referrer=' + item.ref_serie
    CUSTOM_HEADERS['Referer'] = item.ref

    httptools.save_cookie('w3tc_referrer', item.ref_serie, 'srnovelas.com')

    data = httptools.downloadpage(item.url, headers=CUSTOM_HEADERS).data

    olid = scrapertools.find_single_match(data, "var OLID = '(.*?)'")

    if olid:
       new_url = scrapertools.find_single_match(data, 'src="(.*?)"')

       if new_url:
           new_url = new_url.replace("'+OLID+'", '')
           new_url = new_url + olid #+  '&'

           resp = httptools.downloadpage(new_url, headers={'Referer': item.url}, follow_redirects=False, only_headers=True)

           httptools.save_cookie('w3tc_referrer', host, 'srnovelas.com')

           if 'location' in resp.headers: url = resp.headers['location']
           else:
              return 'Archivo [COLOR plum]inexistente[/COLOR]'

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    httptools.save_cookie('w3tc_referrer', host, 'srnovelas.com')

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')

        title = scrapertools.find_single_match(article, ' <span class="screen-reader-text">(.*?)</span>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        if '-capitulo-' in url:
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                        contentType='tvshow', contentSerieName = title, infoLabels={'year': '-', 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                        contentType='tvshow', contentSerieName = title, infoLabels={'year': '-', 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<a class="next page-numbers" href="(.*?)"')
        if next_page:
            itemlist.append(item.clone( title = "Siguientes ...", action = "list_search", url = next_page, text_color='coral' ))

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


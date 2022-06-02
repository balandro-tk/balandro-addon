# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pelisplus.ac/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://pelisplus.so/', 'https://www1.pelisplus.so/', 'https://www2.pelisplus.so/', 'https://pelisplus.sh/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    if '/peliculas-' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '?page=', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos?page=', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series?page=', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<h2>GÉNEROS(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)" title="(.*?)">.*?</a>')

    for url, tit in matches:
        url = host[:-1] + url + '?page='

        itemlist.append(item.clone( title = tit, url = url, action = 'list_all' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1930, -1):
        url = host + 'peliculas-' + str(x) + '?page='

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    data = do_downloadpage(item.url + str(item.page))

    data = data.replace('\n','')

    bloque = scrapertools.find_single_match(data, '<div class="main-peliculas movie-refresh">(.*?)<div class="butmore"')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h2 class="pull-left">(.*?)<div class="footer">')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="item-pelicula(.*?)</figure>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"').strip()

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url

        title = re.sub(r" \(.*?\)| \| .*", "", title)

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year text-center">(.*?)</span>')
        if year: title = title.replace('(' + year + ')', '').strip()
        else: year = '-'

        if '/serie/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb,
                                        contentType = 'season', contentSerieName = title, infoLabels={'year': '-'} ))
        else:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(itemlist) == 20:
            itemlist.append(item.clone (url = item.url, page = item.page + 1, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    temporadas = re.compile('div class="item-season-title">.*?</i>(.*?)</div>', re.DOTALL).findall(data)

    tot_tempo = len(temporadas)

    for tempo in temporadas:
        tempo = tempo.replace('Temporada', '').strip()

        if tot_tempo >= 10:
            if int(tempo) < 10: tempo = '0' + tempo

        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.title)


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    tab_epis = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, 'div class="item-season-title">.*?</i>Temporada ' + str(item.contentSeason) + ".*?</div>(.*?)</div>")

    matches = re.compile('<a href="(.*?)".*?</i>(.*?)</a>', re.DOTALL).findall(bloque)

    num_matches = len(matches)

    if item.page == 0:
        sum_parts = num_matches
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PelisPlus', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, title in matches:
        if url.startswith('/'): url = host[:-1] + url

        title = title.strip()
        episode = scrapertools.find_single_match(title, ".*?Capítulo(.*?)$")

        episode = episode.strip()

        ord_epis = str(episode)

        if len(str(ord_epis)) == 1: ord_epis = '0000' + ord_epis
        elif len(str(ord_epis)) == 2: ord_epis = '000' + ord_epis
        elif len(str(ord_epis)) == 3: ord_epis = '00' + ord_epis
        else:
            if num_matches > 50: ord_epis = '0' + ord_epis

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        if num_matches > 50:
            tab_epis.append([ord_epis, url, titulo, episode])
        else:
            itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode, orden = ord_epis ))

    if num_matches > 50:
        tab_epis = sorted(tab_epis, key=lambda x: x[0])

        for orden, url, tit, epi in tab_epis[item.page * item.perpage:]:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = tit,
                                    orden = orden, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epi ))

            if len(itemlist) >= item.perpage:
                break

        if num_matches > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", data_epi = item.data_epi, orden = '10000',
                                        page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

        return itemlist

    else:
        return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'castell': 'Esp', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    data = data.replace('\n','')

    matches = scrapertools.find_multiple_matches(data, '<ul id=".*?_(.*?)"(.*?)</ul>')

    ses = 0

    for match in matches:
        idioma = match[0]

        urls = scrapertools.find_multiple_matches(match[1], '<li role="presentation" data-video="(.*?)" ')

        for url in urls:
            ses += 1

            if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor == 'directo': link_other = normalize_other(url)
            else: link_other = ''

            lang = idioma

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url,
                                  language = IDIOMAS.get(lang, lang), other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def normalize_other(url):
    if 'pelisplus' in url: link_other = 'plus'
    elif 'damedamehoy' in url: link_other = 'dame'
    elif 'tomatomatela' in url: link_other = 'dame'
    else:
       if config.get_setting('developer_mode', default=False): link_other = url
       else: link_other = ''

    return link_other


def resuelve_dame_toma(dame_url):
    data = do_downloadpage(dame_url)

    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
    if not url:
        checkUrl = dame_url.replace('embed.html#', 'details.php?v=')
        data = do_downloadpage(checkUrl, headers={'Referer': dame_url})
        url = scrapertools.find_single_match(data, '"file":\s*"([^"]+)').replace('\\/', '/')

    return url


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.other == 'dame':
        url = resuelve_dame_toma(item.url)

        if url:
            itemlist.append(item.clone(url=url , server='directo'))
            return itemlist

    elif item.server == 'directo':
        data = do_downloadpage(url)

        data = data.replace('\n','')

        urls = scrapertools.find_multiple_matches(data, "sources:\[{file:.*?\'(.*?)\',label")

        for url in urls:
            if not 'error' in url:
                if '/pelisloadtop.com/' in url: continue

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                itemlist.append(item.clone( url = url, server = servidor ))
    else:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    headers = {'Referer': item.url, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36', 'x-requested-with': 'XMLHttpRequest'}
    cookies ={'gogoanime':'21igr6ets5bksao4au3gj95d31'}
    post = {'keyword': item.payload}

    import requests
    data = requests.get(url = item.url, headers=headers, cookies=cookies, params = post, verify=False)
    data = data.text.replace('\n','')

    bloque = scrapertools.find_single_match(data, '<div class="title-results">(.*?)<\/div><\/div>')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="item-pelicula pull-left">.*?<a href="(.*?)" title="(.*?)".*?src?="(.*?)".*?<span class="year text-center">(.*?)<\/span>')

    for url, title, thumbnail, year in matches:
        if url.startswith('/'): url = host + url
        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if '/tvshows/' in url:
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumbnail, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))

        else:
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            sufijo = '' if item.search_type != 'all' else 'movie'

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumbnail, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()

    try:
       item.payload = texto.replace(" ", "+")
       item.url = host + 'search.html'

       return list_search(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

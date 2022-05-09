# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://areshd.com/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release/' in url:
        raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/', group = 'TENDENCIAS', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tvshows/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host + 'episodes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Nuevas temporadas', action = 'list_all', url = host + 'seasons/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/', group = 'TENDENCIAS', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<li id="menu-item-\d+" class="menu-item menu-item-type-taxonomy menu-item-object-genres menu-item-\d+"><a href="([^"]+)">([^<]+)'
    matches = re.compile(patron).findall(data)

    for url, title in matches:
        if title == 'BÉLICA':
            title = 'Bélica'

        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1939, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'release/' + str(x) + '/', action = 'list_all' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque =  scrapertools.find_single_match(data, '>Networks</a>(.*?)>TENDENCIAS<')
    matches = re.compile('<li id="menu-item-.*?<a href="(.*?)">(.*?)</a>').findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if not item.group:
        item.group = '<h2>Añadido recientemente'
    else:
        if not item.group == '<h2>Añadido recientemente':
            item.group = '<h1>'

    bloque = scrapertools.find_single_match(data, str(item.group) + '(.*?)>TITULOS MAS VISTOS<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '</h3><span>(.*?)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')

        if '/seasons/' in url:
            if item.search_type == 'movie': continue

            tempo = scrapertools.find_single_match(match, '<a href=".*?>Temporada (.*?)</a>').strip()
            if not tempo: continue

            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                        contentType = 'season', contentSerieName = title, contentSeason = tempo, page = 0, infoLabels={'year':year} ))

        elif '/tvshows/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year':year} ))

        else:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<span class="current">' + ".*?<a href='(.*?)'")
        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', group = item.group, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
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
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '/seasons/' in item.url:
        bloque = data
    else:
        bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "</span>(.*?)</div></div>")

    patron = "<li class='mark-.*?src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>"

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('AresHd', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for thumb, s_e, url, title in matches[item.page * item.perpage:]:
        episode = scrapertools.find_single_match(s_e, ".*? - (.*?)$")

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<div id='playeroptions'(.*?)</ul></div></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-(.*?)</span></li>")

    ses = 0

    for match in matches:
        ses += 1

        dpost = scrapertools.find_single_match(match, "data-post='(.*?)'")
        dtype = scrapertools.find_single_match(match, "data-type='(.*?)'")
        dnume = scrapertools.find_single_match(match, "data-nume='(.*?)'")

        lang = scrapertools.find_single_match(match, "<span class='title'>(.*?)</span>")

        if 'Latino' in lang:
            lang = 'Lat'
        elif 'Castellano' in lang or 'Español' in lang:
            lang = 'Esp'
        elif 'Subtitulado' in lang or 'VOSE' in lang:
            lang = 'Vose'
        else:
            lang = '?'

        srv = scrapertools.find_single_match(match, "<span class='server'>(.*?)</span>")

        other = srv.lower()
        other = other.replace('.com', '').replace('.co', '').replace('.cc', '').replace('.ru', '').replace('.tv', '').replace('.site', '').strip()

        if 'youtube' in other: continue
        elif 'waaw' in other: continue
        elif 'hqq' in other: continue
        elif 'netu' in other: continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '',
                              dpost = dpost, dtype = dtype, dnume = dnume, language = lang, other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.dpost:
        data = do_downloadpage(host + '/wp-json/dooplayer/v2/' + item.dpost +'/' + item.dtype + '/2')

        vid = scrapertools.find_single_match(data, '"embed_url":".*?h=(.*?)"')

        if vid:
            post = {'h': vid}
            url = httptools.downloadpage(host + 'f/r.php', post = post, follow_redirects=False).headers.get('location', '')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)>TITULOS MAS VISTOS<')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '</h3><span>(.*?)</span>')
        if not year:
            year = '-'

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<p>(.*?)</p>'))

        if '/tvshows/' in url:
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year':year} ))

        else:
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            sufijo = '' if item.search_type != 'all' else 'movie'

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

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


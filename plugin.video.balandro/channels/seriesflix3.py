# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://seriesflix3.com/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas?page=1', page = 1, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas/estrenos?page=1', page = 1, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series?page=1', page = 1, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'series/estrenos?page=1', page = 1, search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?</svg>(.*?)</a>').findall(bloque)

    for url, title in matches:
        title = title.strip()

        url = host[:-1] + url + '?page=1'

        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url, page = 1 ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1930, -1):
        url = host + 'peliculas-' + str(x) + '?page=1'

        itemlist.append(item.clone( title = str(x), url = url, page = 1, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)>© Seriesflix3')
    if not bloque: bloque = scrapertools.find_single_match(data, 'Series nuevas(.*?)>© Seriesflix3')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="movie-item">(.*?)</a></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        title = title.replace('Poster', '').strip()

        if not url or not title: continue

        url = host[:-1] + url

        thumb = scrapertools.find_single_match(match, '<img src=(.*?)alt=').strip()

        thumb = host[:-1] + thumb

        year = scrapertools.find_single_match(match, '<span class="year text-center">(.*?)</span>')
        if not year: year = '-'

        plot = scrapertools.find_single_match(match, '<p>(.*?)</p>')

        if '/serie/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year, 'plot': plot} ))

        else:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if 'rel="next"' in data:
            next_url = scrapertools.find_single_match(item.url, '(.*?)page=')
            if next_url:
                item.page = int(item.page) + 1
                next_pag = str(item.page)
                next_url = next_url + 'page=' + str(next_pag)

                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', page = next_pag, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('<li class="item-season".*?<span itemprop="name">Temporada(.*?)</span>', re.DOTALL).findall(data)

    for tempo in temporadas:
        tempo = tempo.strip()

        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo, page = 0 ))

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

    bloque = scrapertools.find_single_match(data, '<li class="item-season".*?<span itemprop="name">Temporada ' + str(item.contentSeason) + "(.*?)</li>")

    matches = re.compile('<meta itemprop="episodeNumber".*?content="(.*?)".*?<a href="(.*?)"', re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('SeriesFlix3', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for epis, url in matches[item.page * item.perpage:]:
        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=epis ))

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

    bloque = scrapertools.find_single_match(data, '<ul class="tabs-video">(.*?)</div><div class="video">')

    matches = scrapertools.find_multiple_matches(bloque, 'data-server="(.*?)".*?<span>(.*?)</span>')

    ses = 0

    for dplay, lang in matches:
        ses += 1

        lang = lang.strip()

        if 'Latino' in lang: lang = 'Lat'
        elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
        elif 'Subtitulado' in lang or 'VOSE' in lang: lang = 'Vose'
        else: lang = '?'

        url = dplay.strip()

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = 'directo', title = '', language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url:
        new_url = host + 'sandbox?v=' + url

        resp = httptools.downloadpage(new_url, follow_redirects=False, only_headers=True, raise_weberror=False)

        if 'location' in resp.headers: url = resp.headers['location']
        else:
            return 'Archivo [COLOR plum]inexistente[/COLOR]'

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if not servidor == 'directo':
            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone(server = servidor, url = url))

    return itemlist



def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'title="Búsqueda..."(.*?)$')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?<img src=(.*?)alt=.*?year text-center">(.*?)</span>.*?<p>(.*?)</p>')

    for url, thumb, year, title in matches:
        if not url or not title: continue

        url = host[:-1] + url

        thumb = thumb.strip()

        thumb = host[:-1] + thumb

        if not year: year = '-'

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if '/serie/' in url:
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        else:
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            sufijo = '' if item.search_type != 'all' else 'movie'

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()

    try:
        item.url = host + 'busqueda/' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://pelispanda.com/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/years/' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie', tipo = 'genero' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 4K 2160p', action = 'list_all', url = host + 'quality/4k-2160p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 1080p dual', action = 'list_all', url = host + 'quality/1080p-dual/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 1080p', action = 'list_all', url = host + 'quality/1080p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 720p', action = 'list_all', url = host + 'quality/720p/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En Micro HD', action = 'list_all', url = host + 'peliculas-microhd-9/', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?target=.*?">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    limit = 1969
    if item.search_type == 'tvshow': limit = 2009

    for x in range(current_year, limit, -1):
        url = host + 'years/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="card">(.*?)</div></div>')

    for match in matches:
        if '>Promoción<' in match: continue

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h3 class="card__title">.*?">(.*?)</a>')

        if not url or not title: continue

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        qlty = scrapertools.find_single_match(match, '<ul class="card__list">.*?<li>(.*?)</li>')

        if '/series/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': "-"} ))

        else:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                    contentType='movie', contentTitle=title, infoLabels={'year': "-"} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<ul class="pagination pagination-lg justify-content-center">' in data:
            next_url = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="(.*?)"')

            if next_url:
                if '/page/' in next_url:
                    itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile("<span>Temporada(.*?)</span>", re.DOTALL).findall(data)

    for tempo in temporadas:
        tempo = tempo.strip()
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

    qlty = scrapertools.find_single_match(data, '<span>Temporada ' + str(item.contentSeason) + '.*?<tbody>.*?</td>.*?<td>(.*?)</td>')

    lang = scrapertools.find_single_match(data, '<span>Temporada ' + str(item.contentSeason) + '.*?<tbody>.*?</td>.*?</td>.*?<td>(.*?)</td>')

    if 'Castellano' in lang: lang = 'Esp'
    elif 'Latino' in lang: lang = 'Lat'
    elif 'Subitulado' in lang: lang = 'Vose'
    elif 'Version Original' in lang: lang = 'VO'

    matches = re.compile('<a class="btn btn-primary dwnlds"(.*?)</tr>', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PelisPanda', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for match in matches[item.page * item.perpage:]:
        tempo = scrapertools.find_single_match(match, 'data-season="(.*?)"')
        if not tempo == str(item.contentSeason): continue

        epis = scrapertools.find_single_match(match, 'data-serie="(.*?)"')

        url = scrapertools.find_single_match(match, 'href="(.*?)"')

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'")

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, language = lang, quality = qlty,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.contentType == 'episode':
        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = item.url, server = 'torrent',
                              language = item.language, quality = item.quality ))

        return itemlist

    data = do_downloadpage(item.url)

    links = scrapertools.find_multiple_matches(data, '<td>Torrent</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?href="(.*?)"')

    for qlty, lang, size, link in links:
        if 'Castellano' in lang: lang = 'Esp'
        elif 'Latino' in lang: lang = 'Lat'
        elif 'Subitulado' in lang: lang = 'Vose'
        elif 'Version Original' in lang: lang = 'VO'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = link, server = 'torrent',
                              language = lang, quality = qlty, other = size ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    host_torrent = host[:-1]
    url_base64 = decrypters.decode_url_base64(url, host_torrent)

    if url_base64.startswith('magnet:'):
        itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    elif url_base64.endswith(".torrent"):
       itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'buscar/?buscar=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

# -*- coding: utf-8 -*-

import re, base64

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

    itemlist.append(item.clone( title = 'Catálogo (últimas online)', action = 'list_all', url = host,
                                group = 'cupo', page = 0, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos?page=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series?page=1', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '</i> Géneros </h2>(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?"></i>(.*?)</a>').findall(bloque)

    for url, title in matches:
        url = url + '?page=1'

        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1930, -1):
        url = host + 'peliculas-' + str(x) + '?page=1'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 1

    data = do_downloadpage(item.url)

    if item.group == 'cupo':
        bloque = scrapertools.find_single_match(data, '</i> Películas online</h2>(.*?)>© Seriesflix3')
    else:
        bloque = scrapertools.find_single_match(data, '<h1(.*?)>© Seriesflix3')
        if not bloque: bloque = scrapertools.find_single_match(data, 'Series nuevas(.*?)>© Seriesflix3')

    matches = scrapertools.find_multiple_matches(bloque, '<div class="movie-item">(.*?)</a></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        title = title.replace('Poster', '').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<img src=(.*?)alt=').strip()

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

    if item.gropu == 'cupo': return itemlist

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

    temporadas = re.compile('<h3 class="item-season-title">.*?</i>(.*?)</h3>', re.DOTALL).findall(data)

    for tempo in temporadas:
        tempo = tempo. replace('Temporada', '').strip()

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

    bloque = scrapertools.find_single_match(data, '<h3 class="item-season-title">.*?</i> Temporada ' + str(item.contentSeason) + "(.*?)</div></div>")

    matches = re.compile('<a href="(.*?)".*?<i class="icon-play-circle"></i>(.*?)</a>', re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('SeriesFlix3', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, title in matches[item.page * item.perpage:]:
        episode = title.replace('Capítulo', '').strip()

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
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

    bloque = scrapertools.find_single_match(data, '<div class="tabs-video">(.*?)</ul></div>')

    matches = scrapertools.find_multiple_matches(bloque, 'data-player-video="(.*?)".*?</i>(.*?)</a>')

    ses = 0

    for dplay, lang in matches:
        ses += 1

        lang = lang.strip()

        if 'Latino' in lang: lang = 'Lat'
        elif 'Castellano' in lang or 'Español' in lang: lang = 'Esp'
        elif 'Subtitulado' in lang or 'VOSE' in lang: lang = 'Vose'
        else: lang = '?'

        url = base64.b64decode(dplay).strip()

        if '/hqq.' in str(url) or '/waaw.' in str(url) or '/netu.' in str(url): continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', url = url, server = servidor, title = '', language = lang ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'href=([^>]+).*?src=([^ ]+) .*?year text-center([^<]+)<.*?p>([^<]+)<')

    for url, thumb, year, title in matches:
        url = re.sub(r"\\|\"", "", url)
        title = title.decode('unicode_escape')

        if not url or not title: continue

        thumb = re.sub(r"\\|\"", "", thumb)
        year = re.sub(r"\\|\"|>", "", year)

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if '/serie/' in url:
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year':year} ))

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
        data = do_downloadpage(host)
        token = scrapertools.find_single_match(data, 'name=csrf-token content="([^"]+)"')
        item.url = host + 'suggest?query=%s&_token=%s' % (texto.replace(" ", "+"), token)
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


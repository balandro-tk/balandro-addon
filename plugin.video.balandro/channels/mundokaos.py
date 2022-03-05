# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

from lib import jsunpack


host = 'https://mundokaos.tv/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    url = url.replace('https://mundokaos.net/', host)

    headers = {'Referer': host}

    if '/release/' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + 'generos/marvel/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Generos<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Marvel': continue

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'release/' + str(x) + '/', action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data = scrapertools.find_single_match(str(data), '<h2>Añadido recientemente(.*?)>Peliculas y Series Mas Vistas<')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        year = scrapertools.find_single_match(match, '</h3>.*?<span>.*?,(.*?)</span>')
        year = year.strip()

        if not year: year = '-'
        else:
           if '(' + year + ')' in title:
               title = title.replace('(' + year + ')', '').strip()

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')

        if '/peliculas/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + "href='(.*?)'")

    if next_page:
        if '/page/' in next_page:
            itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<span class='se-t.*?'>(.*?)</span>")

    for  numtempo in matches:
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

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "(.*?)</div></div>")

    patron = "<li class='mark-(.*?)'>.*?<img src='(.*?)'.*?<a href='(.*?)'>(.*?)</a>"

    matches = scrapertools.find_multiple_matches(bloque, patron)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('MundoKaos', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for episode, thumb, url, title in matches[item.page * item.perpage:]:
        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color= 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Spain': 'Esp', 'Mexico': 'Lat', 'Latino': 'Lat', 'Subtitulado': 'Vose', 'United-States-of-AmericaUSA': 'Vose'}

    if '/episodios/' in item.url:
        _type = '2'
    else:
        _type = 'movie'

    data = do_downloadpage(item.url)

    patron = "<li id='player-option-.*?data-type='(.*?)'.*?data-post='(.*?)'.*?data-nume='(.*?)'.*?<span class='title'>(.*?)</span>"

    matches = scrapertools.find_multiple_matches(data, patron)

    ses = 0

    for _type, _post, _nume, lang in matches:
        ses += 1

        if _nume.lower() == 'trailer': continue

        url = host + 'wp-json/dooplayer/v2/%s/%s/%s'  %  (_post, _type, _nume)

        idioma = IDIOMAS.get(lang, lang)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, language = idioma ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if 'mundokaos' in item.url:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'
        elif 'gounlimited' in url or '/streamsb8.' in url:
            return 'Servidor [COLOR tan]No soportado[/COLOR]'

        if url:
            url = url.replace('\\/', '/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone( url=url, server=servidor))

            return itemlist

    if 'mega1080p' in item.url:
        url = do_downloadpage(item.url)
        pack = scrapertools.find_single_match(url, 'p,a,c,k,e,d.*?</script>')
        unpack = jsunpack.unpack(pack).replace('\\', '')

        url = scrapertools.find_single_match(unpack, "'file':'([^']+)'")

        if url:
            url = url.replace('/master', '/720/720p')
            url = 'https://pro.mega1080p.club/' + url
            url += '|Referer=' + url

            itemlist.append(item.clone( url=url, server='directo'))

            return itemlist

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone(server = servidor, url = url))

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

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        if year:
           if '(' + year + ')' in title:
               title = title.replace('(' + year + ')', '').strip()
        else:
            year = '-'

        if '/peliculas/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
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

# -*- coding: utf-8 -*-


from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = "https://pelismaraton.com/"


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    #headers = {'Referer': host}

    if '/peliculas-del/' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(host + 'pelicula/')

    bloque = scrapertools.find_single_match(data, '>Peliculas Por Generos(.*?)>Peliculas Por Año')

    matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)title.*?</i>(.*?)<span>')

    for url, title in matches:
        if descartar_xxx:
           if title == 'Erotico': continue

        url = url.strip()

        title = title.capitalize()

        itemlist.append(item.clone( title = title, action = 'list_all', url = url, genre = title ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    url_any = host + '/peliculas-del/'

    for x in range(current_year, 2009, -1):
        itemlist.append(item.clone( title=str(x), url = url_any + str(x) + '/', action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)<h3')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a title=.*?href=(.*?)class')
        if not url:
            url = scrapertools.find_single_match(match, '<a title=.*?href="(.*?)"')

        title = scrapertools.find_single_match(match, '<h2.*?">(.*?)</h2>')
        if not title:
            title = scrapertools.find_single_match(match, '<h2.*?title=.*?>(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src=(.*?)title')
        if not thumb: 
            thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class=year>.*?>(.*?)</a>')
        if not year:
            year = '-'

        url = url.strip()
        title = title.strip()
        thumb = thumb.strip()

        tipo = 'tvshow' if 'serie/' in item.url or 'serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        if not item.search_type == 'all':
            if not tipo == item.search_type: continue

        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': year} ))

        if tipo == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<nav class="navigation pagination">.*?' + "class='current'.*?" + 'href="(.*?)"')
        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action='list_all', url = next_page, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<h2 class="number-season">.*?Temporada (\d+).*?</h2>')

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season ))

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

    season = item.contentSeason

    patron = '<h2 class="number-season">.*?Temporada %s (.*?)</div>' % str(season)

    bloque = scrapertools.find_single_match(data, patron)

    matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>.*?Capitulo(.*?):(.*?)</a>')

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PelisMaraton', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, epis, title in matches[item.page * item.perpage:]:
        epis = epis.replace(':', '').strip()

        if '<span' in title:
            title = scrapertools.find_single_match(title, '(.*?)<span')

        title = title.strip()

        titulo = season + 'x%s %s' % (epis, title)

        url = url.strip()

        if url:
            itemlist.append(item.clone( action='findvideos', url = url, title = titulo, 
                                        contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'latino': 'Lat', 'castellano': 'Esp', 'español': 'Esp', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<a class=aa-link.*?data="(.*?)".*?<span class=option>(.*?)</span>')

    for url, srv_lang in matches:
        servidor = srv_lang.split('-')[0]
        servidor = servidor.strip().lower()

        if servidor:
            lang = srv_lang.split('-')[1]
            lang = lang.replace('Español', '').strip().lower()

            itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang,lang) ))

    # Descargar
    matches = scrapertools.find_multiple_matches(data, '<span class=num>#.*?</span>(.*?)</td>.*?<td>(.*?)</td>.*?href="(.*?)"')

    for servidor, lang, url in matches:
        servidor = servidor.strip().lower()

        if servidor:
            lang = lang.replace('Español', '').strip().lower()

            itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '',
                            url = url, language = IDIOMAS.get(lang,lang), other = 'D' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = ''

    if item.other == 'D':
        data = httptools.downloadpage(item.url).data
        url = scrapertools.find_single_match(data, '<a id="DownloadScript".*?href="(.*?)"')

    elif item.url.startswith(host):
        data = httptools.downloadpage(item.url).data
        url = scrapertools.find_single_match(data, 'location.href = "([^"]+)')

        if not url.startswith('http'):
            url = 'https:' + url

    if url:
       servidor = servertools.get_server_from_url(url)
       servidor = servertools.corregir_servidor(servidor)
       itemlist.append(item.clone(url = url, server = servidor))
    else:
        itemlist.append(item.clone(server = item.server, url = item.url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []


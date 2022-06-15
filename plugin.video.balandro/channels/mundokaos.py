# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://mundokaos.net/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://mundokaos.tv/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

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

    data = do_downloadpage(host + 'pelicula/')

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href=".*?>(.*?)</a>')

    for title in matches:
        cat = title

        cat = cat.replace('&amp;', '&')

        if cat == 'Acción': cat = 'Accion'
        elif cat == 'Action & Adventure': cat = 'Action-Adventure'
        elif cat == 'Animación': cat = 'Animacion'
        elif cat == 'Bélica': cat = 'Belica'
        elif cat == 'Ciencia ficción': cat = 'Ciencia-ficcion'
        elif cat == 'Fantasía': cat = 'Fantasia'
        elif cat == 'Música': cat = 'Musica'
        elif cat == 'Película de TV': cat = 'Pelicula-de-TV'
        elif cat == 'Sci-Fi & Fantasy': cat = 'Sci-Fi-Fantasy'
        elif cat == 'War & Politics': cat = 'War-Politics'

        url = host + 'category/' +  cat.lower() + '/'

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

    data = scrapertools.find_single_match(str(data), '<h1(.*?)</h3>')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '</h3>.*?<span>.*?,(.*?)</span>')
        year = year.strip()

        if not year: year = '-'
        else:
           if '(' + year + ')' in title: title = title.replace('(' + year + ')', '').strip()

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')

        if '/pelicula/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
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

    matches = scrapertools.find_multiple_matches(data, '<div class="seasons-bx".*?<p>Temporada.*?<span>(.*?)</span>')

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

    if '</div></div></div>' in data:
        bloque = scrapertools.find_single_match(data, '<div class="seasons-bx".*?<p>Temporada.*?<span>' + str(item.contentSeason) + '(.*?)</div></div></div>')
    else:
        bloque = scrapertools.find_single_match(data, '<div class="seasons-bx".*?<p>Temporada.*?<span>' + str(item.contentSeason) + '(.*?)</ul></div></div>')

    patron = 'src="(.*?)".*?alt="(.*?)".*?<span>(.*?)</span>.*?<a href="(.*?)"'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('MundoKaos', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for thumb, title, temp_epis, url, in matches[item.page * item.perpage:]:
        season =  scrapertools.find_single_match(temp_epis, 'S(.*?)-E').strip()

        if not season == str(item.contentSeason): continue

        episode = scrapertools.find_single_match(temp_epis, '.*?-E(.*?)$').strip()

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail=thumb, contentType = 'episode', contentEpisodeNumber = episode ))

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

    if '/episodio/' in item.url: _type = '2'
    else: _type = '1'

    data = do_downloadpage(item.url)

    _trid = scrapertools.find_single_match(data, '&trid=(.*?)&')
    if not _trid: return itemlist

    matches = scrapertools.find_multiple_matches(data, '<span class="num">OPCIÓN.*?<span>(.*?)</span>.*?-(.*?)-')

    ses = 0

    for _opt, lang in matches:
        ses += 1

        if not _opt: continue

        if not _opt == '0': _opt = (int(_opt) - 1)

        url = host + '?trembed=%s&trid=%s&trtype=%s' % (_opt, _trid, _type)

        lang = lang.strip()
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

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    url = item.url

    if '?trembed=' in item.url:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

    elif 'mundokaos' in item.url:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        if url: url = url.replace('\\/', '/')

    elif 'mega1080p' in item.url:
        from lib import jsunpack

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
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'
        elif 'gounlimited' in url or '/streamsb8.' in url:
            return 'Servidor [COLOR tan]No soportado[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone(server = servidor, url = url))

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

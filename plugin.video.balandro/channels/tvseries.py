# -*- coding: utf-8 -*-

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


# ~ links_genres_series = 'https://cinedeantes2.weebly.com'

host = 'https://seriestvdeantes'

perpage = 25


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    # ~ itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'TV-SeriesDeAntes Ciencia Ficción', action = 'menu_series', url = host + '-2.weebly.com' ))

    itemlist.append(item.clone( title = 'TV-SeriesDeAntes Comedias', action = 'menu_series', url = host + '5.weebly.com' ))

    itemlist.append(item.clone( title = 'TV-SeriesDeAntes Dibujos Animados', action = 'menu_series', url = host + '-6.weebly.com' ))

    itemlist.append(item.clone( title = 'TV-SeriesDeAntes Detectives-Espionaje', action = 'menu_series', url = host + '-4.weebly.com' ))

    itemlist.append(item.clone( title = 'TV-SeriesDeAntes Policiacas', action = 'menu_series', url = host + '-3.weebly.com' ))

    itemlist.append(item.clone( title = 'TV-SeriesDeAntes TVE, Mini Series y en Vose', action = 'menu_series', url = host + '-07.weebly.com' ))

    itemlist.append(item.clone( title = 'TV-SeriesDeAntes Variadas', action = 'menu_series', url = host + '-08.weebly.com' ))

    itemlist.append(item.clone( title = 'TV-SeriesDeAntes Westerns', action = 'menu_series', url = host + '1.weebly.com' ))

    return itemlist


def menu_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', url = item.url, search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'series', url = item.url ))

    itemlist.append(item.clone( title = 'Catálogo series con temporadas', action = 'series', url = item.url, grupo = 'seasons' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', url = item.url ))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    sort_series = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<li id="active" class="wsite-menu-item-wrap">(.*?)<a class="hamburger"')

    if not bloque: bloque = scrapertools.find_single_match(data, '<div class="dummy-nav">(.*?)<div class="hamburger')
    if not bloque:
        bloque = scrapertools.find_single_match(data, '<li id="active" class="wsite-menu-item-wrap">(.*?)<li id="active" class="wsite-menu-item-wrap">')

    if not item.grupo == 'seasons': matches = scrapertools.find_multiple_matches(bloque, '<li id="(.*?)</li>')
    else: matches = scrapertools.find_multiple_matches(bloque, '<li id="(.*?)</a>')

    i = 0

    for match in matches:
        if '<span class="wsite-menu-arrow">' in match: continue

        if '<li id="wsite-nav-' in match:
            match = match + '</li>'
            match = scrapertools.find_single_match(match, '<li id="wsite-nav-(.*?)</li>')

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not url: continue

        title = scrapertools.find_single_match(match, 'class="wsite-menu-title">(.*?)</span>').strip()
        if not title: title = scrapertools.find_single_match(match, 'class="wsite-menu-item".*?>(.*?)</a>').strip()

        if not title: continue

        url = item.url + url

        if item.filtro_search:
            buscado = item.filtro_search.lower().strip()
            titulo = title.lower().strip()

            if len(buscado) == 1:
                letra_titulo = titulo[0]
                if not letra_titulo == buscado:
                    if not buscado == '#': continue
                    if letra_titulo in '0123456789': pass
                    else: continue
            elif not buscado in titulo: continue
        else:
            if item.grupo == 'seasons':
                if not '&ordm;' in title: continue

        title = title.replace('&ordm;', 'ª').replace('))', ')').replace('Ó', 'ó').replace('Á', 'á').replace('Í', 'í').replace('Ñ', 'ñ')
        if title.startswith("á") == True: title = title.replace('á', 'a')

        title = title.lower()
        title = title.capitalize()

        if 'ª' in title: title = title.replace('ª', 'ª - T')

        year = ''

        try:
            name = title.split("(")[0]
            name = name.strip()

            if not item.grupo == 'seasons': year = title.split(" (")[1]

            year = year.replace(')', '')
            if '-' in year: year = year.split("-")[0]
        except:
            name = title

        if 'ª' in year: year = '-'
        elif not year == '-':
            if ('(' + year +')') in title:
                title = title.replace('(' + year + ')', '').strip()

        i +=1

        sort_series.append([url, title, name, year])

    if not i == 0:
        num_matches = i -1
        desde = item.page * perpage
        hasta = desde + perpage

        if num_matches < desde:
            hasta = desde
            desde = 0

        sort_series = sorted(sort_series, key=lambda x: x[1])

        for url, title, name, year in sort_series[desde:hasta]:
            itemlist.append(item.clone( action = 'list_all', title = title, url = url, contentType = 'tvshow',
                                        contentSerieName = name, infoLabels = {'year': year} ))

        tmdb.set_infoLabels(itemlist)

        if not item.filtro_search:
            if i > perpage:
                if num_matches > hasta:
                    next_page = item.page + 1
                    itemlist.append(item.clone( title = 'Siguientes ...', page = next_page, action = 'series', text_color='coral' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div id=".*?class="wcustomhtml".*?src="(.*?)"')

    cover = scrapertools.find_single_match(data, '<div><div class="wsite-image wsite-image-border-none ".*?<img src="([^"]+)"')
    if cover.startswith("/") == True: cover = item.url + cover

    order = 0

    if matches: platformtools.dialog_notification('TvSeries', '[COLOR blue]Cargando episodios[/COLOR]')

    for match in matches:
        if match.startswith('//') == True: url = 'https:' + match
        else: url = match

        data_thumb = httptools.downloadpage(url).data

        thumb = scrapertools.find_single_match(data_thumb, '<img src="([^"]+)"')
        thumb = thumb.replace('&amp;', '&')

        if not thumb: thumb = cover

        title = scrapertools.find_single_match(data_thumb, 'class="vid-card_n">(.*?)</span>')
        title = title.replace('(EEEE) p30', '').replace('(EEE) p20', '').replace('(EE)', '').replace('(C)', '').replace('(c)', '').strip()

        if not title:
            order += 1
            title = '¿ Episodio  ' + str(order) + ' ?'
        else:
            if title.endswith(") 0") == True: title = title.replace(' 0', '')
            elif title.endswith(") 1") == True: title = title.replace(' 1', '')
            elif title.endswith(") 2") == True: title = title.replace(' 2', '')
            elif title.endswith(") 3") == True: title = title.replace(' 3', '')
            elif title.endswith(") 4") == True: title = title.replace(' 4', '')
            elif title.endswith(") 5") == True: title = title.replace(' 5', '')
            elif title.endswith(") 6") == True: title = title.replace(' 6', '')
            elif title.endswith(") 7") == True: title = title.replace(' 7', '')
            elif title.endswith(") 8") == True: title = title.replace(' 8', '')
            elif title.endswith(") 9") == True: title = title.replace(' 9', '')

        lang = 'Esp'
        if ' Vose' in title or ' VOSE' in title or ' vose' in title or ' V.o.s.e.' in title or ' V.O.S.E.' in title or ' v.o.s.e.' in title: lang = 'Vose'

        temporada = 0
        capitulo = 0

        if not '"' in title:
            titulo = title.lower()
            titulo = titulo.replace('(', '"').replace(')', '"')
            temporada = scrapertools.find_single_match(titulo, '.*?"(.*?)x')
            capitulo = scrapertools.find_single_match(titulo, '.*?".*?x(.*?)"')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, language = lang, thumbnail = thumb, contentType='episode', contentSeason = temporada, contentEpisodeNumber = capitulo ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'abcdefghijklmnopqrstuvwxyz#':
        itemlist.append(item.clone ( title = letra.upper(), url = item.url, action = 'series', filtro_search = letra ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    servidor = servertools.get_server_from_url(item.url)
    servidor = servertools.corregir_servidor(servidor)

    if servidor:
        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = item.language, url = item.url ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.filtro_search = texto
        return series(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

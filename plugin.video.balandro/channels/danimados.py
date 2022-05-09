# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.d-animados.com/'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
    itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/',
                                _taxonomy = 'none', _term= 'none', _search= 'none', _type= 'movies', page = 1, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'aseries/',
                                _taxonomy = 'none', _term = 'none', _search = 'none', _type = 'series', page = 1, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_last', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def mainlist_animes(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color = 'springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'tag/anime/',
                                _taxonomy = 'post_tag', _term = '180', _search = 'none', _type = 'mixed', page = 1, search_type = 'all' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, 'menu-item-object-category.*?<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url, genre = title, group = 'generos', page = 1 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    _nonce = scrapertools.find_single_match(data, '"nonce":"(\w+)')

    if item.gouup == 'generos':
        item._genres = scrapertools.find_single_match(data, 'data-term="(\w+)')
        item._term = item._genres
        item._genres = "\"" + item._genres + "\""
        item._taxonomy = "category"
        item._type = "mixed"

    post ={
	"action": "action_search",
	"vars": "{\"_wpsearch\":\"%s\",\"taxonomy\":\"%s\",\"search\":\"%s\",\"term\":\"%s\",\"type\":\"%s\",\"genres\":[%s],\"years\":[],\"sort\":\"1\",\"page\":%s}" % (_nonce, item._taxonomy, item._search, item._term, item._type, item._genres, item.page)
    }

    data = httptools.downloadpage(url = host + 'wp-admin/admin-ajax.php', post=post).data

    data = data.replace('\\/', '/')

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        match = match.replace('=\\', '=').replace('\\"', '"')

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not title or not url: continue

        title = scrapertools.decodeHtmlentities(title)

        tipo = 'tvshow' if '/series/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')

        if '/movies/' in url:
            if item.search_type == 'tvshow': continue

            if tipo == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, languages='Lat',
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if '/series/' in url:
            if item.search_type == 'movie': continue

            if tipo == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo, languages='Lat',
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        presentar = True
        if not item.group == 'generos':
            if len(itemlist) < 15: presentar = False

        if presentar:
            itemlist.append(item.clone( title='Siguientes ...', _referer = item._referer,
                                        _taxonomy = item._taxonomy, _term = item._term, _type = item._type, page = item.page + 1,
                                        action='list_all', text_color='coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron  = 'item-pelicula pull-left.*?href="([^"]+).*?title="([^"]+).*?<img src="([^"]+)'

    matches = scrapertools.find_multiple_matches(data, patron)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages='Lat',
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    temporadas = re.compile('</figure><div><p>Temporada.*?<span>(.*?)</span>', re.DOTALL).findall(data)

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

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, "</figure><div><p>Temporada.*?<span>" + str(item.contentSeason) + "</span>(.*?)" + '<div class="tags">')

    matches = re.compile('<figure(.*?)</div></div>', re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('Danimados', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    i = 0

    for match in matches[item.page * item.perpage:]:
        i += 1

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3 class="title"><span>.*?</span>(.*?)</h3>').strip()

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        episode = i

        titulo = str(item.contentSeason) + 'x' + str(i) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

        episode = i

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if not item.url: return itemlist

    data = httptools.downloadpage(item.url).data

    matches = re.findall('<span class="num">OPCIÓN <span>.*?src="(.*?)"', data, flags=re.DOTALL)

    ses = 0

    for link in matches:
        data = httptools.downloadpage(link, headers = {'Referer': item.url}).data

        url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')

        if url:
            data2 = httptools.downloadpage(url, headers = {'Referer': item.url}).data

            links = re.findall("go_to_player.*?'(.*?)'", data2, flags=re.DOTALL)

            for url in links:
                ses += 1

                if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
                    ses = ses -1
                    continue

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                other = ''
                if servidor == 'directo':
                   if '/player' in url: other = 'Player'
                   elif '/sbfast' in url: other = 'Sbfast'

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, language = 'Lat', title = '', url = url, other = other )) 

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.server == 'directo':
        data = httptools.downloadpage(url).data

        url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        if not url:
            if 'function runPlayer' in data:
                api = scrapertools.find_single_match(data, 'function runPlayer.*?url:.*?"(.*?)"')
                if api.startswith('//'): api = 'https:' + api

                if api:
                    data_api = httptools.downloadpage(api).data

                    srv = scrapertools.find_single_match(str(data_api), '"host":"(.*?)"')

                    if srv == 'mediafire':
                        return 'Servidor Mediafire [COLOR tan]No soportado[/COLOR]'

                    url = scrapertools.find_single_match(str(data_api), '"id":"(.*?)"')
                    #if not url: url = scrapertools.find_single_match(str(data_api), '"file":"(.*?)"')

                    if srv == 'videobin': url = 'https://videobin.co/' + url

                    url = url.replace('\\/', '/')

                    if url.startswith('//'): url = 'https:' + url

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    itemlist = []

    try:
        item.url =  host + '?s=' + texto.replace(" ", "+")

        item._taxonomy = 'none'
        item._term = 'none'
        item._type = 'mixed'
        item.page = 1

        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return itemlist

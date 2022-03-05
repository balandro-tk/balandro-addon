# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.animefenix.com/'

perpage = 30


def mainlist(item):
    return mainlist_anime(item)

def mainlist_series(item):
    return mainlist_anime(item)


def mainlist_anime(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_last', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'animes?estado[]=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'animes?type%5B%5D=ova&order=default',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'animes?type%5B%5D=movie&order=default',
                                search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'animes?type%5B%5D=special&order=default',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categorías', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = host + 'animes'

    data = httptools.downloadpage(url_cat).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="order_select"(.*?)<\/select>')

    matches = re.compile(r'<option value="([^"]+)"\s*>([^<]+)').findall(data)

    for categoria, title in matches:
        if title == "Calificación": continue

        url = "%s?order=%s&page=1" % (url_cat, categoria)

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + 'animes'

    data = httptools.downloadpage(url_genre).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="genre_select" multiple="multiple">(.*?)<\/select>')

    matches = re.compile(r'<option value="([^"]+)"\s*>([^<]+)').findall(data)

    for genre_id, title in matches:
        url = "%s?genero[]=%s&order=default&page=1" % (url_genre, genre_id)

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    url_anio = host + 'animes'

    data = httptools.downloadpage(url_anio).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, r'<select name="[^"]+" id="year_select" multiple="multiple">(.*?)<\/select>')

    matches = re.compile(r'<option value="([^"]+)"\s*>([^<]+)').findall(data)

    for anio, title in matches:
        url = "%s?year[]=%s&order=default&page=1" % (url_anio, anio)

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<article class="serie-card"><div class="serie-card__information"><p>([^<]+)<\/p>'
    patron += '<\/div><figure class="image"><a href="([^"]+)" title="([^"]+)">'
    patron += '<img src="([^"]+)".*?<span class="tag year is-dark">(\d+)'

    matches = re.compile(patron).findall(data)

    for info, url, title, thumb, year in matches[item.page * perpage:]:
        if not url or not title: continue

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year':year, 'plot': info} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if '<a class="pagination-link" href="' in data:
        next_url = scrapertools.find_single_match(data, '<a class="pagination-link" href="([^"]+)">Siguiente')
        next_url = item.url.split("?")[0] + next_url
        itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, 'Últimas series agregadas(.*?)Comentarios')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)"')

    for url, thumb, title in matches:
        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year':'-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, 'Últimos Episodios Agregados(.*?)Últimas series agregadas')

    matches = re.compile('<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)".*?<div class="overepisode.*?">(.*?)</div>', re.DOTALL).findall(bloque)

    for url, thumb, title, episode in matches:
        episode = episode.replace('EP', 'epis.')

        title = episode + ' ' + title

        if url:
            itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail=thumb, contentType = 'episode'))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    matches = re.compile('<a class="fa-play-circle d-inline-flex align-items-center is-rounded " href="([^"]+)".*?<span>([^<]+)', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('AnimeFenix', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, title in matches[item.page * item.perpage:]:
        try:
            episode = scrapertools.find_single_match(title, "Episodio.*?(\d+)")
        except:
            episode = 0

        itemlist.append(item.clone( action='findvideos', url = url, title = title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=episode ))

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

    data = httptools.downloadpage(item.url).data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    ses = 0

    srvs = scrapertools.find_multiple_matches(data, '<a title="(.*?)" href="(.*?)"')

    matches = re.compile(r"tabsArray\['\d+'\] = \".*?src='(?:\.\.|)([^']+)", re.DOTALL).findall(data)

    for url in matches:
        ses += 1

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        serv = ''
        for srv, vid in srvs:
            vid = vid.replace('#vid', '')
            if not vid == str(ses): continue

            serv = srv.lower()
            break

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, other = serv ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith('//'): item.url = 'https:' + item.url

    item.url = item.url.replace('&amp;', '&')

    servidor = item.server
    url = item.url

    if '/videa.hu/' in url:
        if url.startswith('//'): url = 'https:' + url
        data = httptools.downloadpage(url).data

        if '/recaptcha/api.js?render=explicit&hl=hu' in data:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    elif '/stream/amz.php' in url:
        if not url.startswith("http"): url = host + url[1:]

        data = httptools.downloadpage(url).data

        url = scrapertools.find_single_match(data, '"file":"([^"]+)"')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

    elif '/redirect.php?' in url:
        data = httptools.downloadpage(url).data
        url = scrapertools.find_single_match(data, 'playerContainer.*?src="([^"]+)"')

        if '/videa.hu/' in url:
            if url.startswith('//'): url = 'https:' + url
            data = httptools.downloadpage(url).data

            if '/recaptcha/api.js?render=explicit&hl=hu' in data:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        elif '/stream/amz.php' in url:
            if not url.startswith("http"): url = host + url[1:]

            data = httptools.downloadpage(url).data
            url = scrapertools.find_single_match(data, '"file":"([^"]+)"')

        elif 'burstcloud' in url:
            data = httptools.downloadpage(url).data

            file = scrapertools.find_single_match(data, 'data-file-id="([^"]+)"')
            if file:
                post = {"fileId": file}

                data = httptools.downloadpage('https://www.burstcloud.co/file/play-request/', post=post, headers={'referer': url}).data

                url = scrapertools.find_single_match(data, '"cdnUrl".*?"([^"]+)"')

                if url: url = url + '|referer=https://www.burstcloud.co/'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

    if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    if url:
        if not url.startswith("http"): url = "https:" + url
        url = url.replace('&amp;', '&').replace("\\/", "/")

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'animes?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


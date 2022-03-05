# -*- coding: utf-8 -*-

from datetime import datetime

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = "https://tioanime.com"


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

    current_year = int(datetime.today().year)

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/directorio', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all',
                                url = host + '/directorio?type%5B%5D=0&year=1950%2C' + str(current_year) +'&status=1&sort=recent', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host, group = 'last_epis', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + '/directorio?type%5B%5D=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + '/directorio?type%5B%5D=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + '/directorio?type%5B%5D=3', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + '/directorio??genero%5B%5D='

    current_year = int(datetime.today().year)

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, '<a href="/directorio(.*?)".*?>(.*?)</a>')

    for genre, title in matches:
        if not '?genero=' in genre: continue

        genre = genre.replace('?genero=', '')

        url = url_genre + genre + '&year=1950%2C' + str(current_year) + '&status=2&sort=recent'

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    url_anios = host + '/directorio?year='

    current_year = int(datetime.today().year)

    for x in range(current_year, 1949, -1):
        url = url_anios + str(x) + '%2C' + str(x) + '&status=2&sort=recent'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3 class="title">(.*?)</h3>')

        if not url or not title: continue

        url = host + url
        thumb = host + thumb

        if item.group == 'last_epis':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action = 'episodios', url = url, title = title, thumbnail = thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))

    next_page = scrapertools.find_single_match(data,'<li class="page-item active">.*?<li class="page-item">.*?href="(.*?)"')
    if next_page:
        if itemlist:
            next_page = host + next_page

            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    info = eval(scrapertools.find_single_match(data, "var anime_info = (\[.*?\])"))
    epis = eval(scrapertools.find_single_match(data, "var episodes = (\[.*?\])"))

    epis = epis[::-1]

    if item.page == 0:
        sum_parts = len(epis)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('TioAnime', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for epi in epis[item.page * item.perpage:]:
        url =  host + '/ver/' + '%s-%s' % (info[1], epi)
        epi_num = epi

        titulo = '1x%s - Episodio %s' % (epi_num, epi_num)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, 
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epi_num ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    videos = eval(scrapertools.find_single_match(data, "var videos = (\[.*?);"))

    ses = 0

    for datos in videos:
        ses += 1

        servidor = datos[0]
        servidor = servidor.lower()

        url = datos[1].replace("\\/", "/")

        if servidor == 'netu': continue
        elif servidor == 'streamium': continue
        elif servidor == 'amus': continue
        elif servidor == 'mepu': continue

        if servidor == 'umi':
            url = url.replace("gocdn.html#", "gocdn.php?v=")

            data = httptools.downloadpage(url).data
            url = scrapertools.find_single_match(data, '"file":"(.*?)"')
            url = url.replace("\\/", "/")

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = 'Vose' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "/directorio?q=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

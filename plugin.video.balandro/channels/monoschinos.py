# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3: import urllib.parse as urllib
else: import urllib


import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://monoschinos2.com'


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
        if actions.adults_password(item) == False: return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/animes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + '/animes?genero=emision', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + '/animes?categoria=false&genero=castellano', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + '/animes?categoria=false&genero=latino', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En blu-ray', action = 'list_all', url = host + '/animes?categoria=false&genero=blu-ray', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url_genre = host + '/animes'

    data = httptools.downloadpage(url_genre).data

    bloque = scrapertools.find_single_match(data, '<select name="genero">(.*?)</select>')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    for gen, title in matches:
        title = title.strip()

        if title == 'Genero': continue
        elif title == 'Blu-ray': continue
        elif title == 'Castellano': continue
        elif title == 'Emisión': continue
        elif title == 'Latino': continue

        url = host + '/animes?categoria=false&genero=%s&fecha=false&letra=false' % gen

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1951, -1):
        url = host + '/animes?categoria=false&genero=false&fecha=%s&letra=false' % str(x)

        itemlist.append(item.clone( title = str(x), url = url, action='list_all' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = host + '/animes'

    data = httptools.downloadpage(url_cat).data

    bloque = scrapertools.find_single_match(data, '<select name="categoria">(.*?)</select>')

    matches = re.compile('<option value="(.*?)">(.*?)</option>').findall(bloque)

    for cat, title in matches:
        title = title.strip()

        if title == 'Categoría': continue

        url = host + '/animes?categoria=%s&genero=false&letra=false' % cat

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="col-.*?href="(.*?)".*?src="(.*?)".*?<h5.*?>(.*?)</h5>').findall(data)

    for url, thumb, title in matches:
        thumb = re.sub("image/imagen/160/224/", "assets/img/serie/imagen/", thumb)

        itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                        infoLabels={'year': '-'}, contentType = 'tvshow', contentSerieName = title ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '"page-item active".*?</li>.*?<a class="page-link" href="([^"]+)">')
        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral' ))

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>Capítulos Recientes(.*?)</section>')

    patron = '<div class="col col-md-6.*?alt="(.*?)".*?href="(.*?)".*?data-src="(.*?)".*?<h5>(.*?)</h5>.*?</div></div>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for title, url, thumb, epis in matches:
        titulo = title + ' [COLOR springgreen]Epis. ' + epis +'[/COLOR]'

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentSerieName=title, contentType = 'episode', contentSeason = 1, contentEpisodeNumber=epis ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data

    matches = re.compile('data-episode="(.*?)".*?href="(.*?)".*?data-src="(.*?)".*?<p class="animetitles">(.*?)<', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('MonosChinos', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    i = 0

    for epis, url, thumb, title in matches[item.page * item.perpage:]:
        i += 1

        title = title.replace('Sub Español', '').strip()

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber=i ))

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

    matches = re.compile('class="play-video".*?data-player="(.*?)">(.*?)</p>', re.DOTALL).findall(data)

    ses = 0

    for d_play, servidor in matches:
        ses += 1

        servidor = servidor.lower()

        if 'hqq' in servidor or 'waaw' in servidor or 'netu' in servidor: continue

        if servidor == 'ok': servidor = 'okru'

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', d_play = d_play, language = 'Vose' ))

    # download
    bloque = scrapertools.find_single_match(data, '<div class="downbtns">(.*?)</div>')

    matches = re.compile('href="(.*?)"><button>(.*?)<', re.DOTALL).findall(bloque)

    for url, srv in matches:
        ses += 1

        srv = srv.lower().strip()

        if srv == '1fichier': continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = srv, title = '', url = url, language = 'Vose', other = 'D' ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if not item.d_play:
        itemlist.append(item.clone( url = item.url, server = item.server ))
        return itemlist

    url = base64.b64decode(item.d_play).decode("utf-8")

    if host in url:
        url = scrapertools.find_single_match(url, 'url=(.*?)$')

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone( url = url, server = servidor ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/buscar?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


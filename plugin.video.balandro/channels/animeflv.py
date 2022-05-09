# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://ww3.animeflv.cc/'

perpage = 30


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www10.animeflv.cc/', 'https://www3.animeflv.net/', 'https://www3.animeflv.cc/'] 

    for ant in ant_hosts:
        url = url.replace(ant, host)

    data = httptools.downloadpage(url, post=post).data
    return data


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'browse', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos animes', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_epis', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Ovas', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=4',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=2',
                                search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Especiales', action = 'list_all', url = host + 'browse?genres=all&year=all&status=all&order=1&Tipo=3',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por categorías', action = 'categorias', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = url = host + 'browse'

    data = do_downloadpage(url_cat)

    matches = re.compile(r'<li class="tmp "><a><label class="radio"><input  type="radio" value="(\d+)" name="order" data-text="([^"]+)').findall(data)

    for categorie_id, title in matches:
        url = '%s?order=%s' %(url_cat, categorie_id)
        title = title.strip()

        itemlist.append(item.clone( action = "list_all", url = url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def generos(item):
    logger.info()
    itemlist = []

    url_genre = url = host + 'browse'

    data = do_downloadpage(url_genre)

    matches = re.compile(r'a><label><input  class="genre-ids" value="([^"]+)".*?type="checkbox">([^<]+)').findall(data)

    for genre_id, title in matches:
        url = '%s?genres=%s' %(url_genre, genre_id)

        itemlist.append(item.clone( action = "list_all", url = url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    url_anio = url = host + 'browse'

    tope_year = 1989

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        itemlist.append(item.clone( title = str(x), url = '%s?year=%s' % (url_anio, str(x)), action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<article class="Anime alt[^"]+"><a href="([^"]+)">'
    patron += '<.*?img src="([^"]+)".*?h3 class="Title">([^<]+).*?<span class="Type ([^"]+).*?<p class="des">([^<]+)'

    matches = re.compile(patron).findall(data)

    num_matches = len(matches)

    for url, thumb, title, tipo, info in matches[item.page * perpage:]:
        if not url or not title: continue

        if tipo == "movie":
            itemlist.append(item.clone( action='findvideos', url=url if url.startswith('http') else host[:-1] + url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url=url if url.startswith('http') else host[:-1] + url, title=title, thumbnail=thumb, 
                                        contentType = 'tvshow', plot = info, contentSerieName = title, infoLabels={'year':'-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
            buscar_next = False

    if buscar_next:
        if itemlist:
            next_url = scrapertools.find_single_match(data, "li\s*class=selected><a href='[^']+.*?<\/li><li.*?<a href='([^']+)")
            if next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if url.startswith('http') else item.url + next_url if not '?' in item.url else item.url.split('?')[0] + next_url,
                                            action = 'list_all', page = 0, text_color = 'coral' ))

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h2>Últimos episodios</h2>(.*?)<h2>Últimos animes agregados</h2>')

    patron = '<li>.*?<a href="(.*?)".*?<img src="(.*?)".*?<span class="Capi">(.*?)</span>.*?class="Title">(.*?)</strong>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for url, thumb, episode, title in matches:
        episode = episode.replace('Episodio', 'epis.')

        title = episode + ' ' + title

        if url:
            itemlist.append(item.clone( action='findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title,
                                        thumbnail=thumb, contentType = 'episode'))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="fa-play-circle"><a href="([^"]+)"><.*?this.src=\'([^\']+).*?<p>([^<]+)', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('AnimeFlv', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    i = 0

    for url, thumb, title in matches[item.page * item.perpage:]:
        i += 1

        itemlist.append(item.clone( action='findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title,
                                    thumbnail=thumb, contentType = 'episode', contentSeason = 1, contentEpisodeNumber = i ))

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
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile(r'<li role="presentation" data-video="([^"]+)" title="([^"]+)".*?<a href="[^"]+', re.DOTALL).findall(data)

    if not matches:
        new_url = scrapertools.find_single_match(data, '<ul class="ListCaps" id="episodeList".*?a href="(.*?)"')
        if new_url:
            if not new_url.startswith('http'):
                new_url = host[:-1] + new_url
                data = do_downloadpage(new_url)

                matches = re.compile(r'<li role="presentation" data-video="([^"]+)" title="([^"]+)".*?<a href="[^"]+', re.DOTALL).findall(data)

    ses = 0

    for url, server in matches:
        ses += 1

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

        if not url.startswith('http'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    servidor = item.server
    url = item.url

    if "/v/" in item.url:
        data = do_downloadpage(item.url)

        if 'yandex.ru' in data:
            url = item.url.split('/v/')[0]
            item.url = item.url.replace(url, 'https://fembed.com')
            url = item.url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

    if "/streaming.php?" in item.url:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<iframe id="embedvideo".*?</div>.*?src="(.*?)"')
        if 'www.googletagmanager.com' in url: url = ''

        if not url: url = scrapertools.find_single_match(data, '<li class="linkserver".*?data-video="(.*?)"')

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

    if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    if url:
        if not url.startswith("http"): url = "https:" + url

        url = url.replace("\\/", "/")

        itemlist.append(item.clone(url = url, server = servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'browse?q=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


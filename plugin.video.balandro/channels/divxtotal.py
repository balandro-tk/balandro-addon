# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, os

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www.divxtotal.re/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('divxtotal', url, post=post, headers=headers).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host, group = 'lasts', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie', tipo = 'genero' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-5/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_all', url = host, group = 'lasts', search_type = 'tvshow' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En DVDR', action = 'list_all', url = host + 'peliculas-dvdr/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'peliculas-hd-5/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 3D', action = 'list_all', url = host + 'peliculas-3-d/', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Todas<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<tbody>(.*?)</tbody>')
    if not bloque:
        if item.search_type == 'tvshow': bloque = data

    if not bloque:
        if item.group == 'lasts':
            if item.search_type == 'movie': bloque = scrapertools.find_single_match(data, '<div class="panel panel-default peliculas-bloque bloque-home">(.*?)>Series</h3>')
            else: bloque = scrapertools.find_single_match(data, '>Series</h3>(.*?)>Programas</h3>')

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')
    if not matches:
        if item.search_type == 'tvshow': matches = scrapertools.find_multiple_matches(bloque, '<div class="col-lg-3 col-md-3 col-md-4 col-xs-6">(.*?)</div>')

    if not matches:
        if item.group == 'lasts': matches = scrapertools.find_multiple_matches(bloque, '<div class="row">(.*?)</div></div>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        if not url: url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if not host in url: continue

        tipo = 'movie' if '/peliculas' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        titulo = title

        titulo = titulo.replace('(720)', '').replace('(720p)', '').replace('(1080)', '').replace('(1080p)', '').replace('(microHD)', '').replace('(BR-Line)', '').strip()
        titulo = titulo.replace('(HDR)', '').replace('(HDRip)', '').replace('(DVDRip)', '').replace('(BR-SCREENER)', '').replace('(TS-SCREENER)', '').replace('(3D)', '').strip()
        titulo = titulo.replace('4K', '').replace('4k', '').replace('(DUAL)', '').replace('[ES-EN]', '').strip()

        thumb = scrapertools.find_single_match(match, "'(.*?)'")

        if '/peliculas' in url:
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                    contentType='movie', contentTitle=titulo, infoLabels={'year': "-" } ))

        if '/series/' in url:
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            titulo = titulo.replace(' - serie', '').strip()

            itemlist.append(item.clone( action='temporadas', url=url, title=titulo, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels={'year': "-" } ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<ul class="pagination">.*?</span></a></li><li>' + "<a href='(.*?)'")

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('class="titulotemporada".*?">(.*?)</a>', re.DOTALL).findall(data)

    for tempo in temporadas:
        tempo = tempo.replace('Temporada', '').strip()

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

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '">Temporada ' + str(item.contentSeason) + '</a>(.*?)</tbody>')

    matches = scrapertools.find_multiple_matches(bloque, '<tr>(.*?)</tr>')

    i = 0

    for match in matches:
        title = scrapertools.find_single_match(match, 'title="">(.*?)</a>')

        if not title: continue

        i =+ 1

        itemlist.append(item.clone( action='findvideos', match=match, title=title, 
                                    language = 'Esp', contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = str(i) ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if item.match: data = item.match
    else: data = do_downloadpage(item.url)

    lang = ''

    if '<p>Español</p>' in data: lang = 'Esp'
    elif '<p>Latino</p>' in data: lang = 'Lat'
    elif '<p>Ingles</p>' in data: lang = 'VO'
    elif '<p>subtitulado</p>' in data: lang = 'Vose'

    qlty = scrapertools.find_single_match(data, '>Formato:.*?<p>(.*?)</p>')

    link1 = scrapertools.find_multiple_matches(data, 'class="linktorrent".*?href="(.*?)"')

    link2 = scrapertools.find_multiple_matches(data, 'class="opcion_2".*?href="(.*?)"')

    link3 =  scrapertools.find_multiple_matches(data, 'class="linktorrent".*?data-src="(.*?)"')

    links = link1 + link2 +link3


    for link in links:
         other = ''
         if not link.startswith('http'): other = 'Directo'

         itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = link, server = 'torrent',
                               language = lang, quality = qlty, other = other))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.other == 'Directo':
        item.url = host + 'download_tt.php?u=' + item.url

        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, '')
        else:
            data = do_downloadpage(item.url)

        if data:
            try:
               if 'Página no encontrada</title>' in str(data):
                   platformtools.dialog_ok('DivxTotal', '[COLOR yellow]Archivo no encontrado[/COLOR]')
                   return itemlist
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

        return itemlist

    if not item.url.endswith('.torrent'):
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'): item.url = url_base64

    if item.url.endswith('.torrent'):
        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, '')
        else:
            data = do_downloadpage(item.url)

        if data:
            try:
               if 'Página no encontrada</title>' in str(data):
                   platformtools.dialog_ok('DivxTotal', '[COLOR yellow]Archivo no encontrado[/COLOR]')
                   return itemlist
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

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

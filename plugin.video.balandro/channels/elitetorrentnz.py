# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://www.elitetorrent.nz/'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post).data
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

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/espanol/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/espanol-latino-1/' ))
    itemlist.append(item.clone( title = 'Inglés', action = 'list_all', url = host + 'idioma/ingles/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/vose/' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 720', action = 'list_all', url = host + 'calidad/720p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 1080', action = 'list_all', url = host + 'calidad/1080p/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En DVD Rip', action = 'list_all', url = host + 'calidad/dvdrip/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En HD Rip', action = 'list_all', url = host + 'peliculas-hdrip/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En Micro HD', action = 'list_all', url = host + 'peliculas-microhd/', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '<ul id="cab-categorias">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, 'href="(.*?)".*?title=.*?">(.*?)</a>')

    for url, title in matches:
        if '/animacion-2' in url: title = title + '-2'

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return sorted(itemlist,key=lambda x: x.title)


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '/?s=' in item.url:
        if '<h1>No se han encontrado resultados para' in data: return itemlist

    matches = scrapertools.find_multiple_matches(data, '<div class="imagen"(.*?)<div class="meta">')

    i = 0

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        if '/tienda/suscripcion-premium/' in url: continue

        if title == "Peso de pelicula": continue

        title = title.replace('(720)', '').replace('(720p)', '').replace('(1080)', '').replace('(1080p)', '').replace('(microHD)', '').replace('(BR-Line)', '').strip()
        title = title.replace('(HDR)', '').replace('(HDRip)', '').replace('(DVDRip)', '').replace('(BR-SCREENER)', '').replace('(TS-SCREENER)', '').strip()

        tipo = 'movie' if '/peliculas/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        thumb = host[:-1] + thumb

        qlty = scrapertools.find_single_match(match, 'style="right.*?<i>(.*?)</i>')

        lngs = []
        langs = scrapertools.find_multiple_matches(match, "data-src='.*?/images/(.*?).png'")

        for lang in langs:
            lng = ''

            if lang == 'espanol': lng = 'Esp'
            if lang == 'latino': lng = 'Lat'
            if lang == 'vose': lng = 'Vose'
            if lang == 'ingles': lng = 'Voi'

            if lng:
               if not lng in str(lngs):
                   if lng == 'Voi': lng = 'Vo'
                   lngs.append(lng)

        if '/peliculas/' in url:
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    qualities=qlty, languages = ', '.join(lngs), fmt_sufijo=sufijo,
                                    contentType='movie', contentTitle=title, infoLabels={'year': "-"} ))

        if '/series/' in url:
            if not item.search_type == 'all':
               if item.search_type == 'movie': continue

            if '-la-serie-s' in url: temp_epis = scrapertools.find_single_match(url, "-la-serie-s(.*?)$")
            elif '-serie-s' in url: temp_epis = scrapertools.find_single_match(url, "-serie-s(.*?)$")
            else: temp_epis = scrapertools.find_single_match(url, "-t(.*?)$")

            if not temp_epis:
               i +=1
               temp_epis = '99e' + str (i)

            SerieName = url

            SerieName = SerieName.replace(host, '').replace('series/', '').replace('-t' + temp_epis, '').strip()
            SerieName = SerieName.replace('-', ' ')

            temp_epis = temp_epis.replace('/', '').strip()

            season = scrapertools.find_single_match(temp_epis, "(.*?)e")
            episode = scrapertools.find_single_match(temp_epis, ".*?e(.*?)$")

            if not season or not episode: continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        qualities=qlty, languages = ', '.join(lngs), fmt_sufijo=sufijo,
                                        contentSerieName = SerieName,
                                        contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode,
                                        infoLabels={'year': "-"} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<span class="pagina pag_actual">.*?' + "<a href='(.*?)'")

        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title='Siguientes ...', url=next_url, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<div class="enlace_descarga"(.*?)</center>')

    links = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)"')

    for link in links:
        other = ''
        if 'magnet' in link: other = 'Magnet'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = link, server = 'torrent',
                              language = item.languages, quality = item.qualities, other = other))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if url.startswith('magnet:'):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    elif url.endswith(".torrent"):
        itemlist.append(item.clone( url = url, server = 'torrent' ))

    else:
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(url, host_torrent)

        if url_base64.startswith('magnet:'):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

        elif url_base64.endswith(".torrent"):
            itemlist.append(item.clone( url = url_base64, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + '?s=' + texto.replace(" ", "+") + '&x=0&y=0'
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

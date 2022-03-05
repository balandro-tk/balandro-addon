# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://elitetorrent.app/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-16-1/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'estrenos-23/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades',  search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie', tipo = 'genero' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-20-1/', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano-17-1/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/espanol-latino-11-1/' ))
    itemlist.append(item.clone( title = 'Inglés', action = 'list_all', url = host + 'idioma/ingles/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/vose-3-1/' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En 720', action = 'list_all', url = host + 'calidad/720p-2/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En 1080', action = 'list_all', url = host + 'calidad/1080p-10-1/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En DVD Rip', action = 'list_all', url = host + 'calidad/dvdrip-1/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En HD Rip', action = 'list_all', url = host + 'calidad/hdrip-1/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En Micro HD', action = 'list_all', url = host + 'peliculas-microhd-9/', search_type = 'movie' ))

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

    matches = scrapertools.find_multiple_matches(data, '<div class="imagen">(.*?)<div class="meta">')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        title = scrapertools.find_single_match(match, 'title="(.*?)"')

        if not url or not title: continue

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        qlty = scrapertools.find_single_match(match, 'style=.*?<i>(.*?)</i>')

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
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    qualities=qlty, languages = ', '.join(lngs), fmt_sufijo=sufijo,
                                    contentType='movie', contentTitle=title, infoLabels={'year': "-"} ))

        else:
            if item.search_type == 'movie': continue

            if '-la-serie-s' in url: temp_epis = scrapertools.find_single_match(url, "-la-serie-s(.*?)$")
            elif '-serie-s' in url: temp_epis = scrapertools.find_single_match(url, "-serie-s(.*?)$")
            else: temp_epis = scrapertools.find_single_match(url, "-s(.*?)$")

            if not temp_epis: continue

            SerieName = url

            SerieName = SerieName.replace(host, '').replace('series/', '').replace('-s' + temp_epis, '').strip()
            SerieName = SerieName.replace('-', ' ')

            temp_epis = temp_epis.replace('/', '').strip()

            season = scrapertools.find_single_match(temp_epis, "(.*?)e")
            episode = scrapertools.find_single_match(temp_epis, ".*?e(.*?)$")

            if not season or  not episode: continue

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

# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb

host = 'https://seriesflix.id/'

perpage = 24


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                data = httptools.downloadpage(url, post=post, headers=headers).data
        except:
            pass

    return data


def mainlist(item):
    return mainlist_series(item)

def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-series-online-gratis/' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por productora', action = 'plataformas', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>GÉNEROS<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>PRODUCTORAS<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?-title">(.*?)</span>')

    for url, title in matches:
        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article class="(.*?)</article>')
    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="([^"]+)')
        title = scrapertools.find_single_match(article, ' class="Title">(.*?)</h2>').strip()
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' data-src="([^"]+)')
        year = scrapertools.find_single_match(article, '<span class="Qlty Yr">(.*?)</span>')
        if not year: year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="Description">\s*<p>(.*?)</p>'))

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='>> Página siguiente', page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if '<nav class="wp-pagenavi">' in data:
            next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"[^>]*><i class="fa-arrow-right"></i></a>')
            if next_page:
               itemlist.append(item.clone (url = next_page, page=0, title = '>> Página siguiente', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'episodes-load">\s*<div class="Title"><a href="([^"]+)">Temporada <span>(\d+)</span>')

    for url, numtempo in matches:
        numtempo = int(numtempo)

        title = 'Temporada ' + str(numtempo)

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = url
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<tr class="Viewed">(.*?)</tr>')

    for data_epi in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(data_epi, '<a href="([^"]+)"')
        episode = scrapertools.find_single_match(data_epi, '<td><span class="Num">(\d+)</span>')
        if not url or not episode: continue

        title = scrapertools.find_single_match(data_epi, '<td class="MvTbTtl"><a [^>]+>(.*?)</a>')
        title = str(item.contentSeason) + 'x' + episode + ' ' + title

        fecha = scrapertools.find_single_match(data_epi, '<span>(.*?)</span>')
        if fecha: title = title + ' [COLOR gray](' + fecha + ')[/COLOR]'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, contentType = 'episode', contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title=">> Página siguiente", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'embed': return 'mystream'
    if servidor == 'flixplayer': return 'directo'
    return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li data-typ(?:e|)="episode"(.*?)</li>')

    ses = 0

    for match in matches:
        ses += 1

        data_key = scrapertools.find_single_match(match, 'data-key="([^"]+)"')
        data_id = scrapertools.find_single_match(match, 'data-id="([^"]+)"')

        if not data_key or not data_id: continue

        lang = scrapertools.find_single_match(match, '-language">(.*?)</p>').lower()
        lang = re.sub('[^a-z]+', '', lang)

        qlty = scrapertools.find_single_match(match, '-equalizer">(.*?)</p>')

        servidor = corregir_servidor(scrapertools.find_single_match(match, '-dns">(.*?)</p>'))

        if servidor == 'server':
            servidor = 'directo'

        url = host + '?trembed=%s&trid=%s&trtype=2' % (data_key, data_id)

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                              language = IDIOMAS.get(lang, lang), quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    data = do_downloadpage(item.url)

    url = scrapertools.find_single_match(data, '<div class="Video">.*?src="([^"]+)"')
    if not url: url = scrapertools.find_single_match(data, 'src="([^"]+)"')

    if url.startswith('/'): url = host + url[1:]

    if item.server == 'directo':
        url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')
        if url.startswith('/'): url = host + url[1:]

    if '/flixplayer.' in url:
        data = do_downloadpage(url)
        url = scrapertools.find_single_match(data, 'link":"([^"]+)"')

    elif host in url or '.seriesflix.' in url and '?h=' in url:
        fid = scrapertools.find_single_match(url, "h=([^&]+)")
        url2 = url.replace('index.php', '').split('?h=')[0] + 'r.php'

        resp = httptools.downloadpage(url2, post='h=' + fid, headers={'Referer': url}, follow_redirects=False)
        if 'location' in resp.headers: url = resp.headers['location']
        else: url = None

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)
        itemlist.append(item.clone( url = url, server = servidor ))

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

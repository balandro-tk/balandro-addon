# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, jsontools


host = "https://www.xvideos.com/"

perpage = 30


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('xvideos', url, post=post, headers=headers).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, page = 0 ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'channels-index', page = 0 ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por estrella', action = 'list_pornstars', url = host + 'pornstars-index', page = 0 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="thumb"><a href="([^"]+)".*?data-src="([^"]+)".*?title="([^"]+)"').findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a href="([^"]+)" class="no-page next-page">')

        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_all', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 250

    data = do_downloadpage(host + 'tags')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li><a href="(/tags/[^"]+)"><b>([^<]+)').findall(data)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for url, title in matches[desde:hasta]:
        titulo = title.capitalize()

        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = titulo ))

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'categorias', text_color='coral' ))

    return itemlist


def list_pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li><a href="([^"]+)" class="btn btn-default">\s*([^<]+)').findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = 'pornstars', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile(r'xv.thumbs.replaceThumbUrl\(\'<img src="([^"]+)".*?<a href="([^"]+)">([^<]+)').findall(data)

    for thumb, url, title in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a href="([^"]+)" class="no-page next-page">')
        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'pornstars', page = item.page + 1, text_color = 'coral' ))

    return itemlist

def canales(item):
    logger.info()
    itemlist = []
    
    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li><a href="(\/channels[^"]+)">([^<|\d+]+)').findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action = 'list_channels', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def list_channels(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="thumb-inside"><div class="thumb"><a href="([^"]+)">.*?xv.thumbs.replaceThumbUrl\(\'<img src="([^"]+)".*?span class="profile-name">([^<]+)'

    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        url = url if url.startswith('http') else host[:-1] + url
        url = url + 'videos/new/0' if url.endswith('/') else url + '/videos/new/0'

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, thumbnail = thumb ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            next_url = next_url.replace('&amp;', '&')

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_channels', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def list_channels_categories(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="floatLeft"><h2>([^<]+)</h2></div>'
    patron += '<div class="floatRight"><a class="seeAllButton greyButton light" href="([^"]+)'

    matches = re.compile(patron).findall(data)

    for title, url in matches:
        if 'premium' in title: continue

        itemlist.append(item.clone( action = 'list_channels_videos', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return itemlist


def list_channels_videos(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    url = item.url + 'videos/best/' if item.url.endswith('/') else item.url + '/videos/best/'

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="videos row-5-thumbs videosGridWrapper" id="showAllChanelVideos">(.*?)<\/ul>')

    matches = re.compile('<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"data-thumb_url = "([^"]+)').findall(bloque)

    for url, title, thumb, thumb2 in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb if not 'base64' else thumb2, contentType = 'movie', contentTitle = title ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            next_url = next_url.replace('&amp;', '&')

            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_channels_videos', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    try:
       m3u8url = re.findall(r"html5player\.setVideoHLS\('([^']+)'", data)[0]
    except:
       return itemlist

    data = do_downloadpage(m3u8url)

    matches = re.compile('(?i)name="([^"]+)"\s*(.*?m3u8)').findall(data)

    for calidad, url in matches:
        if not calidad or not url: continue
        url = m3u8url.replace("hls.m3u8", url)

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = calidad, url = url, language = 'VO' ))

    return sorted(itemlist, key=lambda i: i.quality)


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "?k=%s" % (texto.replace(" ", "%20"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

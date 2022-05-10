# -*- coding: utf-8 -*-

import re, base64
from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = "https://daftsex.com/"

perpage = 30


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

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color='orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, page=0 ))
    itemlist.append(item.clone( title = 'Más caliente', action = 'list_all', url = host + 'hottest'))

    itemlist.append(item.clone( title = 'Listas', action = 'listas', url = host + 'browse', page=0 ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars', page=0 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    post = {"page": item.page}
    data = httptools.downloadpage(item.url, post=post).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="video-item video([^"]+)".*?data-thumb="([^"]+)".*?div class="video-title" (?:[^"]+"){2}>([^<]+)'
    matches = re.compile(patron).findall(data)

    for video_id, thumb, title in matches:
        url = 'https://daftsex.com/watch/%s' % (video_id)
        itemlist.append(item.clone( action = 'findvideos', url = url,
                                    title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li><a href="([^"]+)" title="Next page"')
        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', url= host + next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_all', page = item.page + 1, text_color = 'coral' ))
        else:    
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def listas(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<div class="video-title" (?:[^"]+"){2}>([^<]+)'
    patron += '.*?a href="([^"]+).*?data-thumb="([^"]+)"'

    matches = re.compile(patron).findall(data)
    for title, url, thumb in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url,
                                    thumbnail = thumb if thumb.startswith('http') else host[:-1] + thumb, title = title))
    if itemlist:
        patron = '<li><a href="([^"]+)" title="Next page"'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'listas', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'categories').data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
    patron = '<div class="video-item"><a href="([^"]+)".*?data-thumb="([^"]+)".*?<div class="video-title">([^<]+)'
    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        url = host + url if not url.startswith('/') else host[:-1] + url
        thumb = host + thumb if not url.startswith('/') else host[:-1] + thumb
        itemlist.append(item.clone( action = 'list_all', url = url, title = title, thumbnail = thumb ))

    return sorted(itemlist, key=lambda i: i.title)


def pornstars(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="pornstar"><a href="([^"]+)"><div class="[^"]+">'
    patron += '<div class="lazy thumb" data-thumb="([^"]+)"></div></div><span>([^<]+)'
    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url,
                                    thumbnail = thumb if thumb.startswith('http') else host[:-1] + thumb, title = title))
    if itemlist:
        patron = '<li><a href="([^"]+)" title="Next page"'
        next_url = scrapertools.find_single_match(data, patron)
        if next_url:
            next_url = next_url.replace('&amp;', '&')
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'pornstars', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    hash = scrapertools.find_single_match(data, 'hash:\s*"([^"]+)"')
    color = scrapertools.find_single_match(data, 'color:\s*"([^"]+)"')
    url = 'https://daxab.com/player/%s?color=%s'  % (hash, color)

    headers = {'Referer': item.url}
    data = httptools.downloadpage(url, headers=headers).data

    id = scrapertools.find_single_match(data, 'id:\s*"([^"]+)"')
    id1, id2 = id.split('_')

    srv =  scrapertools.find_single_match(data, 'server:\s*"([^"]+)')[::-1]
    srv = base64.b64decode(srv).decode('utf-8')
    srv = "https://%s" % srv

    patron = '"mp4_\d+":"(\d+).([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for qlty, url in matches:
        url = '%s/videos/%s/%s/%s.mp4?extra=%s' % (srv, id1, id2, qlty, url)
        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = qlty, url = url, language = 'VO' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "video/%s" % (texto.replace(" ", "%20"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

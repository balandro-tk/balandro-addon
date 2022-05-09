# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.youngpornvideos.com/'


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

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'videos/straight/all-popular.html' ))

    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = host + 'videos/straight/all-recent.html' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'videos/straight/all-view.html' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'videos/straight/all-rate.html' ))

    itemlist.append(item.clone( title = 'Long play', action = 'list_all', url = host + 'videos/straight/all-length.html' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'categorias', url = host + 'channels/', group = 'canales' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias', url = host + 'categories/', group = 'categorias' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars/' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    if item.group == 'canales':
        data = scrapertools.find_single_match(data, '<div class="thumb-list(.*?)</section>')

        matches = re.compile('<div class="thumb-ratio">.*?href="(.*?)".*?src="(.*?)".*?title=.*?>(.*?)</a>', re.DOTALL).findall(data)
    else:
        data = scrapertools.find_single_match(data, '<div class="thumb-list(.*?)<h1>Community</h1>')

        matches = re.compile('<div class="thumb-ratio">.*?href="(.*?)".*?src="(.*?)".*?title="(.*?)"', re.DOTALL).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb) )

    if item.group == 'canales':
        return sorted(itemlist, key=lambda x: x.title)

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    data = scrapertools.find_single_match(data, '<div id="straightcat" class="thumb-list ac"(.*?)<!-- alphabetical -->')

    matches = re.compile('<div class="outer-item-pics".*?id="(.*?)".*?href="(.*?)".*?src="(.*?)"', re.DOTALL).findall(data)

    for title, url, thumb in matches:
        itemlist.append(item.clone (action='list_all', title=title, url=url, thumbnail=thumb) )

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>', '', data)

    patron = '<div class="thumb-ratio">.*?<a href="(.*?)".*?src="(.*?)".*?alt="(.*?)"'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for url, thumb, title in matches:
        itemlist.append(item.clone (action='findvideos', title=title, url=url, thumbnail=thumb, contentType = 'movie', contentTitle = title) )

    if itemlist:
        bloque = scrapertools.find_single_match(data,'<div class="pagination _767p">(.*?)<div class="pagination _768plus">')

        if bloque:
            if '<a class="active">' in bloque:
                next_page = scrapertools.find_single_match(data,'<a class="active">.*?href="(.*?)"')
            else:
                next_page = scrapertools.find_single_match(data,'">.*?<a href="(*?)"')

            if next_page:
                if not next_page == item.url:
                    itemlist.append(item.clone (action='list_all', title='Siguientes ...', url=next_page, text_color = 'coral') )

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    m3u = scrapertools.find_single_match(data, 'file: "([^"]+)"')

    if m3u:
        data = httptools.downloadpage(m3u).data

        matches = re.compile('RESOLUTION=\d+x(\d+),.*?(index-.*?).m3u8', re.DOTALL).findall(data)

        for qlty, url in matches:
            url = m3u.replace("master", url)

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, quality = qlty, language = 'VO' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + 'search/video/%s' % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

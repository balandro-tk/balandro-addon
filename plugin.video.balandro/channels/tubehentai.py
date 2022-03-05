# -*- coding: utf-8 -*-

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = "https://tubehentai.com/"

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

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'most-recent/'))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'most-viewed/'))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'top-rated/'))
    itemlist.append(item.clone( title = 'Long play', action = 'list_all', url = host + 'longest/' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias'))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<a href="((?:http|https)://tubehentai.com/video/[^"]+)" title="([^"]+)".*?<span>([^<]+)</span>.*?<img src="([^"]+)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title, duration, thumb in matches:
        titulo = "[COLOR tan]%s[/COLOR] %s" % (duration, title)
                             
        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb, contentType = 'movie', contentTitle = title ))

    next_page = scrapertools.find_single_match(data,'<a href=\'([^\']+)\' class="next"')

    if next_page:
        next_page = host + next_page

        itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host + 'channels/').data

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="videobox.*?<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)".*?</div>'

    matches = re.compile(patron).findall(data)

    for url, thumb, title in matches:
        if title == 'Photos': continue

        title = title.capitalize()

        itemlist.append(item.clone( action = 'list_all', url = url, title = title, thumbnail = thumb ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '<source src="([^"]+\.mp4)"')
    if not url:
        url = scrapertools.find_single_match(data, '<div class="videohere".*?src="([^"]+)"')

    if url:
        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = 'VOS' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "search/videos/%s/" % (texto.replace(" ", "-"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

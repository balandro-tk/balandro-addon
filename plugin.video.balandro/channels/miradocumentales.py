# -*- coding: utf-8 -*-

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, servertools


host = "https://miradocumentales.com/"


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<div class="categorias_side(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, ' href="([^"]+)">([^<]+)')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title = title, url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div class="mini_img">(.*?)<hr>')

    for article in matches:
        url, title = scrapertools.find_single_match(article, ' href="([^"]+)" title="([^"]+)')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="contenido_extracto_index">(.*?)<div')).strip()

        # entradas que no contienen vídeos
        if plot == '': continue
        elif title == 'La guía definitiva para crear un negocio exitoso en Internet': continue
        elif title == 'Ventajas y desventajas de las criptomonedas que necesitas conocer': continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, plot=plot, 
                                    contentType='movie', contentTitle=title, contentExtra='documentary' ))

    next_page_link = scrapertools.find_single_match(data, '<a href="([^"]+)">Pr&oacute;xima')
    if next_page_link:
        itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    url = scrapertools.find_single_match(data, '<p><iframe src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '<p><iframe.*? src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '<div class="single_player">\s*<iframe.*? src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '<div class="single_player">\s*<a href="([^"]+)')

    if not url: url = scrapertools.find_single_match(data, '<p>\[\w+\]([^\[]+)') #Ex: <p>[vimeo]https://vimeo.com/...[/vimeo]</p>

    if url:
        url = url.replace('&#038;', '&').replace('&amp;', '&')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = 'Esp' ))

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

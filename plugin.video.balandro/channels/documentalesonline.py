# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools


host = "https://www.documentales-online.com"

perpage = 25


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_top', url = host + '/populares/', grupo = 'Populares' ))
    itemlist.append(item.clone( title = 'Top 100', action = 'list_top', url = host +'/top/', grupo = 'Top 100' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por tema', action = 'series', url = host + '/series-temas/' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<ul class="sub-menu">(.*?)</ul>')

    patron = ' href="([^"]+)">([^<]+)'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, title in matches:
        if url.startswith('/'): url = host + url

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def series(item):
    logger.info()
    itemlist = []

    perpage = 100

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, 'Populares</a>.*?Series / Temas(.*?)</article>')

    patron  = '<a href="(.*?)".*?>(.*?)</a>'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    num_matches = len(matches)

    for url, title in matches[item.page * perpage:]:
        url = host + url
        title = title.split("<")[0].capitalize()

        itemlist.append(item.clone( action='list_videos', url=url, title=title ))

        if len(itemlist) >= perpage: break

    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='series', text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for article in matches:
        url, title = scrapertools.find_single_match(article, '<h2 class="entry-title"><a href="([^"]+)".*?>(.*?)</a>')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<p>(.*?)</p>'))

        if '/series-temas/' in url: continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, plot=plot,
                                    contentType='movie', contentTitle=title, contentExtra='documentary' ))

    next_page_link = scrapertools.find_single_match(data, '<span aria-current="page" class="page-numbers current">.*?href="(.*?)"')
    if next_page_link:
        itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def list_top(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, 'Populares</a>.*?%s(.*?)>Última revisión' % item.grupo)

    patron  = '<a href="(.*?)".*?>(.*?)</a>'
    matches = scrapertools.find_multiple_matches(bloque, patron)

    num_matches = len(matches)

    for url, title in matches[item.page * perpage:]:
        title = title.split("<")[0]

        itemlist.append(item.clone( action='findvideos', url=url, title=title, contentType='movie', contentTitle=title, contentExtra='documentary' ))

        if len(itemlist) >= perpage: break

    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_top', text_color='coral' ))

    return itemlist


def list_videos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = 'Populares</a>(.*?)</div></article></div></div>'
    data = scrapertools.find_single_match(data, patron)

    patron = 'href="([^"]+).*?src="([^"]+).*?bookmark">([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title in matches:
        title = title.replace("&#8211;","-").strip()
        if not title: continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                    contentType='movie', contentTitle=title, contentExtra='documentary' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<iframe.*?src="(http[^"]+)')

    ses = 0

    i = 0

    num_matches = len(matches)

    for url in matches:
        ses += 1

        if 'amazon-adsystem.com' in url:
            if num_matches == 1:
                url = scrapertools.find_single_match(data, '<param name="src" value="(.*?)"')
                if not url: continue
            else:
                num_matches = num_matches - 1
                continue

        url = url.replace('&amp;', '&')

        other = ''
        if num_matches > 1:
            i += 1
            other = str(i)

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor and servidor != 'directo':
            itemlist.append(Item( channel = item.channel, action = 'play', server=servidor, title = '', url = url, language = 'Esp', other = other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

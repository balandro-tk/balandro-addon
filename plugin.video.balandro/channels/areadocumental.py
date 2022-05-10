# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools


host = "https://www.area-documental.com/"


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'resultados-reciente.php?buscar=&genero=' ))

    itemlist.append(item.clone( title = 'Destacados', action = 'list_all', url = host + 'resultados.php?buscar=&genero=' ))
    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host +'resultados-visto.php?buscar=&genero=' ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))
    itemlist.append(item.clone( title = 'Por fecha', action = 'list_all', url = host + 'resultados-anio.php?buscar=&genero=' ))
    itemlist.append(item.clone( title = 'Por alfabético', action = 'list_all', url = host +'resultados-titulo.php?buscar=&genero=' ))

    itemlist.append(item.clone( title = 'En 3D', action = 'list_all', url = host + '3D.php' ))

    itemlist.append(item.clone( title = 'Series', action = 'list_all', url = host + 'series.php' ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    patron = '<a href="(resultados[^"]+)" class="dropdown-toggle" data-toggle="dropdown">([^<]+)'
    matches = scrapertools.find_multiple_matches(data, patron)

    for url, title in matches:
        patron = '<li><a href="%s">TODO</a></li>(.*?)</ul>' % url.replace('?', '\?')
        bloque = scrapertools.find_single_match(data, patron)
        subitems = scrapertools.find_multiple_matches(bloque, '<li><a href="[^"]+">([^<]+)')

        itemlist.append(item.clone( action='subcategorias', title=title.strip(), url=host + url, subitems=subitems, plot=', '.join(subitems) ))

    return itemlist

def subcategorias(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='list_all', title='Todo ' + item.title, url=item.url ))

    for subgenero in item.subitems:
        itemlist.append(item.clone( action='list_all', title=subgenero, url=host+'resultados.php?genero=&buscar='+subgenero.replace(' ', '+') ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<a class="hvr-shutter-out-horizontal" href="([^"]+)"><img (?:data-|)src="([^"]+)" alt="([^"]+)"'
    patron += '.*?&nbsp;&nbsp;&nbsp;(\d+| ).*?<div class="comments-space">(.*?)</div>'
    matches = scrapertools.find_multiple_matches(data, patron)

    for url, thumb, title, year, plot in matches:
        thumb = host + thumb
        plot = scrapertools.htmlclean(plot).strip()

        if 'player.php' not in url:
            titulo = '%s [COLOR gray](%s)[/COLOR]' % (title, year)
            itemlist.append(item.clone( action='list_all', url=url, title=titulo, thumbnail=thumb, plot=plot ))
        else:
            itemlist.append(item.clone( action='findvideos', url=host+url, title=title, thumbnail=thumb,
                                        infoLabels={"year": year, "plot": plot}, contentType='movie', contentTitle=title, contentExtra='documentary' ))

    next_page_link = scrapertools.find_single_match(data, '<li><a class="last">\d+</a></li>\s*<li>\s*<a href="([^"]+)')
    if next_page_link != '':
        if next_page_link.startswith('?'): 
            if 'series.php' in item.url: next_page_link = host + 'series.php' + next_page_link
            else: next_page_link = host + 'index.php' + next_page_link
        else: next_page_link = host + next_page_link[1:]

        next_page_link = next_page_link.replace('&amp;', '&')
        itemlist.append(item.clone( title='Siguientes ...', action='list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'file:\s*"([^"]+)",.*?label: "([^"]*)"')

    ses = 0

    for url, lbl in matches:
        ses += 1

        if '.mp4' not in url and url != 'video.php' and url != 'videoHD.php' and url != 'video3Dfull.php': continue

        if url in ['video.php', 'videoHD.php', 'video3Dfull.php']:
            url = host + url + '|Referer=' + item.url 
            url += '&Cookie=' + httptools.get_cookies('www.area-documental.com')

        sub_url = scrapertools.find_single_match(data, 'file:\s*"/(webvtt/[^"]+)"')

        lang = 'Vose'
        if 'videoHD.php' in url:
            sub_url = sub_url.replace('spa', 'eng')
            lang = 'VO'

        sub_url = host + sub_url + '|Referer=' + item.url

        itemlist.append(Item( channel = item.channel, action = 'play', server='directo', title = '', url = url, 
                              language = lang, quality = lbl, subtitle = sub_url ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'resultados.php?genero=&buscar=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

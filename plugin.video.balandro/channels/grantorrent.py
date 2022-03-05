# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, base64

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters

host = 'https://grantorrent.ch/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['http://grantorrent.net/', 'https://grantorrent1.com/', 'https://grantorrent.one/', 
                 'https://grantorrent.tv/', 'https://grantorrent.la/', 'https://grantorrent.io/', 'https://grantorrent.eu/',
                 'https://grantorrent.cc/', 'https://grantorrent.li/', 'https://grantorrent.online/', 'https://grantorrentt.com/',
                 'https://grantorrent.nl/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ data = httptools.downloadpage(url, post=post).data
    data = httptools.downloadpage_proxy('grantorrent', url, post=post).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post).data
                data = httptools.downloadpage_proxy('grantorrent', url, post=post).data
        except:
            pass

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = {
        'accion': 'Acción',
        'animacion': 'Animación',
        'aventura': 'Aventura',
        'biografia': 'Biografía',
        'ciencia-ficcion': 'Ciencia ficción',
        'comedia': 'Comedia',
        'crimen': 'Crimen',
        'deporte': 'Deporte',
        'documental': 'Documental',
        'drama': 'Drama',
        'familia': 'Familia',
        'fantasia': 'Fantasía',
        'guerra': 'Guerra',
        'historia': 'Historia',
        'misterio': 'Misterio',
        'musica': 'Música',
        'romance': 'Romance',
        'suspense': 'Suspense',
        'terror': 'Terror',
        'western': 'Western'
        }

    for opc in sorted(opciones):
        itemlist.append(item.clone( title=opciones[opc], url=host + 'categoria/' + opc + '/', action='list_categ_search' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='En 4K', url=host + 'categoria/4k-2/', action='list_categ_search' ))
    itemlist.append(item.clone( title='En BluRay', url=host + 'categoria/BluRay-1080p/', action='list_categ_search' ))
    itemlist.append(item.clone( title='En Dvd Rip', url=host + 'categoria/dvdrip/', action='list_categ_search' ))
    itemlist.append(item.clone( title='En HD Rip', url=host + 'categoria/HDRip-2/', action='list_categ_search' ))
    itemlist.append(item.clone( title='En Micro HD', url=host + 'categoria/MicroHD-1080p/', action='list_categ_search' ))
    itemlist.append(item.clone( title='En 3D', url=host + 'categoria/3D/', action='list_categ_search' ))

    return itemlist


def detectar_idioma(img):
    if 'icono_espaniol.png' in img: return 'Esp'
    else: return 'VO' # !?


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<div class="imagen-post">(.*?)<div class="bloque-superior">(.*?)<div class="bloque-inferior">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for b_main, b_sup, b_inf in matches:
        url = scrapertools.find_single_match(b_main, ' href="([^"]+)')
        title = b_inf.strip()
        if not url or not title: continue

        thumb = scrapertools.find_single_match(b_main, ' src="(http[^"]+)')
        lang = detectar_idioma(b_sup)
        qlty = scrapertools.find_single_match(b_sup, '^([^<]*)').strip()

        if qlty == 'Promocion': continue

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
    if next_page_link:
        itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page_link, text_color='coral' ))

    return itemlist


def list_categ_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<div class="imagen-post">\s*<a href="([^"]+)".*?<img src="([^"]+)"'
    patron += '.*?</a>\s*<div class="bloque-inferior">([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, thumb, title in matches:
        title = title.strip()

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, 
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)')
    if next_page_link:
        itemlist.append(item.clone( title='Siguientes ...', url=next_page_link, action='list_categ_search', text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.lower().replace(' ', '').replace('-', '')
    orden = ['3d', 'screener', 'screener720p', 'hdscreener', 'brscreener', 'avi', 'mkv', 'dvdrip', 'hdrip', 'bluray720p', 'microhd', 'microhd1080p', '1080p', 'bluray1080p', 'fullbluray1080p', 'bdremux1080p', '4k', 'full4k', '4kuhdrip', '4kfulluhd', '4kuhdremux', '4kuhdremux1080p', '4khdr']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<tr class="lol">.*?<noscript>.*?<noscript>.*?<img src="(.*?)".*?</noscript></td><td>(.*?)</td><td>(.*?)</td>.*?href="(.*?)"'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if not matches:
        patron = '<tr class="lol">\s*<td><img ([^>]*)>.*?</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td><a class="link".*?href="([^"]+)'
        matches = re.compile(patron, re.DOTALL).findall(data)

    if not matches:
        patron = '<tr class="lol">\s*<td><img ([^>]*)>.*?</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td><a class="link".*?onclick="([^"]+)'
        matches = re.compile(patron, re.DOTALL).findall(data)

    ses = 0

    for lang, quality, peso, onclick in matches:
        ses += 1

        if onclick.startswith('http'): url = onclick
        else:
            post = scrapertools.find_single_match(onclick, "u:\s*'([^']+)")
            if not post: post = scrapertools.find_single_match(onclick, "u=([^'\"&]+)")
            if not post: continue

            try:
                url = base64.b64decode(post)
            except:
                continue

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'torrent',
                              language = detectar_idioma(lang), quality = quality, quality_num = puntuar_calidad(quality), other = peso ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if not item.url.endswith('.torrent'):
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'):
           if not url_base64.startswith('https://files.'): url_base64 = url_base64.replace(host, 'https://files.grantorrent.ch/' )
           item.url = url_base64

    if item.url.endswith('.torrent'):
        if config.get_setting('proxies', item.channel, default=''):
            if PY3:
                from core import requeststools
                data = requeststools.read(item.url, 'grantorrent')
            else:
                data = do_downloadpage(item.url)

            if data:
                import os

                file_local = os.path.join(config.get_data_path(), "temp.torrent")
                with open(file_local, 'wb') as f: f.write(data); f.close()

                itemlist.append(item.clone( url = file_local, server = 'torrent' ))
        else:
            itemlist.append(item.clone( url = item.url, server = 'torrent' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_categ_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

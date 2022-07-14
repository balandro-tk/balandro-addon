# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, base64

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb

from lib import decrypters


host = 'https://grantorrent.si/'

b64_host = 'grantorrent.si'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['http://grantorrent.net/', 'https://grantorrent1.com/', 'https://grantorrent.one/',
                 'https://grantorrent.tv/', 'https://grantorrent.la/', 'https://grantorrent.io/', 'https://grantorrent.eu/',
                 'https://grantorrent.cc/', 'https://grantorrent.li/', 'https://grantorrent.online/', 'https://grantorrentt.com/',
                 'https://grantorrent.nl/', 'https://grantorrent.ch/', 'https://grantorrent.ac/', 'https://grantorrent.re/'
                 'https://grantorrent.se/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ timeout 13/7/2022
    timeout = 15

    if '/?query' in url: timeout = 30
    elif '/categoria/' in url: timeout = 30

    headers = {'Referer': host}
   
    # ~ data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    data = httptools.downloadpage_proxy('grantorrent', url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                data = httptools.downloadpage_proxy('grantorrent', url, post=post, headers=headers, timeout=timeout).data
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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

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
        itemlist.append(item.clone( title = opciones[opc], url = host + 'categoria/' + opc + '/', action ='list_all' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'peliculas/')

    patron = '<select\s*id="quality"\s*name="quality"[^>]*>(.*?)<\/select><\/div>'

    bloque = scrapertools.find_single_match(data, patron)

    patron = '<option\s*value="([^"]+)">([^<]+)<\/option>'
    matches = re.compile('<option\s*value="([^"]+)">([^<]+)<\/option>', re.DOTALL).findall(bloque)

    for url, title in matches:
        title = title.strip()

        url = host + 'peliculas/?query&quality=' + title

        if '4k' in title.lower(): url = url.replace('4k', '4k-2')
        elif 'hdrip' in title.lower(): url = url.replace('HDRip', 'HDRip-2')

        itemlist.append(item.clone( title=title, url=url, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="relative my-5 md:my-4">(.*?)</p></div></div>', re.DOTALL).findall(data)

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, ' src="(http[^"]+)')

        lang = 'Esp'

        qlty = scrapertools.find_single_match(match, ' text-center">.*?<span>(.*?)</span>')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages=lang, qualities=qlty,
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, "<span aria-current='page'>.*?<a href='(.*?)'")
        if next_page:
            if '/page/' in next_page:
                next_page = next_page.replace('&#038;', '&')

                itemlist.append(item.clone( title='Siguientes ...', action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    txt = txt.lower().replace(' ', '').replace('-', '')
    orden = ['3d',
             'screener',
             'screener720p',
             'hdscreener',
             'brscreener',
             'avi',
             'mkv',
             'dvdrip',
             'hdrip',
             '720p',
             'bluray720p',
             'microhd',
             'microhd1080p',
             '1080p',
             'bluray1080p',
             'fullbluray1080p',
             'bdremux1080p',
             '4k', 'full4k',
             '4kuhdrip',
             '4kfulluhd',
             '4kuhdremux',
             '4kuhdremux1080p',
             '4khdr']

    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('>Download<.*?href="(.*?)"', re.DOTALL).findall(data)

    for url in matches:
        if not url.endswith('.torrent'):
            if not '/s.php' in url: continue

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', url = url, server = 'directo',
                              language = item.languages, quality = item.qualities, quality_num = puntuar_calidad(item.qualities) ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if not item.url.endswith('.torrent'):
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'):
           if not url_base64.startswith('https://files.'): url_base64 = url_base64.replace(host, 'https://files.' + b64_host + '/' )
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
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

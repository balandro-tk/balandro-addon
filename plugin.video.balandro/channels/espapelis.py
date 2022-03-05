# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.espapelis.com/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/fecha/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', page = 1, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host, group = 'masd', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    generos = [
       'accion',
       'animacion',
       'aventura',
       'biografia',
       'comedia',
       'crimen',
       'documental',
       'drama',
       'familia',
       'guerra',
       'historia',
       'misterio',
       'romance',
       'suspense',
       'terror',
       'western'
       ]

    for genero in generos:
        url = host + 'category/' + genero + '/'

        itemlist.append(item.clone( action = 'list_all', title = genero.capitalize(), url = url, page = 1 ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1978, -1):
        url = host + 'peliculas/fecha/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all', page = 1 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist=[]

    if item.post:
        data = do_downloadpage(item.url, item.post)
    else:
        data = do_downloadpage(item.url)

    if not item.group:
        bloque = data
    else:
        bloque = scrapertools.find_single_match(data, '<div class="grid popular">(.*?)</section>')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>').strip()

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if not item.group:
        if itemlist:
            if '"load-more-ajax"' in data:
               url = host + 'wp-admin/admin-ajax.php'
               next_page = item.page + 1
               post = {'action': 'action_load_pagination_home', 'number': 18, 'paged': next_page, 'postype': 'movie'}

               itemlist.append(item.clone( title = 'Siguientes ...', url = url, post = post, action = 'list_all', page = next_page, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<li data-playerid="(.*?)".*?/flags/(.*?).png.*?<span style.*?>(.*?)</span>')

    ses = 0

    for url, lang, qlty in matches:
        ses += 1

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
        elif '/gounlimited.' in url: continue
        elif '/jetload.' in url: continue
        elif '/vidcloud.' in url: continue
        elif '.mystream.' in url: continue

        if lang == 'es': lang = 'Esp'
        elif lang == 'la': lang = 'Lat'
        elif lang == 'mx': lang = 'Lat'

        if '//mega.' in url:
            servidor = 'mega'
            if '/embed#!#!' in url: url = url.replace('/embed#!#!', '/embed#!')
        else:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(Item(channel = item.channel, action = 'play', title = '', server = servidor, url = url,
                        language = lang, quality = qlty ))

    # Descargas
    matches = scrapertools.find_multiple_matches(data, '<span class="num">#.*?</span>(.*?)</td><td>(.*?)</td><td><span>(.*?)</span>.*?href="(.*?)"')

    for srv, lang, qlty, url in matches:
        ses += 1

        srv = srv.replace('.net', '').replace('.com', '').replace('.nz', '').replace('.to', '').strip().lower()

        if srv == 'turbobit': continue
        elif srv == '1fichier': continue

        if lang == 'Castellano': lang = 'Esp'
        elif lang == 'Latino': lang = 'Lat'

        if srv == 'bittorrent': servidor = 'torrent'
        elif srv == 'mega': servidor = 'mega'
        else:
           servidor = servertools.get_server_from_url(url)
           servidor = servertools.corregir_servidor(servidor)

           url = servertools.normalize_url(servidor, url)

        other = 'D'
        if not srv == servidor:
            other = srv + ' d'

        itemlist.append(Item(channel = item.channel, action = 'play', title = '', server = servidor, url = url,
                        language = lang, quality = qlty, other = other))

    itemlist = servertools.get_servers_itemlist(itemlist)

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if 'D' in item.other or ' d' in item.other:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, 'url=(.*?)"')

        if not url:
            new_url = scrapertools.find_single_match(data, 'href="(.*?)"')
            if new_url:
               if '/short/' in new_url:
                   data = do_downloadpage(new_url)
                   url = scrapertools.find_single_match(data, 'url=(.*?)"')

        if url:
            if '/%23!' in url:
                url = url.replace('/%23!%23!', '/#!').replace('/%23!', '/#!')

            if '//pelistop.co/' in url:
                url = url.replace('//pelistop.co/', '//streamsb.net/')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone( url = url, server = servidor ))

    else:
        itemlist.append(item.clone( url = item.url, server = item.server ))

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

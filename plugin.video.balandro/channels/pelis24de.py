# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://pelis24.de/'


perpage = 30


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/peliculas/fecha/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    return data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = host, group = 'desta', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    opciones = [
       ('accion', 'Acción'),
       ('animacion', 'Animación'),
       ('aventura', 'Aventura'),
       ('belica', 'Bélica'),
       ('ciencia-ficcion', 'Ciencia ficción'),
       ('comedia', 'Comedia'),
       ('crimen', 'Crimen'),
       ('documental', 'Documental'),
       ('drama', 'Drama'),
       ('familia', 'Familia'),
       ('fantasia', 'Fantasía'),
       ('historia', 'Historia'),
       ('misterio', 'Misterio'),
       ('musica', 'Música'),
       ('Película de TV', 'pelicula-de-tv'),
       ('romance', 'Romance'),
       ('sci-fi-fantasy', 'Sci-Fi & Fantasy'),
       ('suspense', 'Suspense'),
       ('terror', 'Terror'),
       ('western', 'Western')
    ]

    for opc, tit in opciones:
        itemlist.append(item.clone( title=tit, url= host + 'category/' + opc + '/', action = 'list_all' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1922, -1):
        url = host + 'peliculas/fecha/' + str(x) + '/'

        itemlist.append(item.clone( title=str(x), url=url, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = data

    if item.group == 'desta': bloque = scrapertools.find_single_match(data, '<div class="grid popular">(.*?)</section>')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        title = scrapertools.find_single_match(article, '<div class="entry-title">(.*?)</div>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, '-src="(.*?)"')

        itemlist.append(item.clone( action='findvideos', url=url, title = title, thumbnail = thumb,
                                    contentType='movie', contentTitle=title, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if num_matches < perpage: return itemlist

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='Siguientes ...', url= item.url, page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if item.group == 'desta': return itemlist

    if buscar_next:
       if itemlist:
           if not '/page/' in item.url:
               next_pagina = 2
               current_url = item.url
           else:
               current_url = scrapertools.find_single_match(item.url, '(.*?)/page/')
               next_pagina = scrapertools.find_single_match(item.url, '.*?/page/(.*?)/')

               next_pagina = int(next_pagina)
               next_pagina +=1

           next_page = current_url + '/page/' + str(next_pagina) + '/' 

           itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', page=0, text_color='coral' ))


    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<li data-playerid=(.*?)</a></li>')

    for match in matches:
        url = scrapertools.find_single_match(match, '"(.*?)"')

        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
        elif 'embed.' in url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if 'Castellano' in match: lang = 'Esp'
        elif 'Latino"' in match: lang = 'Lat'
        elif 'Subtitulado' in match:  lang = 'Vose'
        else: lang = 'Lat'

        qlty = 'HD'

        other = ''
        if servidor == 'directo':
            if '//pelistop' in url: other = 'Pelistop'
            elif '/fembed/?h=' in url: other = 'Fembed'
            elif '/dood.' in url: other = 'Dood'

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url,
                              language = lang, quality = qlty, other = other ))

    # ~ downloads recatpcha

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')
    item.url = item.url.replace('amp;#038;', '&').replace('#038;', '&').replace('amp;', '&')

    url = item.url

    if item.other == 'Pelistop':
        if 'url=' in item.url:
            fid = scrapertools.find_single_match(item.url, "url=(.*?)$")
            api_url = 'https://api.cuevana3.me/ir/redirect_ddh.php'
            api_post = 'url=' + fid

            resp = httptools.downloadpage(api_url, post=api_post, headers={'Referer': item.url}, follow_redirects=False, only_headers=True)

            url = ''

            if 'location' in resp.headers: 
                url = resp.headers['location']

                if url.startswith('//'): url = 'https:' + url

        else:
            data = do_downloadpage(item.url)

            url = scrapertools.find_single_match(data, '>Ver ahora<.*?src="(.*?)"')
            url = url.replace('//pelistop.co/', '//streamsb.net/')

    elif item.other == 'Fembed':
        hash = scrapertools.find_single_match(item.url, "h=(.*?)$")

        data = do_downloadpage('https://api.cuevana3.me/fembed/api.php', post={'h': hash})

        url = scrapertools.find_single_match(data, '"url":"(.*?)"')

    if url:
        url = url.replace('\\/', '/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))

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

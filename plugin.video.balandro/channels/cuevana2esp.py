# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://cuevana2espanol.com/'

perpage = 25


def do_downloadpage(url, post=None, headers=None, follow_redirects=True, only_headers=False, raise_weberror=True):
    resp = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers, raise_weberror=raise_weberror)

    if only_headers: return resp.headers

    return resp.data


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-pelicula-online/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'calificaciones/', search_type = 'movie' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="poster">(.*?)</article>').findall(data)
    if not matches: matches = re.compile('<article>(.*?)</article>').findall(data)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, ' href="(.*?)"')
        title = scrapertools.find_single_match(article, ' alt="(.*?)"').strip()
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="(.*?)"')
        year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        if not year: year = '-'

        if '/es.png' in article: lang = 'Esp'
        else: lang = '?'

        plot = scrapertools.find_single_match(article, '<p>(.*?)</p>')

        itemlist.append(item.clone( action='findvideos', url = url, title = title, thumbnail = thumb, languages = lang,
                                            contentType = 'movie', contentTitle = title, infoLabels = {'year': year, 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_url = scrapertools.find_single_match(data, '''<a class='arrow_pag' href="([^"]+)"''')
        if next_url:
            itemlist.append(item.clone( title='Siguientes ...', url=next_url, page=0, action='list_all', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    lng = 'Esp'

    data = do_downloadpage(item.url)

    matches = re.compile('<li><a class="options" href="#(.*?)">.*?</b>(.*?)</a>', re.DOTALL).findall(data)

    ses = 0

    for opt, srv in matches:
        ses += 1

        srv = srv.replace(' Servidor ', '').lower().strip()

        if srv:
            if srv == 'hqq' or srv == 'cuevana2espanol' or srv == 'raptu' or srv == 'vid' or srv == 'youtube': continue

            url = scrapertools.find_single_match(data, '<div id="' + opt + '".*?src="(.*?)"')

            if url.startswith('/'): url = 'https:' + url

            itemlist.append(Item( channel = item.channel, action = 'play', other = srv, server = '', title = '', url = url, referer = item.url, language = lng ))

    bloque = scrapertools.find_single_match(data, '<div id="downloads" class="sbox">(.*?)</div>')

    matches = re.compile('<img src=.*?domain=(.*?)".*?<a href="(.*?)".*?<td>(.*?)</td>', re.DOTALL).findall(bloque)

    for dom, url, qlty in matches:
        ses += 1

        dom = dom.replace('.com', '').replace('.net', '').replace('.to', '').replace('.cc', '').replace('.nz', '').lower().strip()

        if dom == 'filefactory': continue
        elif dom == '1fichier': continue

        itemlist.append(Item( channel = item.channel, action = 'play', other = dom, server = '', title = '', url = url, referer = item.url, language = lng ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    player = 'https://player.cuevana2espanol.com/'

    url = ''

    if '/sc/' in item.url:
        hash = item.url.replace(player + 'sc/?h=', '')
        post = {'h': hash}

        url = do_downloadpage(player + 'sc/r.php', post = post, follow_redirects = False, only_headers = True).get('location', '')

    elif '/irgoto.php' in item.url:
        headers = {'Referer': host}

        data = do_downloadpage(item.url, headers = headers)
        url = scrapertools.find_single_match(data, "location.href='(.*?)'")

        if 'goto.php' in url:
            if url.startswith('goto.php'): url = player + url

            data = do_downloadpage(url, headers = headers)

            if 'action="r.php"' in data:
                value = scrapertools.find_single_match(data, 'value="(.*?)"')
                post = {'url': value, 'sub': ''}

                if value:
                    url = do_downloadpage(player + 'r.php', post = post, follow_redirects=False, only_headers=True).get('location', '')
            else:
                url = do_downloadpage(url, follow_redirects=False, only_headers=True).get('location', '')

    elif '/index.php' in item.url:
        headers = {'Referer': host}

        data = do_downloadpage(item.url, headers = headers)
        hash = scrapertools.find_single_match(data, 'config_player.link = "(.*?)"')

        if hash:
            post = {'link': hash}
            url = do_downloadpage(player + 'plugins/gkpluginsphp.php', post = post, follow_redirects=False, only_headers=True, raise_weberror=False).get('location', '')

    elif '/link/' in item.url:
        data = do_downloadpage(item.url)
        url = scrapertools.find_single_match(data, "location.href='(.*?)'")

    if url:
        if '/openload.' in url: url = ''
        elif '/jetload.' in url: url = ''
        elif '.premiumstream.' in url: url  = ''

        if url:
            if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor == 'zplayer':
                url = url + '|' + player

            itemlist.append(item.clone( url = url, server = servidor ))

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


# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    from urllib.parse import quote
else:
    from urllib import quote

import re

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools

host = "https://pornhub.com/"

perpage = 30


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('pornhub', url, post=post, headers=headers).data

    return data


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

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color = 'orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + "video/", page = 0 ))

    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + "video?o=cm", page = 0 ))
    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + "video?o=mv", page = 0 ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + "video?o=tr", page = 0 ))
    itemlist.append(item.clone( title = 'Más candentes', action = 'list_all', url = host + "video?o=ht", page = 0 ))

    itemlist.append(item.clone( title = 'Long play', action = 'list_all', url = host + "video?o=lg", page = 0 ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + 'channels/', page = 0 ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))
    itemlist.append(item.clone( title = 'Por tipo', action = 'tipos', url = host + 'videos/'))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + 'pornstars/', page = 0 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul id="videoCategory" class="nf-videos videos search-video-thumbs">(.*?)<\/ul')

    if not bloque:
        bloque = scrapertools.find_single_match(data, '<ul class="videos recommendedContainerLoseOne">(.*?)<\/ul')
    if not bloque:
        bloque = scrapertools.find_single_match(data, '<ul class="videos row-5-thumbs search-video-thumbs scrollLazyload js-videoPlaylist viewPlaylist" id="videoPlaylist">(.*?)<\/ul')
    if not bloque and 'viewChunked' in item.url:
        bloque = data
    if not bloque:
        bloque = scrapertools.find_single_match(data, 'class="videos search-video-thumbs(.*?)<div class="reset"></div>')

    matches = re.compile('<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"data-thumb_url = "([^"]+)').findall(bloque)

    for url, title, thumb, thumb2 in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title,
                                    thumbnail = thumb if not 'base64' else thumb2, contentType = 'movie', contentTitle = title ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            next_url = next_url.replace('&amp;', '&')
        else:
            token = scrapertools.find_single_match(data, '<input type="hidden" name="token" value="([^"]+)')
            playlistId = scrapertools.find_single_match(data, '<input name="edit-pl-id" id="js-editPlaylistId" type="hidden" value="([^"]+)')
            if token and playlistId:
                next_url = '%splaylist/viewChunked?id=%s&token=%s&page=%s' % (host, playlistId, token, str(item.page + 1))

        if next_url:
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_all', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<nav id="mainMenuChannels">(.*?)<\/nav>')

    matches = re.compile('<a href="([^"]+)"><span>([^<]+)').findall(data)

    for url, title in matches:
        if 'Explorar todos los canales' in title: continue

        itemlist.append(item.clone( action = 'list_channels', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def categorias(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'categories')
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="headerSubMenu">(.*?)<\/ul')

    patron = '<li class="big video"><a class="js-mixpanel" data-mixpanel-listing="" '
    patron += 'href="([^"]+)".*? alt="([^"]+)"><img class="js-menuSwap" data-image="([^"]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb ))

    return sorted(itemlist, key=lambda x: x.title)


def tipos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div class="leftPanel videos">(.*?)<\/div>')

    patron = '<a class="js-mixpanel" data-mixpanel-listing="" '
    patron += 'href="([^"]+)".*?><i class="[^"]+"><\/i>([^<]+)'

    matches = re.compile(patron).findall(bloque)

    for url, title in matches:
        if title == 'Canales': continue

        if title == 'Listas de videos':
            action = 'listas'
        else:
            action = 'list_all'

        itemlist.append(item.clone( action = action, url = url if url.startswith('http') else host[:-1] + url, title = title))

    return sorted(itemlist, key=lambda x: x.title)


def pornstars(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul id="popularPornstars" class="videos row-5-thumbs popular-pornstar">(.*?)<\/ul>')

    patron = '<a class="js-mxp" data-mxptype="Pornstar" data-mxptext="([^"]+)" '
    patron += 'href="([^"]+)">.*?<span class="rank_number">(\d+).*?thumb_url="([^"]+)'

    matches = re.compile(patron).findall(bloque)

    for title, url, rank, thumb in matches:
        if not url.endswith('/videos'):
            url += '/videos'

        itemlist.append(item.clone( action = 'list_pornstars', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb ))

    return itemlist


def listas(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloques = scrapertools.find_multiple_matches(data, '<li id="playlist_\d+" class="full-width">(.*?)<\/li>')

    for bloque in bloques:
        matches = re.compile('data-image="([^"]+)"/>.*?<a class="title " title="([^"]+)" href="([^"]+)"').findall(bloque)

        for thumb, title, url in matches:
            itemlist.append(item.clone( action = 'list_all', url = url if url.startswith('http') else host[:-1] + url, title = title, thumbnail = thumb))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            next_url = next_url.replace('&amp;', '&')
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'listas', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def list_channels(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<li class="wrap"><div class="channelsWrapper clearfix"><div class="imgWrapper">'
    patron += '<a href="([^"]+)".*?<imgalt="([^"]+)".*?thumb_url="([^"]+)'

    matches = re.compile(patron).findall(data)

    for url, title, thumb in matches:
        itemlist.append(item.clone( action = 'list_categories', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            next_url = next_url.replace('&amp;', '&')
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_channels', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def list_categories(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = '<div class="floatLeft"><h2>([^<]+)</h2></div>'
    patron += '<div class="floatRight"><a class="seeAllButton greyButton light" href="([^"]+)'

    matches = re.compile(patron).findall(data)

    for title, url in matches:
        if 'premium' in title: continue

        itemlist.append(item.clone( action = 'list_videos', url = url if url.startswith('http') else host[:-1] + url, title = title))

    return itemlist


def list_videos(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<ul class="videos row-5-thumbs videosGridWrapper" id="showAllChanelVideos">(.*?)<\/ul>')

    matches = re.compile('<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"data-thumb_url = "([^"]+)').findall(bloque)

    for url, title, thumb, thumb2 in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url,
                                    title = title, thumbnail = thumb if not 'base64' else thumb2, contentType = 'movie', contentTitle = title ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            next_url = next_url.replace('&amp;', '&')
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_videos', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def list_pornstars(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<div id="profileContent" class="claimed profileVideos">(.*?)<div class="reset"><\/div>')

    matches = re.compile('<a href="([^"]+)" title="([^"]+)"class="[^"]+"[^<]+<imgsrc="([^"]+)"data-thumb_url = "([^"]+)').findall(bloque)

    for url, title, thumb, thumb2 in matches:
        itemlist.append(item.clone( action = 'findvideos', url = url if url.startswith('http') else host[:-1] + url, title = title,
                                    thumbnail = thumb if not 'base64' else thumb2, contentType = 'movie', contentTitle = title ))

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<li class="page_next"><a href="([^"]+)')

        if next_url:
            next_url = next_url.replace('&amp;', '&')
            itemlist.append(item.clone( title = 'Siguientes ...', url = next_url if next_url.startswith('http') else host[:-1] + next_url,
                                        action = 'list_pornstars', page = item.page + 1, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    headers = {'Referer': item.url}

    data = do_downloadpage(item.url, headers = headers)

    datos = scrapertools.find_single_match(data, '<div id="player"(.*?)</script>')
    datos = datos.replace('" + "', '' )

    vid_url = scrapertools.find_multiple_matches(datos, 'var media_\d+=([^;]+)')

    try:
        for match in vid_url:
            orden = scrapertools.find_multiple_matches(match, '\*\/([A-z0-9]+)')
            url = ''

            for i in orden:
                url += scrapertools.find_single_match(datos, '%s="([^"]+)"' % i)

        data = do_downloadpage(url, headers=headers)
    except:
        return itemlist

    jdata = jsontools.load(data)

    for elem in jdata:
        url = elem['videoUrl']
        qlty = elem['quality']

        if url:
            if ',' in str(qlty):
               continue

            url = url.replace('\\/', '/')

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, quality = qlty, language = 'VO' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = servertools.get_parse_hls(item.url)

    # ~ if config.get_setting('proxies', item.channel, default=''):
    # ~     if 'ip=' in url:
    # ~         part1_url = scrapertools.find_multiple_matches(url, '(.*?)ip=')
    # ~         if part1_url:
    # ~             part2_url = scrapertools.find_multiple_matches(url, 'ipa=(.*?)$')
    # ~             if part2_url:
    # ~                 url = '%s%s' % (part1_url, part2_url)
    # ~                 url = str(url.replace("']['", 'ipa='))

    itemlist.append(item.clone(server = item.server, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "video/search?search=%s" % (texto.replace(" ", "+"))
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

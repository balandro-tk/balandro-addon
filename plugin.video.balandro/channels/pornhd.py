# -*- coding: utf-8 -*-

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools


host = "https://www.pornhd.com"

host2 = 'https://www.pornhdprime.com'

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

    itemlist.append(item.clone( title = 'Buscar vídeo ...', action = 'search', search_type = 'movie', text_color='orange' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/?page=1' ))

    itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + '/?order=newest&page=1' ))
    itemlist.append(item.clone( title = 'Sugeridos', action = 'list_all', url = host + '/saved-videos' ))
    itemlist.append(item.clone( title = 'Más destacados', action = 'list_all', url = host + '/?order=featured&page=1' ))
    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + '/?order=most-popular&page=1' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + '/?order=top-rated&page=1' ))
    itemlist.append(item.clone( title = 'Long play', action = 'list_all', url = host + '/?order=longest&page=1' ))

    itemlist.append(item.clone( title = 'Por canal', action = 'canales', url = host + '/channel/' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))
    itemlist.append(item.clone( title = 'Por estrella', action = 'pornstars', url = host + '/pornstars/' ))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Novedades en canales', action = 'list_canales', url = item.url + '?order=newest'))
    itemlist.append(item.clone( title = 'Canales más populares', action = 'list_canales', url = item.url + '?order=most-popular'))
    itemlist.append(item.clone( title = 'Canales con más vídeos', action = 'list_canales', url = item.url + '?order=video-count'))
    itemlist.append(item.clone( title = 'Canales por alfabético', action = 'list_canales', url = item.url + '?order=alphabetical'))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    url_cat = host + '/category/'
   
    itemlist.append(item.clone( title = 'Novedades en categorías', action = 'list_categorias', url = url_cat + '?order=newest' ))
    itemlist.append(item.clone( title = 'Categorías más populares', action = 'list_categorias', url = url_cat + '?order=most-popular' ))
    itemlist.append(item.clone( title = 'Categorías con más vídeos', action = 'list_categorias', url = url_cat + '?order=video-count' ))
    itemlist.append(item.clone( title = 'Categorías por alfabético', action = 'list_categorias', url = url_cat + '?order=alphabetical' ))

    return itemlist


def pornstars(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Estrellas más populares', action = 'list_pornstars', url = item.url + '?order=most-popular&page=1' ))
    itemlist.append(item.clone( title = 'Estrellas con más vídeos', action = 'list_pornstars', url = item.url + '?order=video-count&page=1' ))
    itemlist.append(item.clone( title = 'Estrellas por alfabético', action = 'list_pornstars', url = item.url + '?order=alphabetical&page=1' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<phd-video-item(.*?)</phd-video-item')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        if 'live-video-item">' in match: continue

        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if url:
            title = scrapertools.find_single_match(match, 'img.*?alt="(.*?)"').strip()

            thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

            if url.startswith('/') == True:
               if '/videos/' in url:
                   url = host + url
               else:
                   url = host2 + url

            if thumb.startswith('//') == True: thumb = 'https:' + thumb

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie', contentTitle = title ))

            if len(itemlist) >= perpage: break

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, pagina = item.pagina, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
       if itemlist:
          if not 'pager next disabled' in data:
              if '<a class="pagination-next"' in data:
                  if 'page=' in item.url:
                      if '/?page=' in item.url: active_page = item.url.split("/?page=")[1]
                      else: active_page = item.url.split("&page=")[1]

                      if '/?page=' in item.url: next_url = item.url.replace('/?page=' + active_page, '')
                      else: next_url = item.url.replace('&page=' + active_page, '')

                      next_page = int(active_page) + 1

                      if '/?page=' in item.url: next_url = next_url + '/?page=' + str(next_page)
                      else: next_url = next_url + '&page=' + str(next_page)

                      itemlist.append(item.clone(title = "Siguientes ...", url = next_url, page = 0, action = 'list_all', text_color='coral'))

    return itemlist


def list_canales(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<section class="columns(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<a(.*?)</a>')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for match in matches[desde:hasta]:
        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not url: continue

        title = scrapertools.find_single_match(match, 'img.*?alt="(.*?)"')

        if 'data-src=' in match: thumb = scrapertools.find_single_match(match, 'data-src="([^"]+)"')
        else: thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')

        if url.startswith('/') == True: url = host + url

        if thumb.startswith('//') == True: thumb = 'https:' + thumb

        itemlist.append(item.clone( action = 'list_all', url = url + '/?page=1', title = title, thumbnail = thumb ))

    if num_matches > hasta:
        itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_canales', text_color='coral' ))

    return itemlist


def list_categorias(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<section class="columns(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<a(.*?)</a>')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for match in matches[desde:hasta]:
        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if not url: continue

        title = scrapertools.find_single_match(match, 'img.*?alt="(.*?)"')

        if 'data-src=' in match: thumb = scrapertools.find_single_match(match, 'data-src="([^"]+)"')
        else: thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')

        if url.startswith('/') == True: url = host + url

        if thumb.startswith('//') == True: thumb = 'https:' + thumb

        itemlist.append(item.clone( action = 'list_all', url = url + '/?page=1', title = title, thumbnail = thumb ))

    if num_matches > hasta:
        itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_categorias', text_color='coral' ))

    return itemlist


def list_pornstars(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<section class="columns(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<a(.*?)</a>')

    for match in matches:
        url = scrapertools.find_single_match(match, 'href="([^"]+)"')

        if url:
            title = scrapertools.find_single_match(match, '<div class="small-thumb-title">(.*?)</div>')

            videos = scrapertools.find_single_match(match, '<div class="is-size-7">(.*?)</div>')
            videos = videos.replace('videos' ,'').strip()

            title = title + ' (' + videos + ')'

            if 'data-src=' in match: thumb = scrapertools.find_single_match(match, 'data-src="([^"]+)"')
            else: thumb = scrapertools.find_single_match(match, 'src="([^"]+)"')

            if url.startswith('/') == True: url = host + url

            if thumb.startswith('//') == True: thumb = 'https:' + thumb

            itemlist.append(item.clone( action = 'list_all', url = url + '/?page=1', title = title, thumbnail = thumb ))

    if itemlist:
       if not 'pager next disabled' in data:
           if '<a class="pagination-next"' in data:
               active_page = item.url.split("&page=")[1]

               next_url = item.url.replace('&page=' + active_page, '')
               next_page = int(active_page) + 1

               next_url = next_url + '&page=' + str(next_page)

               itemlist.append(item.clone(title = "Siguientes ...", url = next_url, action = 'list_pornstars', text_color='coral'))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    matches = []

    if item.url.startswith(host2) == True:
        url_find = item.url.replace(host2, host)
        data = httptools.downloadpage(url_find, raise_weberror = False).data

        matches = scrapertools.find_multiple_matches(data, '<source src="(.*?)".*?res=(.*?)/>')

        if not matches:
            if 'id="html5-player"' in data:
                block = scrapertools.find_single_match(data, 'id="html5-player"(.*?)</video>')
                matches = scrapertools.find_multiple_matches(block, 'src="(.*?)".*?res=(.*?)/>')

    if not matches:
        data = httptools.downloadpage(item.url, raise_weberror = False).data

        matches = scrapertools.find_multiple_matches(data, '<source src="(.*?)".*?res=(.*?)/>')

        if not matches:
            if 'id="html5-player"' in data:
                block = scrapertools.find_single_match(data, 'id="html5-player"(.*?)</video>')
                matches = scrapertools.find_multiple_matches(block, 'src="(.*?)".*?res=(.*?)/>')

    for url, qlty in matches:
        qlty = scrapertools.find_single_match(qlty, "'(.*?)'").strip()

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', quality = qlty, url = url, ref = item.url, language = 'VO' ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url.replace('&amp;', '&')

    if item.url.startswith(host) == True:
        url = httptools.downloadpage(item.url, headers={'Referer': item.ref}, follow_redirects = False, only_headers = True).headers.get('location')

    itemlist.append(item.clone( url = url ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/search/?search=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

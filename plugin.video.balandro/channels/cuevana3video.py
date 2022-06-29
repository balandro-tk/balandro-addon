# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urlparse
else:
    import urllib.parse as urlparse


import re, time

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www1.cuevana3.vc/'

perpage = 22


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://www1.cuevana3.video', 'https://www2.cuevana3.video',
                 'https://cuevana3.so', 'https://www1.cuevana3.so', 'https://www2.cuevana3.so',
                 'https://cuevana3.cx', 'https://www1.cuevana3.cx', 'https://www2.cuevana3.cx',
                 'https://cuevana3.pe/', 'https://www1.cuevana3.pe/', 'https://www2.cuevana3.pe/'
                 'https://cuevana3.vc/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('cuevana3video', url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/estrenos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + '/peliculas-mas-vistas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catalogo', action = 'list_all', url = host + '/serie', filtro = 'tabserie-1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + '/serie', filtro = 'tabserie-4', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_episodes', url = host + '/serie', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data,'href="#">Géneros</a>(.*?)<li id="menu-item-1954"')
    matches = scrapertools.find_multiple_matches(bloque,'<a href=".*?">.*?</a>')

    for match in matches:
        url = scrapertools.find_single_match(match,'<a href="(.*?)">')
        title = scrapertools.find_single_match(match,'>(.*?)</a>')

        itemlist.append(item.clone( title = title, url = host + url , action = 'list_all', search_type = item.search_type ))

    return sorted(itemlist, key=lambda it: it.title)


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if item.filtro:
        if item.pageser:
            url = host + '/serie?action=cuevana_ajax_pagination&page=' + str(item.pageser)
            data = do_downloadpage(url, headers={'Referer': url})
        else:
            data = do_downloadpage(item.url)

        data = scrapertools.find_single_match(data, '<div\s*id="%s"(.*?)</nav>\s*</div>' % item.filtro)
    else:
        data = do_downloadpage(item.url)

    matches = re.compile('<div class="TPost C(.*?)</li>', re.DOTALL).findall(data)

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(article, '\s*href=(?:"|)([^ >"]+)')
        if '/pagina-ejemplo' in url: continue

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        if item.search_type not in ['all', tipo]: continue

        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, 'data-src="([^ >]+)"')
        if not thumb: thumb = scrapertools.find_single_match(article, ' src=(?:"|)([^ >"]+)')

        thumb = host + url

        title = scrapertools.find_single_match(article, '<h2 class="Title">([^<]+)</h2>').strip()
        qlty = scrapertools.find_single_match(article, '<span\s*class=(?:"|)Qlty(?:"|)>([^<]+)</span>')
        plot = scrapertools.find_single_match(article, '<p>(.*?)</p>')

        url = host + url

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail='https:'+ thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': '-', 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': '-', 'plot': plot} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        if item.filtro:
           if itemlist:
                pagina = 2 if not item.pageser else item.pageser + 1
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', pageser = pagina, text_color='coral' ))
        else:
           if '<nav class="navigation pagination">' in data:
               bloque_next = scrapertools.find_single_match(data, '<nav class="navigation pagination">(.*?)</nav>')
               next_page_link = scrapertools.find_single_match(bloque_next, "class='page-link current'>.*?</a><a href='(.*?)'")

               if next_page_link:
                   if not '?page=' in item.url:
                       next_page_link = item.url + next_page_link
                   else:
                       ant_url = scrapertools.find_single_match(item.url, "(.*?)page=")
                       ant_url = ant_url.replace('?', '')
                       next_page_link = ant_url + next_page_link

                   itemlist.append(item.clone( title = 'Siguientes ...', url = next_page_link, page = 0, action = 'list_all', text_color='coral' ))

    return itemlist


def last_episodes(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'Ultimos Episodios.*?</ul>')
    patron  = '(?is)<a href="([^"]+).*?src="([^"]+).*?"Title">([^<]+).*?<p>([^<]+)'

    matches = scrapertools.find_multiple_matches(bloque, patron)

    for url, thumb, title, date in matches:
        season, episode = scrapertools.get_season_and_episode(title).split("x")
        contentSerieName = scrapertools.find_single_match(title, '(.*?) \d')

        url = host + url
        thumb = 'https://' + thumb
        titulo = title + ' (%s)' % date

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSerieName=contentSerieName, contentSeason = season, contentEpisodeNumber = episode ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<option\s*value="(\d+)".*?Temporada'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action='episodios', title=title, contentType='season', contentSeason=numtempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    if item.contentSeason:
        data = scrapertools.find_single_match(data, '<ul\s*id="season-' + str(item.contentSeason) + '(.*?)</ul>')

    patron = '<li class="xxx TPostMv">.*?<a href="(.*?)">(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('Cuevana3Video', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, datos in matches[item.page * item.perpage:]:
        try:
            season, episode = scrapertools.find_single_match(datos, '<span class="Year">(.*?)x(.*?)</span>')
        except:
            continue

        if item.contentSeason:
           if not str(item.contentSeason) == str(season): continue

        title = scrapertools.find_single_match(datos, '<h2[^>]*>(.*?)</h2>')

        thumb = scrapertools.find_single_match(datos, 'data-src=([^ >]+)"')
        if  thumb.startswith('//'): thumb = 'https:' + thumb

        url = host + url

        itemlist.append(item.clone( action='findvideos', title = title, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['Cam', 'WEB-S', 'DVD-S', 'TS-HQ', 'DVD', 'DvdRip', 'HD', 'FullHD1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'Castellano': 'Esp', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = re.compile('<ul class="anime_muti_link server-item-(.*?)</ul>', re.DOTALL).findall(data)

    ses = 0

    for option in matches:
        ses += 1

        links = scrapertools.find_multiple_matches(option, '<li data-(.*?)</li>')

        for link in links:
            url = scrapertools.find_single_match(link, 'video="(.*?)"')
            lang = scrapertools.find_single_match(link,'<span class="cdtr">.*?<span>.*?-(.*?)-.*?</span>').strip()

            qlty = scrapertools.find_single_match(link,'<span class="cdtr">.*?<span>.*?-.*?-(.*?)</span>').strip()
            quality_num = puntuar_calidad(qlty)
            if quality_num == 0: qlty = ''

            if url.startswith('//'): url = 'https:' + url

            if url:
                if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                if servidor == 'directo':
                    link_other = normalize_other(url)
                    if link_other == '': continue
                else:
                    link_other = ''

                if not config.get_setting('developer_mode', default=False):
                   if link_other == 'hydrax': continue

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, referer = item.url,
                                      language = IDIOMAS.get(lang, lang), quality = qlty, quality_num = quality_num, other = link_other ))

    if '<li class="downloadopt">' in data:
        url = scrapertools.find_single_match(data, '<li class="downloadopt">.*?<a href="(.*?)"')
        if url:
            ses += 1

            if url.startswith('//'): url = 'https:' + url

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor == 'directo':
                link_other = normalize_other(url)
            else:
                link_other = ''

            if not config.get_setting('developer_mode', default=False):
                if link_other == 'hydrax': link_other = ''

            if link_other:
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, referer = item.url,
                                      quality = 'HD', other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def normalize_other(url):
    # hydrax no es pot resoldre

    link_other = ''
    url = url.lower()

    if 'pelisplus' in url: link_other = 'plus'
    elif 'peliscloud' in url: link_other = 'cloud'
    elif 'damedamehoy' in url: link_other = 'dame'
    elif 'tomatomatela' in url: link_other = 'dame'
    elif 'hydrax' in url: link_other = 'hydrax'
    else:
       if config.get_setting('developer_mode', default=False):
           try:
              link_other = url.split('//')[1]
              link_other = link_other.split('/')[0]
              link_other.lower()
           except:
              link_other = url

    return link_other


def resuelve_dame_toma(dame_url):
    data = do_downloadpage(dame_url)

    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
    if not url:
        checkUrl = dame_url.replace('embed.html#', 'details.php?v=')
        data = do_downloadpage(checkUrl, headers={'Referer': dame_url})
        url = scrapertools.find_single_match(data, '"file":\s*"([^"]+)').replace('\\/', '/')

    return url


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    servidor = item.server

    if servidor and servidor != 'directo':
        itemlist.append(item.clone(server = servidor, url = url))

    if item.other == 'hydrax':
        v = scrapertools.find_single_match(url, 'v=(\w+)')
        post = 'slug=%s&dataType=mp4' % v
        data = do_downloadpage("https://ping.iamcdn.net/", post = post)
        data = do_downloadpage('https://geoip.redirect-ads.com/?v=%s' % v, headers={'Referer' : url})

        return itemlist

    elif item.other == 'plus':
        data = do_downloadpage(item.url)

        if item.url.startswith('https://pelisplus.icu/play'):
            url = scrapertools.find_single_match(data, "sources:.*?'(.*?)'")
            if url:
                itemlist.append(item.clone(url=url , server='directo'))
                return itemlist

        elif item.url.startswith('https://pelisplus.icu/download'):
            matches = scrapertools.find_multiple_matches(data, '<div class="dowload".*?href="(.*?)"')

            for url in matches:
                if not 'https://xstreamcdn.com/f/' in url: continue

                url = url.replace('https://xstreamcdn.com/f/', '')

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                if servidor and servidor != 'directo':
                    itemlist.append(item.clone(url=url , server=servidor))
                    return itemlist

        matches = scrapertools.find_multiple_matches(data, 'data-video="(.*?)"')

        for url in matches:
            if '//damedamehoy.' in url or '//tomatomatela.' in url :
                url = resuelve_dame_toma(url)

                if url:
                    itemlist.append(item.clone(url=url , server='directo'))
                    return itemlist

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor and servidor != 'directo':
                itemlist.append(item.clone(url=url , server=servidor))
                return itemlist

        return itemlist

    elif item.other == 'cloud':
        dominio = urlparse.urlparse(url)[1]
        id = scrapertools.find_single_match(url, 'id=(\w+)')
        tiempo = int(time.time())
        url = 'https://' + dominio + '/playlist/' + id + '/%s.m3u8' % tiempo
        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, '/hls/\w+/\w+') + '?v=%s' % tiempo
        url = "https://" + dominio + url

        servidor = 'directo'
        if '/hls/' in url: servidor = 'm3u8hls'

        itemlist.append(item.clone(url=url , server=servidor))
        return itemlist

    elif item.other == 'dame':
        url = resuelve_dame_toma(item.url)

        if url:
            itemlist.append(item.clone(url=url , server=servidor))
            return itemlist

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/search.html?keyword=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

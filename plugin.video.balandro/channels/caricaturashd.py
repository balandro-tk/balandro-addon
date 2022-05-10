# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools, recaptcha
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = "https://caricaturashd.net/"


def do_downloadpage(url, post=None, headers=None):
    headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ultimas-peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ultimas-caricaturas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(host)

    matches = scrapertools.find_multiple_matches(data, 'menu-item-object-category.*?<a href="(.*?)".*?>(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url, genre = title ))

    itemlist.append(item.clone( action = 'list_all', title = 'Terror', url = host + 'terror/' ))
    itemlist.append(item.clone( action = 'list_all', title = 'Western', url = host + 'western/' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if item.genre:
        if not '?type=' in item.url:
            if item.search_type == 'movie':
                item.url = item.url + '?type=movies'
            else:
                item.url = item.url + '?type=series'

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article class="post dfx fcl movies">(.*?)</article>')

    for match in matches:
        title =  scrapertools.find_single_match(match, '<h2 class="entry-title text-center">(.*?)</h2>')
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        thumb if thumb.startswith('http') else "https:" + thumb

        tipo = 'movie' if '>Ver Película<' in match else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            itemlist.append(item.clone( action='temporadas', url = url, title = title, thumbnail = thumb, genre = item.genre, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title,  infoLabels = {'year': '-'} ))

        if tipo == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, genre = item.genre, fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if '>NEXT<' in data:
        next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?<a class="page-link".*?href="([^"]+)')

        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action='list_all', url = next_page, genre = item.genre, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    id_obj = scrapertools.find_single_match(data, ' data-object = "(.*?)"')
    if not id_obj: id_obj = scrapertools.find_single_match(data, ' data-object ="(.*?)"')
    if not id_obj: id_obj = scrapertools.find_single_match(data, ' data-object="(.*?)"')

    id_post = scrapertools.find_single_match(data, ' data-post="(.*?)"')

    if not id_obj or not id_post:
        return itemlist

    matches = scrapertools.find_multiple_matches(data, '<li class="sel-temp"><a data-post=".*?data-season="(.*?)"')

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.id_obj = id_obj
            item.id_post = id_post
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season,
                                    id_obj = id_obj, id_post = id_post ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda i: i.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    url_post =  host + 'wp-admin/admin-ajax.php'
    season = item.contentSeason

    post = {"action": "action_select_season", "season": season, "post": item.id_post, "object": item.id_obj}
    data = do_downloadpage(url_post, post = post)

    matches = scrapertools.find_multiple_matches(data, '<article class="post dfx fcl movies">(.*?)</article>')

    if '<a class="page-numbers"' in data:
        pages = scrapertools.find_multiple_matches(data, '<a class="page-numbers".*?>(.*?)</a>')

        for page in pages:
            post = {"action": "action_pagination_ep", "page": page, "season": season, "object": item.id_obj}
            data = do_downloadpage(url_post, post = post)

            matches_page = scrapertools.find_multiple_matches(data, '<article class="post dfx fcl movies">(.*?)</article>')
            if matches_page:
                matches += matches_page

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('CaricaturasHd', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for match in matches[item.page * item.perpage:]:
        title =  scrapertools.find_single_match(match, '<h2 class="entry-title text-center">(.*?)</h2>')
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')

        if not title or not url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
        thumb if thumb.startswith('http') else "https:" + thumb

        epis =  scrapertools.find_single_match(match, '<span class="year">' + str(item.contentSeason) + 'x(.*?)</span>').strip()

        ord_epis = str(epis)

        if len(str(ord_epis)) == 1:
            ord_epis = '0000' + ord_epis
        elif len(str(ord_epis)) == 2:
            ord_epis = '000' + ord_epis
        elif len(str(ord_epis)) == 3:
            ord_epis = '00' + ord_epis
        else:
            if item.perpage > 50:
                ord_epis = '0' + ord_epis

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    orden = ord_epis, contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", orden = '10000',
                                        page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return sorted(itemlist, key=lambda i: i.orden)


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es': 'Esp', 'lat': 'Lat', 'sub': 'Vose', 'latino': 'Lat', 'castellano': 'Esp', 'español': 'Esp', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    options = scrapertools.find_multiple_matches(data, 'data-opt=".*?options-(.*?)">.*?<span class="option">(.*?)</span>')

    ses = 0

    for option, lang in options:
        ses += 1

        lang = lang.split(" - ")[1]
        lang = lang.lower().strip()

        url = scrapertools.find_single_match(data, '<div id="options-' + option + '.*?<iframe.*?src="(.*?)"')

        if url == 'about:blank': url = scrapertools.find_single_match(data, '<div id="options-' + option + '.*?data-lazy-src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, '<div id="options-' + option + '.*?<iframe src="(.*?)"')

        if url:
           url = url.replace('&#038;', '&').replace('&amp;', '&')

           if '&lt;IFRAME SRC=&quot;' in url: url = scrapertools.find_single_match(url, '&lt;IFRAME SRC=&quot;(.*?)&quot;')
           elif '/cinemaupload.com/' in url: url = scrapertools.find_single_match(url, 'src=&quot;(.*?)&quot;')

           servidor = servertools.get_server_from_url(url)
           servidor = servertools.corregir_servidor(servidor)

           # ~ los servidores casi siempre son falsos pone cinemaupload
           if host in url: servidor = ''
           elif '/cinemaupload.com/' in url: servidor = ''

           itemlist.append(Item(channel = item.channel, action = 'play', server = servidor, title = '', url = url,
                                language = IDIOMAS.get(lang,lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.server:
        itemlist.append(item.clone(server = item.server, url = item.url))

    elif item.url.startswith(host):
        resp = httptools.downloadpage(item.url, follow_redirects=False)

        if 'location' in resp.headers: 
            url = resp.headers['location']
        else:
            url = scrapertools.find_single_match(resp.data, '<div class="Video">.*?src="(.*?)"')
            if not url: url = scrapertools.find_single_match(resp.data, '<IFRAME SRC="(.*?)"')

        if url:
            if '/cinemaupload.com/' in url:
                url = url.replace('/cinemaupload.com/', '/embed.cload.video/')

                data = do_downloadpage(url)

                sitekey = scrapertools.find_single_match(data, 'data-sitekey="([^"]+)')
                if not sitekey:
                    url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
                    if url:
                        if '/download/' in url:
                           url = url.replace('//download/', '/files/').replace('/download/', '/files/')
                           itemlist.append(item.clone( url = url, server = 'directo' ))
                           return itemlist

                        elif '/manifest.mpd' in url:
                           if platformtools.is_mpd_enabled():
                              itemlist.append(['mpd', url, 0, '', True])
                           itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
                        else:
                           itemlist.append(['m3u8', url])
                        return itemlist

                # ~ Opción aún sin desarrollar
                response = recaptcha.get_recaptcha_response(sitekey, item.url)
                return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone(server = servidor, url = url))

    elif item.url.startswith('https://cinemaupload.com/'):
        item.url = item.url.replace('/cinemaupload.com/', '/embed.cload.video/')

        data = do_downloadpage(item.url)

        sitekey = scrapertools.find_single_match(data, 'data-sitekey="([^"]+)')
        if not sitekey:
            url = scrapertools.find_single_match(data, 'file:\s*"([^"]+)')
            if url:
                if '/download/' in url:
                   url = url.replace('//download/', '/files/').replace('/download/', '/files/')
                   itemlist.append(item.clone( url = url, server = 'directo' ))
                   return itemlist

                elif '/manifest.mpd' in url:
                   if platformtools.is_mpd_enabled():
                       itemlist.append(['mpd', url, 0, '', True])
                   itemlist.append(['m3u8', url.replace('/users/', 'hls/users/', 1).replace('/manifest.mpd', '/index.m3u8')])
                else:
                   itemlist.append(['m3u8', url])
                   return itemlist

        # ~ Opción aún sin desarrollar
        response = recaptcha.get_recaptcha_response(sitekey, item.url)
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    else:
        data = do_downloadpage(item.url)

        new_url = scrapertools.find_single_match(data, "location.href='([^']+)")
        if new_url:
            servidor = servertools.get_server_from_url(new_url)
            servidor = servertools.corregir_servidor(servidor)
            itemlist.append(item.clone(url = new_url, server = servidor))

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


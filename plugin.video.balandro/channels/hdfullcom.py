# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www.hdfull-v1.com/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    url = url.replace('https://www.hd-full.com/', host)

    if 'release/' in url: raise_weberror = False

    # ~ timeout
    timeout = 30
    if '/?s=' in url: timeout = 50

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data
    data = httptools.downloadpage_proxy('hdfullcom', url, post=post, headers=headers, raise_weberror=raise_weberror, timeout=timeout).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-pelicula-1/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_new', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'category/destacadas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Sagas', action = 'list_sag', url = host, search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-serie-1/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Episodios recientes', action = 'list_epis', url = host + 'ver-episodios-online/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'category/destacadas/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Genero<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if title == 'Destacadas': continue

        if title == 'Reality':
            if item.search_type == 'movie': continue

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1932, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'release/' + str(x) + '/', action = 'list_all' ))

    return itemlist


def list_new(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Peliculas<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a title="(.*?)".*?href="(.*?)"')

    for title, url in matches:
        title = title.capitalize()

        if not url.startswith("http"): url = host + url[1:]

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def list_sag(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Sagas<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        if not url.startswith("http"): url = host + url[1:]

        itemlist.append(item.clone( title = title, url = url, action = 'list_all' ))

    return itemlist


def list_epis(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 30

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)</section>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        temp_epis = scrapertools.find_single_match(match, '<span class="num-epi">(.*?)</span>')

        season = scrapertools.find_single_match(temp_epis, '(.*?)x')
        episode = scrapertools.find_single_match(temp_epis, '.*?x(.*?)')

        itemlist.append(item.clone( action='findvideos', url=url, title=title, contentSerieName=title,
                                   contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage:
            break

    buscar_next = True
    if num_matches > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title="Siguientes ...", action="list_epis", page=item.page + 1, text_color='coral' ))
        buscar_next = False

    if buscar_next:
        next_page = scrapertools.find_single_match(data, '<a class="page-numbers".*?</a>.*?href="(.*?)"')

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'list_epis', text_color = 'coral'))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    data = scrapertools.find_single_match(data, '<h1(.*?)</section>')

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')

        if not url or not title: continue

        tipo = 'movie' if '/ver-pelicula' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(match, '<span class="Qlty">(.*?)</span>')

        langs = []
        if '/esp.png' in match: langs.append('Esp')
        if '/mexico2.png' in match: langs.append('Lat')
        if '/subs.png' in match: langs.append('Vose')

        if '/ver-pelicula' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, languages=', '.join(langs), fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')

    if next_page:
        if '/page/' in next_page:
            itemlist.append(item.clone(title = 'Siguientes ...', url = next_page, action = 'list_all', text_color = 'coral'))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'data-season="(.*?)"')

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    postid = scrapertools.find_single_match(data, 'data-postid="(.*?)"')
    if not postid:
        postid = scrapertools.find_single_match(data, 'postid-(.*?) ')

    post = {'action': 'action_select_season', 'season': str(item.contentSeason), 'post': postid}
    headers = {'Referer': item.url}

    data = do_downloadpage(host + 'wp-admin/admin-ajax.php',  post = post, headers = headers)

    patron = '<span class="num-epi">(.*?)</span>.*?<h2 class="entry-title">(.*?)</h2>.*?<a href="(.*?)"'

    matches = scrapertools.find_multiple_matches(data, patron)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('HdFullCom', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for episode, title, url in matches[item.page * item.perpage:]:
        epis = scrapertools.find_single_match(episode, '.*?x(.*?)$')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, contentType = 'episode', contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color= 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'id="options-(.*?)".*?<iframe.*?data-src="(.*?)"')

    ses = 0

    for opt, url in matches:
        ses += 1

        srv, lang = scrapertools.find_single_match(data, 'href="#options-' + str(opt)+ '">.*?<span class="server">(.*?)-(.*?)</span>')

        srv = srv.strip()

        lang = lang.strip()
        if '</td>' in lang: lang = scrapertools.find_single_match(lang, '(.*?)</td>')

        idioma = IDIOMAS.get(lang, lang)

        other = srv.lower() + '-' + str(ses)

        if 'hqq' in other or 'waaw' in other or 'netu' in other: continue
        elif 'openload' in other: continue
        elif 'powvideo' in other: continue
        elif 'streamplay' in other: continue
        elif 'rapidvideo' in other: continue
        elif 'streamango' in other: continue
        elif 'verystream' in other: continue
        elif 'vidtodo' in other: continue

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = 'directo', url = url, other = other, language = idioma ))

    # ~ Download
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<span class="num">#.*?</span>(.*?)</td><td>(.*?)</td><td><span>(.*?)</span>.*?href="(.*?)"')
    if not matches:
        matches = scrapertools.find_multiple_matches(data, '<span class="num">#.*?</span>(.*?)</td> <td>(.*?)</td> <td><span>(.*?)</span>.*?href="(.*?)"')

    for servidor, lang, qlty, url in matches:
        ses += 1

        servidor = servidor.lower().strip()

        idioma = IDIOMAS.get(lang, lang)

        other = 'd'

        if servidor == 'op':
            other = 'dop'
            servidor = 'directo'

        if url:
            itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, other = other,
                                  language = idioma, quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    headers = {'Referer': item.url}

    if item.other == 'd':
        url = httptools.downloadpage(item.url, headers=headers, follow_redirects=False).headers.get('location', '')

        if url:
            url = url.replace('uptobox', 'uptostream')

            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            itemlist.append(item.clone(server = servidor, url = url))

        return itemlist

    elif item.other == 'dop':
        data = do_downloadpage(item.url, headers=headers)

        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="(.*?)"')

        if '/validaEnlace' in url:
            url = httptools.downloadpage(url, headers=headers, timeout = 30, follow_redirects=False).headers.get('location', '')
            if url == 'https://streamplusvip.xyz': url = ''

        if '/hqq.' in url or '/waaw.' in url or '/netu' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)
            itemlist.append(item.clone( url=url, server=servidor))

        return itemlist

    data = do_downloadpage(item.url, headers=headers)

    url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')
    if not url: url = scrapertools.find_single_match(data, '<IFRAME.*?SRC="(.*?)"')

    if '.streamplusvip.' in url:
        data = do_downloadpage(url, headers=headers)

        video = scrapertools.find_single_match(data, "watch_video.php(.*?)'")
        hostr = scrapertools.find_single_match(data, "hostRedirection.*?'(.*?)'")

        if '/hqq.' in hostr or '/waaw.' in hostr or '/netu.' in hostr:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        url = ''
        if video:
            if hostr:
                url = 'https://1.streamplusvip.xyz/player/ip.php/' + video
                data = do_downloadpage(url, headers=headers)

                _iss = scrapertools.find_single_match(data, 'iss="(.*?)"')
                if _iss:
                    url = hostr +'/' + _iss

    elif '/mostrarEnlace' in url or '/validaEnlace' in url:
        url = url.replace('/mostrarEnlace', '/validaEnlace')
        url = httptools.downloadpage(url, headers=headers, timeout = 30, follow_redirects=False).headers.get('location', '')

        if url == 'https://streamplusvip.xyz': url = ''

    if '/hqq.' in url or '/waaw.' in url or '/netu' in url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'
    elif 'peliculonhd.' in url:
        return 'Servidor [COLOR yellow]NO soportado[/COLOR]'

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)
        itemlist.append(item.clone( url=url, server=servidor))

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

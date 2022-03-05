# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://123pelis.fun/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/lanzamiento/' in url: raise_weberror = False

    data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=movies', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'tag/pelicula-netflix/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'tag/Series-netflix/', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'tag/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'tag/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'tag/subtitulado/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    generos = [
       'accion',
       'animacion',
       'aventura',
       'belica',
       'ciencia-ficcion',
       'comedia',
       'crimen',
       'documental',
       'drama',
       'familia',
       'fantasia',
       'historia',
       'misterio',
       'musica',
       'romance',
       'suspense',
       'terror',
       'western'
       ]

    for genero in generos:
        url = host + 'genero/' + genero + '/'

        itemlist.append(item.clone( action = 'list_all', title = genero.capitalize(), url = url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1931, -1):
        url = host + 'lanzamiento/' + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if '<h2>Añadido recientemente' in data: patron = '<h2>Añadido recientemente(.*?)123Pelis:'
    else: patron = '<h1>(.*?)123Pelis:'

    bloque = scrapertools.find_single_match(data, patron)

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, '<image src="(.*?)"')

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')
        qlty = qlty.replace('⭐', '').strip()

        year = scrapertools.find_single_match(match, '</noscript>.*?</h3><span>(.*?)</span>')
        if not year: year = '-'

        if '/pelicula/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if '/serie/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<span class="current">' + ".*?<a href='(.*?)'")
        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', group = item.group, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile("<span class='se-t.*?'>(.*?)</span>", re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>" + str(item.contentSeason) + "</span>(.*?)</div></div>")

    patron = "<li class='mark-.*?src='(.*?)'.*?<div class='numerando'>(.*?)</div>.*?<a href='(.*?)'>(.*?)</a>"

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('123Pelis', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for thumb, s_e, url, title in matches[item.page * item.perpage:]:
        episode = scrapertools.find_single_match(s_e, ".*? - (.*?)$")

        titulo = str(item.contentSeason) + 'x' + str(episode) + ' ' + title

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail=thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<div id='playeroptions'(.*?)</ul></div></div>")

    matches = scrapertools.find_multiple_matches(bloque, "<li id='player-option-(.*?)</span></li>")

    lang = scrapertools.find_single_match(data, '<meta property="article.*?content="(.*?)"')

    lang = ''
    if lang == 'Latino': lang = 'Lat'
    elif lang == 'Castellano': lang = 'Esp'
    elif lang == 'Subtitulado': lang = 'Vose'

    ses = 0

    for match in matches:
        ses += 1

        dpost = scrapertools.find_single_match(match, "data-post='(.*?)'")
        dtype = scrapertools.find_single_match(match, "data-type='(.*?)'")
        dnume = scrapertools.find_single_match(match, "data-nume='(.*?)'")

        srv = scrapertools.find_single_match(match, "<span class='server'>(.*?)</span>")

        other = srv.lower()
        other = other.replace('.com', '').replace('.co', '').replace('.cc', '').replace('.ru', '').replace('.sh', '').replace('.so', '').replace('.sx', '')
        other = other.replace('.me', '').replace('.to', '').replace('.tv', '').replace('.fun', '').replace('.site', '').strip()

        if 'youtube' in other: continue

        elif 'waaw' in other: continue
        elif 'hqq' in other: continue
        elif 'netu' in other: continue

        elif 'cloudyport' in other: continue
        elif 'onlystream' in other: continue
        elif 'ninjastream' in other: continue
        elif 'videomega' in other: continue
        elif 'stream.kiwi' in other: continue

        if 'zlive' in other: other = 'zplayer'
        elif 'hideload' in other: other = 'hideload'

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '',
                              dpost = dpost, dtype = dtype, dnume = dnume, language = lang, other = other.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.dpost:
        post = {'action': 'doo_player_ajax', 'post': item.dpost, 'nume': item.dnume, 'type': item.dtype}

        data = do_downloadpage(host + 'wp-admin/admin-ajax.php/', post = post)

        url = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        if url:
            url = url.replace('\\/', '/')

            if 'pelis123' in url: url = juicycodes(url)
            elif 'hideload' in url: url = unhideload(url)

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if 'zplayer' in url: url += "|referer=%s" % host

        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def unhideload(url):
    logger.info()

    servers = {
           "ad": "https://videobin.co/embed-",
           "gd": "https://mixdrop.co/e/",
           "hd": "https://stream.kiwi/e/",
           "jd": "https://clipwatching.com/embed-",
           "kd": "https://play.pelis123.fun/e/",
           "ld": "https://dood.watch/e/",
           "md": "https://feurl.com/v/",
           "pd": "https://cloudvideo.tv/embed-",
           "ud": "https://dood.watch/e/"
           }

    try:
        server = scrapertools.find_single_match(url, r'(\wd)=')
        server = servers.get(server, server)

        hash_ = url.split('=')[1].split('&')[0]
        inv = hash_[::-1]

        result = codecs.decode(inv, 'hex').decode('utf-8')
        url = "%s%s" % (server, result)
    except:
        pass

    return url


def juicycodes(url):
    logger.info()

    import base64

    from lib import jsunpack

    try:
        data = do_downloadpage(url)

        juiced = scrapertools.find_single_match(data, 'JuicyCodes.Run\((.*?)\);')
        b64_data = juiced.replace('+', '').replace('"', '')
        b64_decode = base64.b64decode(b64_data)
        dejuiced = jsunpack.unpack(b64_decode)

        matches = re.compile('"file":"([^"]+)","label":"(\d+P)"', re.DOTALL).findall(dejuiced)
        for vid_url, vid_qlty in matches:
            return vid_url
            break

    except:
         return ''
    
def list_search(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, '<h1(.*?)123Pelis:')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')

        title = scrapertools.find_single_match(match, ' alt="(.*?)"')

        if not url or not title: continue

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        year = scrapertools.find_single_match(match, '</h3><span>(.*?)</span>')
        if not year:
            year = '-'

        plot = scrapertools.htmlclean(scrapertools.find_single_match(match, '<p>(.*?)</p>'))

        lngs = []
        langs = scrapertools.find_multiple_matches(match, '/flags/(.*?).png')

        for lang in langs:
            lng = ''

            if lang == 'es': lng = 'Esp'
            if lang == 'mx': lng = 'Lat'
            if lang == 'en': lng = 'Vose'

            if lng:
               if not lng in str(lngs): lngs.append(lng)

        if '/pelicula/' in url:
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            sufijo = '' if item.search_type != 'all' else 'movie'

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, languages = ', '.join(lngs), fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))

        if '/serie/' in url:
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


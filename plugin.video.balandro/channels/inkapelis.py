# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://inkapelis.in/'


descartar_anime = config.get_setting('descartar_anime', default=False)


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    url = url.replace('https://inkapelis.me/', host)

    raise_weberror = False if '/fecha/' in url else True

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

    itemlist.append(item.clone( title = 'Estrenos (en HD)', action = 'list_all', url = host + 'genero/estrenos-hd/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'genero/destacadas/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'calidad/hd/', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'En cines', action = 'list_all', url = host + 'genero/cine/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Infantiles', action = 'list_all', url = host + 'seccion/infantil/', search_type = 'movie' ))

    if not descartar_anime:
        itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'seccion/animes/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos capítulos', action = 'last_episodes', url = host + 'episodio/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Últimas temporadas', action = 'last_seasons', url = host + 'temporada/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Infantiles', action = 'list_all', url = host + 'seccion/infantil/', search_type = 'tvshow' ))

    if not descartar_anime:
        itemlist.append(item.clone( title = 'Animes', action = 'list_all', url = host + 'seccion/animes/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Castellano', action = 'list_all', url = host + 'idioma/castellano/' ))
    itemlist.append(item.clone( title = 'Latino', action = 'list_all', url = host + 'idioma/latino/' ))
    itemlist.append(item.clone( title = 'Subtitulado', action = 'list_all', url = host + 'idioma/subtituladas/' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': url_gen = host + 'pelicula/'
    else: url_gen = host + 'serie/'

    data = do_downloadpage(url_gen)

    bloque = scrapertools.find_single_match(data, '<ul class="genres scrolling">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>.*?<i>(.*?)</i>')

    for url, title, num in matches:
        if num == '0': continue

        if '/cine/' in url or '/destacadas/' in url or '/estrenos-hd/' in url: continue

        if item.search_type == 'tvshow': titulo = title
        else: titulo = '%s (%s)' % (title, num)

        itemlist.append(item.clone( action='list_all', title=titulo, url=url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1938, -1):
        itemlist.append(item.clone( title=str(x), url= host + '/fecha/' + str(x) + '/', action='list_all' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    productoras = [
        ['abc', 'ABC'],
        ['adult-swim', 'Adult Swim'],
        ['amazon', 'Amazon'],
        ['amc', 'AMC'],
        ['apple-tv', 'Apple TV+'],
        ['bbc-one', 'BBC One'],
        ['bbc-two', 'BBC Two'],
        ['bs11', 'BS11'],
        ['cbc', 'CBC'],
        ['cbs', 'CBS'],
        ['comedy-central', 'Comedy Central'],
        ['dc-universe', 'DC Universe'],
        ['disney', 'Disney+'],
        ['disney-xd', 'Disney XD'],
        ['espn', 'ESPN'],
        ['fox', 'FOX'],
        ['fx', 'FX'],
        ['hbc', 'HBC'],
        ['hbo', 'HBO'],
        ['hbo-espana', 'HBO España'],
        ['hbo-max', 'HBO Max'],
        ['hulu', 'Hulu'],
        ['kbs-kyoto', 'KBS Kyoto'],
        ['mbs', 'MBS'],
        ['nbc', 'NBC'],
        ['netflix', 'Netflix'],
        ['nickelodeon', 'Nickelodeon'],
        ['paramount', 'Paramount+'],
        ['showtime', 'Showtime'],
        ['sky-atlantic', 'Sky Atlantic'],
        ['stan', 'Stan'],
        ['starz', 'Starz'],
        ['syfy', 'Syfy'],
        ['tbs', 'TBS'],
        ['telemundo', 'Telemundo'],
        ['the-cw', 'The CW'],
        ['tnt', 'TNT'],
        ['tokyo-mx', 'Tokyo MX'],
        ['tv-tokyo', 'TV Tokyo'],
        ['usa-network', 'USA Network'],
        ['youtube-premium', 'YouTube Premium'],
        ['zdf', 'ZDF']
        ]

    url = host + 'network/'

    for x in productoras:
        itemlist.append(item.clone( title = x[1], url = url + str(x[0]) + '/', action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<h2>Añadido recientemente(.*?)<div class="copy">'
    if '/page/' in item.url:
        patron = '(.*?)<div class="copy">'

    bloque = scrapertools.find_single_match(data, patron)

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, ' alt="([^"]+)"')
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        title_alt = title.split('(')[0].strip() if ' (' in title else ''

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = scrapertools.find_single_match(article, '<span>(\d{4})</span>')
        plot = scrapertools.htmlclean(scrapertools.find_single_match(article, '<div class="texto">(.*?)</div>'))

        if tipo == 'movie':
            if item.search_type == 'tvshow': continue
            elif item.search_type == 'movie':
                if not '/pelicula/' in url: continue

            qlty = scrapertools.find_single_match(article, '<span class="quality">([^<]+)')

            langs = []
            if '<div class="castellano">' in article: langs.append('Esp')
            if '<div class="español">' in article: langs.append('Esp')
            if '<div class="latino">' in article: langs.append('Lat')
            if '<div class="subtitulado">' in article: langs.append('Vose')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty,
                                        languages = ', '.join(langs), fmt_sufijo = sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))
        else:
            if item.search_type == 'movie': continue
            elif item.search_type == 'tvshow':
                if not '/serie/' in url: continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo = sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot}, contentTitleAlt = title_alt ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "href='(.*?)'")
        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile("<span class='se-t[^']*'>(\d+)</span>", re.DOTALL).findall(data)

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


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    matches = re.compile("<li class='mark-\d+'>(.*?)</li>", re.DOTALL).findall(data)

    num_matches = len(matches)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('InkaPelis', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for datos in matches[item.page * item.perpage:]:
        try:
            url, title = scrapertools.find_single_match(datos, " href='([^']+)'>([^<]+)</a>")
            season, episode = scrapertools.find_single_match(datos, "<div class='numerando'>(\d+) - (\d+)")
        except:
            num_matches = num_matches - 1
            continue

        if item.contentSeason:
            if not str(item.contentSeason) == str(season):
                num_matches = num_matches - 1
                continue

        thumb = scrapertools.find_single_match(datos, " src='([^']+)")
        titulo = '%sx%s %s' % (season, episode, title)

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail=thumb, url = url,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def last_episodes(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = r'data-src="([^"]+)".*?<div class="data"><h3><a href="([^"]+)">([^<]+)</a></h3>.*?<span>([^/]+).*?<span class="serie">([^<]+)'

    matches = scrapertools.find_multiple_matches(data, patron)

    for thumb, url, title, season_episode, tvshow_title in matches:
        if not url or not title: continue

        season = scrapertools.find_single_match(season_episode, 'T(.*?) E')
        episode = scrapertools.find_single_match(season_episode, 'E(.*?)$')
        if not season or not episode: continue

        if thumb.startswith('//') == True: thumb = 'https:' + thumb

        titulo = season + 'x' + episode + ' ' + title.strip() + '  ' + tvshow_title.strip()

        itemlist.append(item.clone( action='findvideos', title = titulo, thumbnail = thumb, url = url,
                                    contentType = 'episode', contentSerieName = tvshow_title, contentSeason = season, contentEpisodeNumber = episode ))

    if itemlist:
        next_url = scrapertools.find_multiple_matches(data, """<span class="current">.*?<a href='([^']+)""")
        if next_url:
            url = next_url[-1]
            itemlist.append(item.clone( title="Siguientes ...", action="last_episodes", url = url, text_color='coral' ))

    return itemlist


def last_seasons(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(item.url)

    matches = re.compile(' class="item se seasons"(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<span class="c">(.*?)</span>')
        numtempo = scrapertools.find_single_match(article, '<span class="b">(\d+)</span>')

        if not url or not title or not numtempo: continue

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')

        itemlist.append(item.clone( action='episodios', title='%s - Temporada %s' % (title, numtempo), thumbnail=thumb, url = url,
                                    contentType='season', contentSeason=numtempo, contentSerieName=title ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, '<div class="pagination">.*?<span class="current">.*?' + "href='(.*?)'")
        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url=next_page, action='last_seasons', text_color='coral' ))

    return itemlist


def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)

    if servidor == 'drive': return 'gvideo'
    elif servidor == 'drive [vip]': return 'gvideo'
    elif servidor == 'playstp': return 'streamtape'
    elif servidor == 'playsl': return 'streamlare'
    elif servidor == 'descargar': return 'mega' # 1fichier, Uptobox
    elif servidor == 'vip': return 'directo'
    elif servidor == 'premium': return 'digiload'
    elif servidor == 'goplay': return 'gounlimited'
    elif servidor in ['meplay', 'megaplay']: return 'netutv'
    elif servidor == 'playerv': return 'directo' # storage.googleapis
    elif servidor == 'stream': return 'mystream'
    elif servidor == 'evoplay': return 'evoload'
    elif servidor == 'zplay': return 'zplayer'

    else: return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'castellano': 'Esp', 'español': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, "<li id='player-option-\d+'(.*?)</li>")

    ses = 0

    for enlace in matches:
        ses += 1

        dtype = scrapertools.find_single_match(enlace, "data-type='(.*?)'")
        dpost = scrapertools.find_single_match(enlace, "data-post='(.*?)'")
        dnume = scrapertools.find_single_match(enlace, "data-nume='(.*?)'")

        if dnume == 'trailer': continue
        elif not dtype or not dpost or not dnume: continue

        if dtype == 'tv': link_final = '/tv/meplayembed'
        else: link_final = '/movie/meplayembed'

        enbed_url = do_downloadpage(host + 'wp-json/dooplayer/v2/' + dpost + link_final, headers={'Referer': item.url})
        if not enbed_url: continue

        new_embed_url = scrapertools.find_single_match(enbed_url, '"embed_url":"(.*?)"')
        if not new_embed_url: continue

        new_embed_url = new_embed_url.replace('\\/', '/')

        data2 = do_downloadpage(new_embed_url, headers={'Referer': item.url})

        # ~  "Server1" tienen RecaptCha
        url = scrapertools.find_single_match(data2, '"Server0":"(.*?)"')
        if not url: continue

        lang = scrapertools.find_single_match(enlace, "/img/flags/(.*?).svg").lower()

        if 'play.php?v=' in url:
            vurl = url.split('play.php?v=')[1]
            if vurl.startswith('//'): vurl = 'https:' + vurl
            servidor = servertools.get_server_from_url(vurl)

            if servidor and servidor != 'directo':
                vurl = servertools.normalize_url(servidor, vurl)
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = vurl, language = IDIOMAS.get(lang, lang) ))

        else:
            data3 = do_downloadpage(url, headers={'Referer': host})
            dom = '/'.join(url.split('/')[:3])

            links = scrapertools.find_multiple_matches(data3, '<li(?: id="servers"|) onclick(.*?)</li>')

            i_lang = 0

            for lnk in links:
                i_lang += 1

                vurl = scrapertools.find_single_match(lnk, "go_to_player\('([^']+)")
                if not vurl: continue

                patron = ".*?'" + str(i_lang) + ".*?/assets/player/lang/(.*?).png"

                lang2 = scrapertools.find_single_match(str(links), patron).lower()

                if lang2: lang = lang2

                vurl = vurl.replace('https://go.megaplay.cc/index.php?h=', '/playerdir/')
                if '/playerdir/' in vurl: vurl = '/playdir/' + scrapertools.find_single_match(vurl, "/playerdir/([^&]+)")
                if vurl.startswith('/'): vurl = dom + vurl

                servidor = scrapertools.find_single_match(lnk, 'player/server/([^."]+)').lower()
                if not servidor: servidor = scrapertools.find_single_match(lnk, '<span class="serverx">([^<]+)').lower()

                if servidor == 'meplay': continue
                elif servidor == 'stream': continue
                elif servidor == 'playsb': continue
                elif servidor == 'descargar': continue

                if not lang2:
                    lang3 = scrapertools.find_single_match(lnk, "<p>([A-z]+)").lower()
                    if lang3: lang = lang3
                    else:
                       if str(item.languages): lang = str(item.languages)
                       else:
                          if not lang: lang = '?'

                servidor = corregir_servidor(servidor)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = vurl, language = IDIOMAS.get(lang, lang) ))

            if not links:
                links = scrapertools.find_multiple_matches(data3, '<a id="servers"(.*?)</a>')
                for lnk in links:
                    lembed = scrapertools.find_single_match(lnk, 'data-embed="([^"]+)')
                    ltype = scrapertools.find_single_match(lnk, 'data-type="([^"]+)')

                    servidor = scrapertools.find_single_match(lnk, 'title="([^".]+)').lower()
                    if not servidor: servidor = scrapertools.find_single_match(lnk, '<span class="serverx">([^<]+)').lower()

                    if servidor == 'meplay': continue
                    elif servidor == 'playsb': continue
                    elif servidor == 'stream': continue

                    servidor = corregir_servidor(servidor)

                    itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', referer = url,
                                          lembed = lembed, ltype = ltype, lurl = '/'.join(url.split('/')[:3]), language = IDIOMAS.get(lang, lang) ))

            if not links:
                dom = '/'.join(url.split('/')[:3])
                links = get_sources(data3)
                for lnk in links:
                    if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]

                    itemlist.append(Item( channel = item.channel, action = 'play', server = '', title = '', url = lnk[0], referer = url,
                                          language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.lembed and item.ltype and item.lurl:
        post = {'type': item.ltype, 'streaming': item.lembed}
        data = do_downloadpage(item.lurl + '/edge-data/', post=post, headers={'Referer': item.referer})

        item.url = scrapertools.find_single_match(data, '"url": "([^"]+)')
        if not item.url:
            if data.startswith('http'): item.url = data
            elif data.startswith('/'): item.url = item.lurl + data

        if not item.url:
            return itemlist

        item.url = item.url.replace('inkapelis.in/player?url=', 'inkapelis.in/player/?url=')
        item.url = item.url.replace('inkapelis.in/fplayer?url=', 'inkapelis.in/redirector.php?url=')

    if 'playerd.xyz/' in item.url or 'inkapelis.in/' in item.url:
        resp = httptools.downloadpage(item.url, headers={'Referer': item.referer if item.referer else item.url}, follow_redirects=False)

        if 'refresh' in resp.headers: vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
        elif 'location' in resp.headers: vurl = resp.headers['location']
        else:
            url = scrapertools.find_single_match(resp.data, '<iframe src="([^"]+)')
            if not url: url = scrapertools.find_single_match(resp.data, "window\.open\('([^']+)")
            if not url: url = scrapertools.find_single_match(resp.data, 'location\.href = "([^"]+)')
            if url and url.startswith('/'): url = '/'.join(item.url.split('/')[:3]) + url

            if 'playerd.xyz/' in url or 'inkapelis.in/' in url:
                url = url.replace('iframe?url=', 'redirect?url=')
                resp = httptools.downloadpage(url, headers={'Referer': item.url}, follow_redirects=False)

                if 'refresh' in resp.headers: vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
                elif 'location' in resp.headers: vurl = resp.headers['location']
                else:
                    vurl = scrapertools.find_single_match(resp.data, 'downloadurl = "([^"]+)')
                    if not vurl and 'player.php?id=' in url: vurl = url
            else:
                if url: vurl = url
                else:
                    gk_link = scrapertools.find_single_match(resp.data, 'config_player\.link = "([^"]+)')
                    if gk_link:
                        post = 'link=' + gk_link
                        data = do_downloadpage('https://players.inkapelis.in/player/plugins/gkpluginsphp.php', post=post)
                        vurl = scrapertools.find_single_match(data, '"link":"([^"]+)').replace('\\/', '/')
                    else:
                        vurl = None
                        dom = '/'.join(item.url.split('/')[:3])
                        links = get_sources(resp.data)

                        for lnk in links:
                            if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
                            if lnk[1] == 'hls': itemlist.append(item.clone(url = lnk[0], server = 'm3u8hls'))
                            else: itemlist.append([lnk[2], lnk[0]])

        if vurl and vurl.startswith('/'): vurl = '/'.join(item.url.split('/')[:3]) + vurl

    elif item.url.startswith('http'):
        vurl = item.url

    if vurl and '/playdir' in vurl:
        resp = httptools.downloadpage(vurl, headers={'Referer': item.url}, follow_redirects=False)
        if 'refresh' in resp.headers: vurl = scrapertools.find_single_match(resp.headers['refresh'], ';\s*(.*)')
        elif 'location' in resp.headers: vurl = resp.headers['location']
        else: vurl = None

    if vurl:
        if 'player.php?id=' in vurl:
            resp = httptools.downloadpage(vurl, headers={'Referer': item.url}, follow_redirects=False)
            dom = '/'.join(vurl.split('/')[:3])
            links = get_sources(resp.data)

            for lnk in links:
                if lnk[0].startswith('/'): lnk[0] = dom + lnk[0]
                if lnk[1] == 'hls': itemlist.append(item.clone(url = lnk[0], server = 'm3u8hls'))
                else: itemlist.append([lnk[2], lnk[0]])

            vurl = None

        elif 'index.php?h=' in vurl:
            hash = scrapertools.find_single_match(vurl, 'h=(.*?)&')
            post = {'h': hash}
            player = 'https://gcs.megaplay.cc/'

            vurl = httptools.downloadpage(player + 'r.php', post = post, headers={'Referer': item.url}, follow_redirects = False, only_headers = True, raise_weberror=False).headers.get('location', '')

    if vurl:
        if '/hqq.' in vurl or '/waaw.' in vurl or '/netu.' in vurl:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(vurl)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'zplayer':
            player = 'https://player.inkapelis.in/'
            vurl = vurl + '|' + player

        if servidor and (servidor != 'directo' or 'googleapis.com' in vurl):
            url = servertools.normalize_url(servidor, vurl)
            itemlist.append(item.clone( url=url, server=servidor ))

    return itemlist


def get_sources(data):
    srcs = []

    bloque = scrapertools.find_single_match(data, '(?:"|)sources(?:"|):\s*\[(.*?)\]')

    for enlace in scrapertools.find_multiple_matches(bloque, "\{(.*?)\}"):
        v_url = scrapertools.find_single_match(enlace, '(?:"|)file(?:"|):\s*"([^"]+)')
        if not v_url: continue

        v_type = scrapertools.find_single_match(enlace, '(?:"|)type(?:"|):\s*"([^"]+)')
        v_lbl = scrapertools.find_single_match(enlace, '(?:"|)label(?:"|):\s*"([^"]+)')
        if not v_lbl: v_lbl = 'mp4'
        srcs.append([v_url, v_type, v_lbl])

    return srcs


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

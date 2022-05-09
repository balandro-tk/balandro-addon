# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://repelishd.me/'

player = 'https://player.repelishd.me'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )


def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if not headers: headers = {'Referer': host}

    if '/fecha/' in url: raise_weberror = False
    elif '/network/' in url: raise_weberror = False

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('repelishd', url, post=post, headers=headers, raise_weberror=raise_weberror).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'estrenos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + 'calidad/hd/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'destacadas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'serie/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'genero/serie-destacada/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por plataforma', action = 'plataformas', search_type = 'tvshow' ))

    return itemlist


def estrenos(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Estrenos 2021', action = 'list_all', url = host + 'categoria/estrenos-2021/' ))
    itemlist.append(item.clone( title = 'Estrenos 2020', action = 'list_all', url = host + 'categoria/estrenos-2020/' ))
    itemlist.append(item.clone( title = 'Estrenos 2019', action = 'list_all', url = host + 'categoria/estrenos-2019/' ))

    itemlist.append(item.clone( title = 'Otros estrenos en cines', action = 'list_all', url = host + 'calidad/cine/' ))

    return itemlist


def destacadas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Destacadas en HD', action = 'list_all', url = host + 'seccion/destacadas-hd/' ))

    itemlist.append(item.clone( title = 'Destacadas 2021', action = 'list_all', url = host + 'seccion/destacadas-2021/' ))
    itemlist.append(item.clone( title = 'Destacadas 2020', action = 'list_all', url = host + 'seccion/destacadas-2020/' ))
    itemlist.append(item.clone( title = 'Destacadas 2019', action = 'list_all', url = host + 'seccion/destacadas-2019/' ))
    itemlist.append(item.clone( title = 'Destacadas 2018', action = 'list_all', url = host + 'seccion/destacadas-2018/' ))

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

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '">Géneros<(.*?)>Años de Lanzamiento<')

    matches = scrapertools.find_multiple_matches(bloque, '<a href=(.*?)>(.*?)</a>')

    for url, title in matches:
        if '<div ' in title: continue

        url = url.strip()
        title = title.strip()

        if not url.startswith("http"): url = host[:-1] + url

        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    if item.search_type == 'movie': limit = 1949
    else: limit = 1999

    for x in range(current_year, limit, -1):
        url = host + 'fecha/' + str(x) + '/'

        itemlist.append(item.clone( title=str(x), url= url, action='list_all' ))

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

    if '<h2>Añadido recientemente' in data:
        bloque = scrapertools.find_single_match(data, '<h2>Añadido recientemente(.*?)">Géneros<')
    else:
        bloque = scrapertools.find_single_match(data, '</h1>(.*?)">Géneros<')

    matches = re.compile('<article(.*?)</article>').findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, '<a href=(.*?)>').strip()

        title = scrapertools.find_single_match(article, '<div class=title><h4>(.*?)</h4>')
        if not title:
            title = scrapertools.find_single_match(article, 'alt="(.*?)"')
            if not title: title = scrapertools.find_single_match(article, 'alt=(.*?)>')

        if not url or not title: continue

        tipo = 'tvshow' if '/serie/' in url else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, 'data-src=(.*?) alt=').strip()
        if thumb.startswith('//'): thumd = 'https:' + thumb

        qlty = scrapertools.find_single_match(article, '<span class=quality>(.*?)</span>')

        langs = []
        if '<div class=castellano></div>' in article: langs.append('Esp')
        if '<div class=latino></div>' in article: langs.append('Lat')
        if '<div class=subtitulado></div>' in article: langs.append('Vose')

        year = scrapertools.find_single_match(article, '</h3> <span>(.*?)</span>')
        if not year: year = '-'

        if '/serie/' in url:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, qualities=qlty, languages=', '.join(langs),
                                        fmt_sufijo=sufijo, contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))
        else:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title = title, thumbnail = thumb, qualities=qlty, languages=', '.join(langs),
                                        fmt_sufijo=sufijo, contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, r'<a class=arrow_pag href=([^>]+)><i id=nextpagination').strip()
        if not next_page: next_page = scrapertools.find_single_match(data, r'<span class=current>.*?<a href=(.*?) class=inactive').strip()

        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', url = next_page, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile("<span class=.*?se-t.*?>(.*?)</span>", re.DOTALL).findall(data)

    for season in matches:
        title = 'Temporada ' + season

        url = item.url

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = url
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, contentType = 'season', contentSeason = season ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    season = item.contentSeason

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<span class=.*?se-t.*?>" + str(season) + "</span>(.*?)</ul></div></div>")

    matches = re.compile("<li class=mark-(.*?)</div></li>").findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('RePelisHd', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for datos in matches[item.page * item.perpage:]:
        thumb = scrapertools.find_single_match(datos, "src=(.*?)>")
        if thumb.startswith('//'): thumd = 'https:' + thumb

        url = scrapertools.find_single_match(datos, " href=(.*?)>").strip()
        title = scrapertools.find_single_match(datos, " href=.*?>(.*?)</a>").strip()

        epis = scrapertools.find_single_match(datos, "<div class=numerando>(.*?)</div>")
        epis = epis.split('-')[1].strip()

        titulo = season + 'x' + epis + ' ' + title

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > (item.page + 1) * item.perpage:
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

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

    IDIOMAS = {'castellano': 'Esp', 'español': 'Esp', 'latino': 'Lat', 'subtitulado': 'Vose', 'sub español': 'Vose'}

    data = do_downloadpage(item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    patron = "<li id=player-option-(.*?)</span>"

    matches = scrapertools.find_multiple_matches(data, patron)

    ses = 0

    for options in matches:
        ses += 1

        dtype = scrapertools.find_single_match(data, "data-type=(.*?)data-post=").strip()
        dpost = scrapertools.find_single_match(data, "data-post=(.*?)data-nume=").strip()
        dnume = scrapertools.find_single_match(data, "data-nume=(.*?)>").strip()

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

        langs = []
        if 'Castellano' in options or 'Español' in options: langs.append('Esp')
        if 'Latino' in options: langs.append('Lat')
        if 'Subtitulado' in options: langs.append('Vose')

        data = do_downloadpage(url, headers = {'Referer': item.url})
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

        if 'IdiomaSet' in data:
            patron = 'onclick="IdiomaSet\(this, \'(\d)\'\);" class="select.*?"><span class="title"><img src="/assets/player/lang/([^.]+)'

            matches1 = scrapertools.find_multiple_matches(data, patron)

            for n, lang2 in matches1:
                data1 = scrapertools.find_single_match(data, '<div class="Player%s(.*?)</div></div>' % n)

                matches2 = scrapertools.find_multiple_matches(data1, "go_to_player\('([^']+).*?<span class=\"serverx\">([^<]+)")

                for embed, srv in matches2:
                    if srv.lower() == 'mePlay': continue
                    elif srv.lower() == 'stream': continue
                    elif srv.lower() == 'playsb': continue
                    elif srv.lower() == 'descargar': continue

                    if '/download/' in embed:
                        embed = embed.replace('/download/', '')
                        servidor = corregir_servidor(srv)
                    else:
                        embed = embed.replace('/playerdir/', '')
                        servidor = corregir_servidor(srv)

                    lang = IDIOMAS.get(lang2.lower(), lang2.lower())

                    itemlist.append(Item( channel = item.channel, action = 'play', url = embed, server = servidor, title = '', language = lang ))
        else:
            matches3 = scrapertools.find_multiple_matches(data, 'data-embed="([^"]+)".*?<span class="serverx">([^<]+)</span>')

            for embed, srv in matches3:
                if srv.lower() == 'mePlay': continue
                elif srv.lower() == 'stream': continue
                elif srv.lower() == 'playsb': continue

                if srv.lower() == 'descargar':
                    if not embed.startswith("http"):
                        embed = 'https://embeds.repelishd.me/redirect?url=' + embed
                        srv = 'directo'

                servidor = corregir_servidor(srv)

                itemlist.append(Item( channel = item.channel, action = 'play', url = embed, server = servidor, title = '', languages=', '.join(langs) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = ''

    if '/go.megaplay.cc/' in item.url or '/gcs.megaplay.cc/' in item.url:
        data = do_downloadpage(item.url)
        key, value = scrapertools.find_single_match(data, r'name="([^"]+)" value="([^"]+)"')

        if '/go.megaplay.cc/' in item.url: url_post = 'https://go.megaplay.cc/r.php'
        else: url_post = 'https://gcs.megaplay.cc/r.php'

        url = httptools.downloadpage(url_post, post={key: value}, follow_redirects=False).headers['location']

    elif '//embeds' in item.url:
        data = do_downloadpage(item.url)

        new_url = scrapertools.find_single_match(data, r'downloadurl.*?"(.*?)"')
        new_url = new_url.replace('/download?url=', '')

        if new_url:
            if not new_url.startswith("http"): new_url = 'https://embeds.repelishd.me/redirect?url=' + new_url

            data = do_downloadpage(new_url)

            new_url = scrapertools.find_single_match(data, r'downloadurl.*?"(.*?)"')

        if new_url: url = new_url

    else:
        url = player + '/playdir/' + item.url
        data = do_downloadpage(url.split('&')[0], headers={'Referer': url})

        url = scrapertools.find_single_match(data, r'<iframe .*?src="([^"]+)')

        if url == 'https://URL/NONE/':
            url = ''
            if item.server == 'uqload':
                code = scrapertools.find_single_match(data, r'file_code=(.*?)&hash')
                if code: url = 'https://uqload.com/embed-' + code + '.html'

        if url:
            if not url.startswith("http"):
                data = do_downloadpage(player + item.url, headers={'Referer': url})
                url = scrapertools.find_single_match(data, r'<iframe .*?src="([^"]+)')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'zplayer': url = url + '|' + player

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(url = url, server = servidor))

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

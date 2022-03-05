# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://pelisflix.li/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    if '/release/' in url: raise_weberror = False

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-peliculas-online-gratis/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver-series-online-gratis/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por productora', action = 'productora', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>GÉNEROS<(.*?)</ul>')

    matches = re.compile('<a href="([^"]+)">([^<]+)').findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title.capitalize(), action = 'list_all', url = url ))

    itemlist.append(item.clone( title = 'Western', action = 'list_all', url = host + 'genero/western/' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1959, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'release/' + str(x) + '/', action = 'list_all' ))

    return itemlist


def productora(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque =  scrapertools.find_single_match(data, '>PRODUCTORAS<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)".*?title">(.*?)</span>').findall(bloque)

    for url, title in matches:
        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h2 class="Title">(.*?)</h2>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')

        year = scrapertools.find_single_match(match, '<span class="Date">(.*?)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(match, '<span class="Qlty">(.*?)</span>')

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'tvshow':
            if not item.search_type == 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        if tipo == 'movie':
            if not item.search_type == 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_url = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="(.*?)"')
        if next_url:
            if '/page/' in next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_all', group = item.group, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('<section class="SeasonBx.*?<a href="(.*?)".*?<span>(.*?)</span>', re.DOTALL).findall(data)

    for url, tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = url
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    patron = '<tr class="Viewed">.*?<span class="Num">(.*?)</span>.*?<a href="(.*?)".*?<img src="(.*?)".*?<a href=.*?">(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PelisFlix', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for episode, url, thumb, title in matches[item.page * item.perpage:]:
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

    matches = scrapertools.find_multiple_matches(data, '<button  data-typ=(.*?)</button>')

    ses = 0

    for match in matches:
        ses += 1

        dkey = scrapertools.find_single_match(match, 'data-key="(.*?)"')
        dide = scrapertools.find_single_match(match, 'data-id="(.*?)"')

        if not dkey or not dide: continue

        lang = scrapertools.find_single_match(match, "</span>.*?<span>(.*?)</span>").lower().strip()

        if 'latino' in lang: lang = 'Lat'
        elif 'castellano' in lang or 'español' in lang: lang = 'Esp'
        elif 'subtitulado' in lang or 'vose' in lang: lang = 'Vose'
        else: lang = '?'

        qlty = scrapertools.find_single_match(match, "</span>.*?<span>.*?<span>(.*?)•")

        servidor = scrapertools.find_single_match(match, "</span>.*?<span>.*?<span>.*?•(.*?)</span>").strip().lower()

        servidor = servertools.corregir_servidor(servidor)

        #if servidor == 'dood': servidor = 'doodstream'
        if 'gounlimited' in servidor: continue

        if '"movie"' in match: dtype = "1"
        else: dtype = "2"

        url = host + '?trembed=%s&trid=%s&trtype=%s' % (dkey , dide, dtype)

        if 'vip' in servidor:
            data = httptools.downloadpage(url).data

            url = scrapertools.find_single_match(data, 'src="(.*?)"')

            data = httptools.downloadpage(url).data

            matches2 = re.compile("go_to_player\('([^']+)'\)", re.DOTALL).findall(data)
            for url in matches2:
                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url,
                                      language = lang, quality = qlty, other = servidor.capitalize() ))

            continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lang, quality = qlty ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if 'pelisflix' in url:
        data = do_downloadpage(url)

        url = scrapertools.find_single_match(data, 'src="(.*?)"')

        if url:
           id = scrapertools.find_single_match(url, r"\?h=([A-z0-9]+)")

           post = {'h': id}
           url = host + 'stream/r.php'

           url = httptools.downloadpage(url, post = post, follow_redirects=False).headers['location']

    if 'byegoto' in url:
        id = scrapertools.find_single_match(url, '=([^"]+)')

        post = {'url': id}
        url =  host + 'byegoto/rd.php'

        url = httptools.downloadpage(url, post = post).data

    if 'mega1080p' in url:
        from lib import jsunpack

        url = httptools.downloadpage(url).data

        pack = scrapertools.find_single_match(url, 'p,a,c,k,e,d.*?</script>')
        unpack = jsunpack.unpack(pack).replace('\\', '')

        url = scrapertools.find_single_match(unpack, "'file':'([^']+)'")

        url = url.replace("/master", "/720/720p")
        url = 'https://pro.mega1080p.club/' + url
        url += '|Referer=' + url

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        itemlist.append(item.clone(server = servidor, url = url))

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


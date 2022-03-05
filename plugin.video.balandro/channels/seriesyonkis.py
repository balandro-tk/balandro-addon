# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://seriesyonkis.cc/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('seriesyonkis', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone ( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone ( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone ( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Más vistas', action = 'list_all', url = host + 'mas-vistas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'DC comics', action = 'list_all', url = host + 'category/dc-comics/?tr_post_type=1', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Netflix', action = 'list_all', url = host + 'category/netflix/?tr_post_type=1', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone ( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host, search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'HBO', action = 'list_all', url = host + 'category/hbo/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Marvel', action = 'list_all', url = host + 'category/marvel/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Netflix', action = 'list_all', url = host + 'category/netflix/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque =  scrapertools.find_single_match(data, '>Categories<(.*?)</ul>')

    matches = re.compile('<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(bloque)

    for url, tit in matches:
        if tit == 'Actualizadas': continue
        elif tit == 'DC comics': continue
        elif tit == 'HBO': continue
        elif tit == 'Netflix': continue
        elif tit == 'News': continue

        if item.search_type == 'movie':
            if tit == 'Anime': continue
            elif tit == 'Marvel': continue
            elif tit == 'Reality': continue
            elif tit == 'Talk': continue

            url += '?tr_post_type=1'
        else:
            url += '?tr_post_type=2'

        itemlist.append(item.clone( title = tit.capitalize(), url = url, action = 'list_all' ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque =  scrapertools.find_single_match(data, '</h1>(.*?)<div id="categories')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h3 class="Title">(.*?)</h3>')
        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, 'src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(article, 'class="Date AAIco-date_range">(\d+)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)</span>')

        tipo = 'movie' if '/movie/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if tipo == 'movie':
            if not item.search_type == 'all':
               if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo=sufijo, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))

        if tipo == 'tvshow':
            if not item.search_type == 'all':
               if item.search_type == 'movie': continue

            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, fmt_sufijo=sufijo,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data, 'class="page-numbers current">.*?href="([^"]+)')
        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('data-tab="(.*?)"', re.DOTALL).findall(data)

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

    bloque =  scrapertools.find_single_match(data, 'data-tab="' + str(item.contentSeason) + '"(.*?)</table>')

    if not 'data-src=&quot;' in bloque:
        patron = '<span class="Num">(.*?)</span>.*?<a href="(.*?)".*?src="(.*?)".*?<td class="MvTbTtl">.*?">(.*?)</a>'
    else:
        patron = '<span class="Num">(.*?)</span>.*?<a href="(.*?)".*?src=(.*?)alt=.*?<td class="MvTbTtl">.*?">(.*?)</a>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('SeriesYonkis', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for epis, url, thumb, title in matches[item.page * item.perpage:]:
        title = item.contentSeason + 'x' + epis + ' ' + title

        if thumb.startswith('//'): thumb = 'https:' + thumb
        thumb = thumb.replace('&quot;', '').strip()

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, contentType = 'episode', contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color= 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'ESP': 'Esp', 'LAT': 'Lat', 'ESPSUB': 'Vose', 'PLAYER': 'Vose', 'ENG': 'VO'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'data-tplayernv="(.*?)".*?</img></span>(.*?)</span>')

    ses = 0

    for opt, lang in matches:
        ses += 1

        lang = lang.strip()

        url = scrapertools.find_single_match(data, 'id="' + str(opt) + '".*?<iframe.*?src="(.*?)"')

        if not url or url.startswith('//'):
           url = scrapertools.find_single_match(data, 'id="' + str(opt) + '".*?iframe.*?src=&quot;(.*?)&quot;')

        if url:
            if '/movie/' in item.url:
                itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, language = IDIOMAS.get(lang, lang) ))

            else:
                url = url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')
                data2 = do_downloadpage(url)

                url = scrapertools.find_single_match(data2, '<iframe.*?src="([^"]+)')

                if '/hqq.' in url or '/waaw.' in url or '/netu.' in url: continue
                elif 'openload' in url: continue
                elif 'powvideo' in url: continue
                elif 'streamplay' in url: continue
                elif 'rapidvideo' in url: continue
                elif 'streamango' in url: continue
                elif 'verystream' in url: continue
                elif 'vidtodo' in url: continue

                if not 'pelispluss' in url:
                    itemlist.append(Item( channel=item.channel, action='play', server='directo', title='', url=url, language=IDIOMAS.get(lang, lang) ))

                else:
                    data3 = do_downloadpage(url)
                    matches2 = scrapertools.find_multiple_matches(data3, "go_to_player.*?'(.*?)'.*?<span>(.*?)</span>.*?<p>(.*?)-.*?</p>")

                    for url, servidor, lng in matches2:
                        servidor = servidor.replace('.com', '').replace('.net', '').replace('.cc', '').replace('.to', '').replace('.sx', '')

                        lng = lng.strip()
                        if lng == 'Espanol': lng = 'Esp'
                        elif lng == 'Latino': lng = 'Lat'
                        elif lng == 'Subtitulado': lng = 'Vose'
                        elif lng == 'Ingles': lng = 'VO'

                        itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = lng ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')

    url = item.url

    if item.server == 'directo':
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
           data = do_downloadpage(url)
           url = scrapertools.find_single_match(data, '<iframe.*?src="([^"]+)')
    else:
        if 'pelispluss' in url:
            vid = scrapertools.find_single_match(url, 'h=(.*?)$')

            post = {'h': vid}
            url = httptools.downloadpage('https://pelispluss.net/sc/r.php', post = post, follow_redirects=False).headers.get('location', '')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'
        elif 'openload' in url or 'powvideo' in url or 'streamplay' in url or 'rapidvideo' in url or 'streamango' in url or 'verystream' in url or 'vidtodo' in url:
            return 'Servidor [COLOR yellow]NO soportado[/COLOR]'

        if url.startswith('//'): url = 'https:' + url

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor:
            url = servertools.normalize_url(servidor, url)
            itemlist.append(item.clone( url=url, server=servidor ))

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

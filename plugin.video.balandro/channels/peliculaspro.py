# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://peliculaspro.net/'


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
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

    itemlist.append(item.clone ( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone ( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Estrenos', action = 'list_all', url = host + 'category/uncategorized/', search_type = 'movie' ))

    itemlist.append(item.clone ( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    bloque = scrapertools.find_single_match(data, '>Categorías<(.*?)</ul>')

    matches = re.compile('<a href="([^"]+)">([^<]+)').findall(bloque)

    for url, title in matches:
        if title == 'Estrenos': continue

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    bloque =  scrapertools.find_single_match(data, '</h1>(.*?)>Register<')

    matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2 class="entry-title">(.*?)</h2>')
        if not url or not title: continue

        tipo = 'movie' if '/pelicula/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        if thumb.startswith('//'): thumb = 'https:' + thumb

        year = scrapertools.find_single_match(article, '<span class="year">(\d+)</span>')
        if not year: year = '-'

        qlty = scrapertools.find_single_match(article, '<span class="Qlty">([^<]+)</span>')

        if '/pelicula/' in url:
            if item.search_type != 'all':
                if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, fmt_sufijo = sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            if item.search_type != 'all':
                if item.search_type == 'movie': continue

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '>NEXT<' in data:
            next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?</a>.*?href="([^"]+)')
            if next_page:
                if '/page/' in next_page:
                    itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    temporadas = re.compile('<div class="aa-drp choose-season">.*?<a href="(.*?)".*?inline">(.*?)</dt>', re.DOTALL).findall(data)

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

    return sorted(itemlist, key=lambda x: x.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, 'data-tab="' + str(item.contentSeason) + ".*?</span>(.*?)</div></div>")

    matches = re.compile('<span class="num-epi">.*?x(.*?)</span><h2 class="entry-title">(.*?)</h2>.*?<a href="(.*?)".*?src="(.*?)"', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PeliculasPro', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for epis, title, url, thumb in matches[item.page * item.perpage:]:
        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'Sub Español': 'Vose'}

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'id="options-(.*?)".*?<iframe .*?src="(.*?)"')

    i = 0

    for opt, url in matches:
        i += 1
        srv, lang = scrapertools.find_single_match(data, 'href="#options-' + str(opt)+ '">.*?<span class="server">(.*?)-(.*?)</span>')

        srv = srv.lower().strip()

        lang = lang.strip()
        if '</td>' in lang: lang = scrapertools.find_single_match(lang, '(.*?)</td>')

        idioma = IDIOMAS.get(lang, lang)

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor).lower()

        other = ''
        if servidor:
           if srv == 'streamz':
               servidor = srv
           elif srv == 'peliculaspro':
               other = 'fembed' + '-' + str(i)
           elif srv == 'streamcrypt':
               other = srv + '-' + str(i)
           else:
               other = srv.lower() + '-' + str(i)

        itemlist.append(Item( channel = item.channel, action = 'play', title = '', server = servidor, url = url, other = other, language = idioma ))

    # ~ downloads recatpcha

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('&amp;#038;', '&').replace('&#038;', '&').replace('&amp;', '&')
    item.url = item.url.replace('amp;#038;', '&').replace('#038;', '&').replace('amp;', '&')

    url = item.url

    if item.url.startswith(host):
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<iframe.*?src="(.*?)"')

        url = url.replace('//peliculaspro.biz/', '//femax20.com/')

    if url.startswith('https://streamcrypt.net/'):
        url = httptools.downloadpage(url, follow_redirects=False).headers.get('location', '')
        if url:
            url = url.replace('?id=', '?p=2&id=')
            url = httptools.downloadpage(url, follow_redirects=False).headers.get('location', '')
        else:
            data = do_downloadpage(url)
            url = scrapertools.find_single_match(data, "window.open.*?'(.*?)'")

    if url:
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

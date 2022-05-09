# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, jsontools, servertools, tmdb


host = 'https://www.cliver.to/'


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )


def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ timeout
    timeout = 30

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
    data = httptools.downloadpage_proxy('cliver', url, post=post, headers=headers, timeout=timeout).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers, timeout=timeout).data
                data = httptools.downloadpage_proxy('cliver', url, post=post, headers=headers, timeout=timeout).data
        except:
            pass

    return data


def mainlist(item):
    return mainlist_pelis(item)

    # ~ las series las han quitado en la web
    # ~ logger.info()
    # ~ itemlist = []

    # ~ itemlist.append(item_configurar_proxies(item))

    # ~ itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    # ~ itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    # ~ itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    # ~ return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host, 
                                search_type = 'movie', tipo = 'index', pagina = 0 ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'peliculas/estrenos/', 
                                search_type = 'movie', tipo = 'estrenos', pagina = 0 ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'peliculas/mas-vistas/', 
                                search_type = 'movie', tipo = 'mas-vistas', pagina = 0 ))

    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas/tendencias/', 
                                search_type = 'movie', tipo = 'peliculas-tendencias', pagina = 0 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', 
                                search_type = 'tvshow', tipo = 'indexSeries', pagina = 0 ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_episodes', url = host + 'series/nuevos-capitulos/', 
                                search_type = 'tvshow', tipo = 'nuevos-capitulos', pagina = 0 ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'series/mas-vistas/', 
                                search_type = 'tvshow', tipo = 'mas-vistas-series', pagina = 0 ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por plataforma', action = 'networks', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    url = host if item.search_type == 'movie' else host + 'series/'
    data = do_downloadpage(url)

    bloque = scrapertools.find_single_match(data, '<div class="generos">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">\s*<span class="cat">([^<]+)')
    for url, title in matches:
        adicional = scrapertools.find_single_match(url, '/genero/([^/]+)')
        tipo = 'genero' if item.search_type == 'movie' else 'generosSeries'

        itemlist.append(item.clone( action="list_all", title=title, url=url, tipo=tipo, adicional=adicional, pagina=0 ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    url = host if item.search_type == 'movie' else host + 'series/'
    data = do_downloadpage(url)

    bloque = scrapertools.find_single_match(data, '<div class="anios">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)">([^<]+)')
    for url, title in matches:
        adicional = scrapertools.find_single_match(url, '/anio/([^/]+)')
        tipo = 'anio' if item.search_type == 'movie' else 'anioSeries'

        itemlist.append(item.clone( action="list_all", title=title, url=url, tipo=tipo, adicional=adicional, pagina=0 ))

    return itemlist


def networks(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'series/')

    bloque = scrapertools.find_single_match(data, '<div class="networks">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)" class="[^"]*" title="([^"]+)')
    for url, title in matches:
        adicional = scrapertools.find_single_match(url, '/network/([^/]+)')

        itemlist.append(item.clone( action="list_all", title=title, url=url, tipo='networkSeries', adicional=adicional, pagina=0 ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.pagina: item.pagina = 0

    if item.pagina == 0 and item.tipo == 'buscador':
        httptools.save_cookie('tipo_contenido', 'peliculas', host.replace('https://', '')[:-1])
        data = do_downloadpage(item.url, headers={'Referer': host})
    else:
        post = {'tipo': item.tipo, 'pagina': item.pagina}
        if item.adicional: post['adicional'] = item.adicional
        data = do_downloadpage(host+'frm/cargar-mas.php', post=post, headers={'Referer': host})

    matches = re.compile('<article class="contenido-p">(.*?)</article>', re.DOTALL).findall(data)

    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()
        year = scrapertools.find_single_match(article, '<span>(\d{4})')
        if not year: year = '-'

        if item.search_type == 'movie':
            if '<div class="es"' in article: article = article.replace('<div class="es"', '<div class="Esp"')
            if '<div class="lat"' in article: article = article.replace('<div class="lat"', '<div class="Lat"')
            if '<div class="vose"' in article: article = article.replace('<div class="vose"', '<div class="Vose"')

            langs = scrapertools.find_multiple_matches(article, '<div class="([^"]+)"></div>')

            id_pelicula = scrapertools.find_single_match(thumb, '/(\d+)_min')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, id_pelicula = id_pelicula,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year}, languages = ', '.join(langs) ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, 
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    num = 12 if item.tipo.startswith('index') else 18
    if len(matches) >= num:
        itemlist.append(item.clone( title='Siguientes ...', pagina = item.pagina + 1, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="menu-item" id="temporada(\d+)">', re.DOTALL).findall(data)

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)

def episodios(item):
    logger.info()
    itemlist=[]

    color_lang = config.get_setting('list_languages_color', default='red')

    if not item.page: item.page = 0
    perpage = 50

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="mic">(.*?)<i class="fa fa-play">', re.DOTALL).findall(data)

    for article in matches[item.page * perpage:]:
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        plot = scrapertools.find_single_match(article, '<p>(.*?)</p>').strip()

        season = scrapertools.find_single_match(article, 'data-numtemp="([^"]+)')
        episode = scrapertools.find_single_match(article, 'data-numcap="([^"]+)')
        title = scrapertools.find_single_match(article, 'data-titulo="([^"]+)')

        if not item.contentSeason: continue
        elif not str(item.contentSeason) == season: continue

        langs = []
        for opc in ['data-url-es', 'data-url-es-la', 'data-url-vose', 'data-url-en']:
            url = scrapertools.find_single_match(article, '%s="([^"]+)' % opc)
            if url: langs.append(opc.replace('data-url-', '').replace('es-la', 'lat').replace('es-es', 'esp').capitalize())

        if langs: title += ' [COLOR %s][%s][/COLOR]' % (color_lang, ', '.join(langs))

        itemlist.append(item.clone( action='findvideos', title = title, thumbnail=thumb, plot = plot,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, text_color='coral' ))

    return itemlist


def list_episodes(item):
    logger.info()
    itemlist = []
    if not item.pagina: item.pagina = 0
    color_lang = config.get_setting('list_languages_color', default='red')

    post = {'tipo': item.tipo, 'pagina': item.pagina}
    data = do_downloadpage(host+'frm/cargar-mas.php', post=post)

    matches = re.compile('<article class="contenido-p">(.*?)</article>', re.DOTALL).findall(data)
    for article in matches:

        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        show = scrapertools.find_single_match(article, '<h2>(.*?)</h2>').strip()
        title = scrapertools.find_single_match(article, '<span>(.*?)</span>')
        langs = scrapertools.find_multiple_matches(article, '<div class="([^"]+)"></div>')

        s_e = scrapertools.find_single_match(url, '/(\d+)/(\d+)/')
        if not s_e: continue

        titulo = '%s - %s' % (show, title)
        if langs: titulo += ' [COLOR %s][%s][/COLOR]' % (color_lang, ', '.join(langs))

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, 
                                    contentType='episode', contentSerieName=show, contentSeason = s_e[0], contentEpisodeNumber = s_e[1] ))

    tmdb.set_infoLabels(itemlist)

    if len(matches) >= 18:
        itemlist.append(item.clone( title='Siguientes ...', pagina = item.pagina + 1, action='list_episodes', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'es_la': 'Lat', 'es': 'Esp', 'vose': 'Vose', 'en': 'VO'}

    ses = 0

    if item.contentType == 'movie':
        if not item.id_pelicula:
            data = do_downloadpage(item.url)
            item.id_pelicula = scrapertools.find_single_match(data, 'Idpelicula\s*=\s*"([^"]+)')

        header = {'Referer': item.url}
        data = do_downloadpage(host + 'frm/obtener-enlaces-pelicula.php', post={'pelicula': item.id_pelicula}, headers=header)

        enlaces = jsontools.load(data)
        for lang in enlaces:
            ses += 1

            for it in enlaces[lang]:
                servidor = 'directo' if it['reproductor_nombre'] in ['SuperVideo', 'FastPlayer'] else it['reproductor_nombre'].lower()
                servidor = servertools.corregir_servidor(servidor)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor,
                                      title = '', url = 'https://directv.clivertv.to/getFile.php?hash=' + it['token'],
                                      language = IDIOMAS.get(lang, lang), other = it['reproductor_nombre'] if servidor == 'directo' else '' ))

    else:
        data = do_downloadpage(item.url)

        data = scrapertools.find_single_match(data, 'data-numcap="%s" data-numtemp="%s"(.*?)>' % (item.contentEpisodeNumber, item.contentSeason))

        for opc in ['data-url-es', 'data-url-es-la', 'data-url-vose', 'data-url-en']:
            ses += 1

            url = scrapertools.find_single_match(data, '%s="([^"]+)' % opc)
            if url:
                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)
                if not servidor or servidor == 'directo': continue

                lang = opc.replace('data-url-', '').replace('-', '_')
                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = IDIOMAS.get(lang, lang) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.url.startswith('https://directv.clivertv.to/getFile.php'):
        url = item.url.split('?')[0]
        post = item.url.split('?')[1]

        url = url.replace('/directv.clivertv.to/', '/directv.cliver.to/')

        data = do_downloadpage(url, post=post, headers={'Referer': host})
        data = data.replace('\\/', '/')

        try:
            dom, vid = scrapertools.find_single_match(data, '(https://[^/]+)/player/([^&]+)')
            url = '%s/hls/%s/%s.m3u8' % (dom, vid, vid)
        except:
            url = scrapertools.find_single_match(data, '"url":"([^"]+)').replace(' ', '%20')

        if 'id=' in url:
            vid = scrapertools.find_single_match(url, 'id=([^&]+)')
            if vid:
                dom = '/'.join(url.split('/')[:3])
                url = dom + '/hls/' + vid + '/' + vid + '.playlist.m3u8'

                data = httptools.downloadpage(url).data

                matches = scrapertools.find_multiple_matches(data, 'RESOLUTION=\d+x(\d+)\s*(.*?\.m3u8)')
                if matches:
                    if 'xtream.to/' in url:
                        for res, url in sorted(matches, key=lambda x: int(x[0]), reverse=True):
                            itemlist.append(item.clone(url = dom + url, server = 'm3u8hls'))
                            break
                    else:
                        for res, url in sorted(matches, key=lambda x: int(x[0])):
                            itemlist.append([res + 'p', dom + url])
                    return itemlist

            else:
                url = None

    else:
        url = item.url

    if url:
        itemlist.append(item.clone(url=url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        tipo = 'buscador' if item.search_type == 'movie' else 'buscadorSeries'
        return list_all(item.clone( pagina=0, tipo=tipo, adicional=texto.replace(" ", "+"), url=host+'buscar/?txt=' + texto.replace(" ", "+") ))
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

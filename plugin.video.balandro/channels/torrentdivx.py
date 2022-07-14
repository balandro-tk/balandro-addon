# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import re, os

from platformcode import logger, config, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools

from lib import decrypters


host = 'https://www1.ditorrent.com/'


# ~  las series con recaptcha
# ~  04/2022 algunas pelis tambien con recaptcha


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['http://www.torrentdivx.net/', 'https://www.torrentdivx.com/', 'https://www.ditorrent.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
    data = httptools.downloadpage_proxy('torrentdivx', url, post=post, headers=headers).data

    if '<title>You are being redirected...</title>' in data:
        try:
            from lib import balandroresolver
            ck_name, ck_value = balandroresolver.get_sucuri_cookie(data)
            if ck_name and ck_value:
                httptools.save_cookie(ck_name, ck_value, host.replace('https://', '')[:-1])
                # ~ data = httptools.downloadpage(url, post=post, headers=headers).data
                data = httptools.downloadpage_proxy('torrentdivx', url, post=post, headers=headers).data
        except:
            pass

    return data


def mainlist(item):
    return mainlist_pelis(item)

    # ~ logger.info()
    # ~ itemlist = []

    # ~ itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    # ~ itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    # ~ itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))

    # ~ return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'tag/estreno/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por calidad', action = 'calidades', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title='Catálogo', action='list_all', url= host + 'tvshows/', search_type = 'tvshow' ))

    return itemlist


def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Castellano', action='list_all', url=host + 'tag/castellano/' ))
    itemlist.append(item.clone( title='Latino', action='list_all', url=host + 'tag/latino/' ))
    itemlist.append(item.clone( title='Subtitulado', action='list_all', url=host + 'tag/subtitulado/' ))

    return itemlist


def calidades(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='En Magnet', action='list_all', url=host + 'tag/magnet/', search_type = 'movie' ))
    itemlist.append(item.clone( title='En Torrent', action='list_all', url=host + 'tag/torrent/', search_type = 'movie' ))

    itemlist.append(item.clone( title='En HdRip', action='list_all', url=host + 'tag/hdrip/', search_type = 'movie' ))
    itemlist.append(item.clone( title='En 720p', action='list_all', url=host + 'tag/720p/', search_type = 'movie' ))
    itemlist.append(item.clone( title='En 1080p', action='list_all', url=host + 'tag/1080p/', search_type = 'movie' ))
    itemlist.append(item.clone( title='En 4K', action='list_all', url=host + 'tag/4k/', search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host + 'tag/estreno/')

    bloque = scrapertools.find_single_match(data, '>Géneros<(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="(.*?)">(.*?)</a>')

    for url, title in matches:
        itemlist.append(item.clone( action='list_all', title=title, url=url ))

    return itemlist


def list_all(item): 
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<h1>(.*?)>TOP ESTRENOS<')
    if not bloque: bloque = scrapertools.find_single_match(data, '</h2>(.*?)>TOP ESTRENOS<')
    if not bloque: bloque = scrapertools.find_single_match(data, '<h1>(.*?)>Géneros<')

    matches = re.compile('<li class="xxx TPostMv" id="post-(.*?)</div></div></li>', re.DOTALL).findall(bloque)
    if not matches: matches = re.compile('<article(.*?)</article>', re.DOTALL).findall(bloque)

    for article in matches:
        url = scrapertools.find_single_match(article, '<a href="(.*?)"')

        title = scrapertools.find_single_match(article, '<h2 class="Title">(.*?)</h2>')
        if not title: title = scrapertools.find_single_match(article, 'alt="(.*?)"')
        if not title: title = scrapertools.find_single_match(article, '<h3>(.*?)</h3>')

        if not url or not title: continue

        thumb = scrapertools.find_single_match(article, 'data-src="(.*?)"')
        if not thumb: thumb = scrapertools.find_single_match(article, '<img src="(.*?)"')

        year = scrapertools.find_single_match(article, '<span class="Date AAIco-date_range">(\d{4})</span>').strip()
        if not year: year = scrapertools.find_single_match(article, '<span class="wdate">(.*?)</span>')

        if year: title = title.replace('(%s)' % year, '').strip()
        else:  year = '-'

        plot = scrapertools.find_single_match(article, '<p>(.*?)</p>')

        tipo = 'tvshow' if '/tvshows/' in url else 'movie'

        if tipo == 'movie':
            qlty = scrapertools.find_single_match(article, '<span class="quality">(.*?)</span>')

            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=qlty, 
                                        contentType='movie', contentTitle=title, infoLabels={'year': year, 'plot': plot} ))
        else:
            itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=title, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    next_page = scrapertools.find_single_match(data, '<a class="page-link current".*?<a href="(.*?)"')
    if not next_page: next_page = scrapertools.find_single_match(data, '<span class="current">.*?' + "<a href='(.*?)'")

    if next_page:
       if '/page/' in next_page:
           itemlist.append(item.clone (url = next_page, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile("domain=utorrent.com.*?Temporada (\d+)", re.DOTALL).findall(data)

    for numtempo in matches:
        title = 'Temporada ' + numtempo

        itemlist.append(item.clone( action = 'findvideos', title = title, contentType = 'season', contentSeason = numtempo, contentEpisodeNumber = numtempo))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def puntuar_calidad(txt):
    txt = txt.replace(' ', '').replace('-', '').lower()

    orden = ['cam',
          'ts',
          'webdl',
          'webrip',
          'bdscr',
          'hdtv',
          'hc720p',
          'bdrip',
          'dvdrip',
          'hdrip',
          '720p',
          'hd720p',
          '1080p',
          'fullhd',
          'hd1080p',
          'hd2160p',
          '2160p',
          '4khd2160p',
          '4k']

    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Castellano': 'Esp', 'Latino': 'Lat', 'V.O. Subtitulado': 'Vose', 'Version Original': 'VO',
               'Subtitulo Español': 'Vose', 'Version Original +Sub': 'VOS', 'Latino - Varios': 'Varios', 'Español latino': 'Lat'}

    data = do_downloadpage(item.url)

    bloque = scrapertools.find_single_match(data, "<div class='links_table'>(.*?)</table>")

    matches = scrapertools.find_multiple_matches(bloque, '<tr(.*?)</tr>')

    ses = 0

    for enlace in matches:
        ses += 1

        if '<th' in enlace or 'torrent' not in enlace: continue
        if "id='link-fake'" in enlace: continue

        url = scrapertools.find_single_match(enlace, " href='([^']+)")
        if not url: continue

        if '&url=' in url:
            url = scrapertools.find_single_match(url, "&url=(.*?)$")

        tds = scrapertools.find_multiple_matches(enlace, '<td>(.*?)</td>')
        qlty = scrapertools.find_single_match(tds[1], "<strong class='quality'>([^<]+)")
        lang = tds[2]

        other = tds[3] if tds[3] != '----' else ''
        if other == 'No Aplica': other = '?'

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'torrent', title = '', url = url,
                              language = IDIOMAS.get(lang,lang), quality = qlty, quality_num = puntuar_calidad(qlty), other = other ))

    if len(itemlist) == 0:
        matches = scrapertools.find_multiple_matches(data, ' href="(magnet[^"]+)')
        for url in matches:
            itemlist.append(Item( channel = item.channel, action = 'play', server = 'torrent', title = '', url = url ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if '&urlb64=' in item.url:
        import base64

        url = scrapertools.find_single_match(item.url, '&urlb64=(.*?)$')
        url = base64.b64decode(url)

        if url: item.url = url

    if item.url.startswith(host) and '/links/' in item.url:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, '<a id="link" rel="nofollow" href="([^"]+)')

        if '/www.pastexts' in url or '/tmearn' in url or '/sturl' in url or '/uii' in url or '/down.fast-' in url or '/adshort' in url or '/passgen' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        if url.startswith('magnet:') or url.endswith('.torrent'):
            if config.get_setting('proxies', item.channel, default=''):
                if PY3:
                    from core import requeststools
                    data = requeststools.read(url, 'torrentdivx')
                else:
                    data = do_downloadpage(url)

                if data:
                    import os

                    file_local = os.path.join(config.get_data_path(), "temp.torrent")
                    with open(file_local, 'wb') as f: f.write(data); f.close()

                    itemlist.append(item.clone( url = file_local, server = 'torrent' ))
            else:
                itemlist.append(item.clone( url = url, server = 'torrent' ))

            return itemlist

        if url:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            url = servertools.normalize_url(servidor, url)

            if servidor and servidor != 'directo':
                itemlist.append(item.clone( url = url, server = servidor ))

    if not item.url.endswith('.torrent'):
        host_torrent = host[:-1]
        url_base64 = decrypters.decode_url_base64(item.url, host_torrent)

        if url_base64.endswith('.torrent'): item.url = url_base64

    if item.url.endswith('.torrent'):
        if PY3:
            from core import requeststools
            data = requeststools.read(item.url, 'torrentdivx')
        else:
            data = do_downloadpage(item.url)

        if data:
            try:
               if 'Página no encontrada</title>' in str(data):
                   platformtools.dialog_ok('DivxTotal', '[COLOR yellow]Archivo no encontrado[/COLOR]')
                   return itemlist
            except:
               pass

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))


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

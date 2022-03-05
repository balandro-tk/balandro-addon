# -*- coding: utf-8 -*-

import re

from platformcode import logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://playview.io/'


perpage = 20

# En la web: No hay acceso a serie solamente a serie+temporada


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None, follow_redirects=True, only_headers=False):
    # ~ resp = httptools.downloadpage(url, post=post, follow_redirects=follow_redirects, only_headers=only_headers)
    resp = httptools.downloadpage_proxy('playview', url, post=post, follow_redirects=follow_redirects, only_headers=only_headers)

    if only_headers: return resp.headers
    return resp.data


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas-online', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'estrenos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series-online', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Animadas', action = 'list_all', url = host + 'series-animadas-online', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Anime', action = 'list_all', url = host + 'anime-online', search_type = 'tvshow' ))

    return itemlist


def estrenos(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)
    previous_year = current_year - 1

    itemlist.append(item.clone( title = 'Estrenos ' + str(current_year), action = 'list_all', url = host + 'estrenos-' + str(current_year), 
                                search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Estrenos ' + str(previous_year), action = 'list_all', url = host + 'estrenos-' + str(previous_year),
                                search_type = 'movie' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(host)

    patron = '<li><a href="(%s[^"]+)">([^<]+)</a></li>' % (host + 'peliculas-online/')
    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, title in matches:
        itemlist.append(item.clone( action="list_all", title=title.strip(), url=url ))

    return sorted(itemlist, key=lambda it: it.title)

def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1935, -1):
        itemlist.append(item.clone( title = str(x), url = host + 'estrenos-' + str(x), action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="spotlight_image lazy"(.*?)<div class="playRing">', re.DOTALL).findall(data)

    if item.search_type != 'all':
        matches = list(filter(lambda x: (' class="info-series"' not in x and item.search_type == 'movie') or \
                                   (' class="info-series"' in x and item.search_type == 'tvshow'), matches))

    num_matches = len(matches)

    for article in matches[item.page * perpage:]:
        tipo = 'tvshow' if ' class="info-series"' in article else 'movie'
        sufijo = '' if item.search_type != 'all' else tipo

        thumb = scrapertools.find_single_match(article, ' data-original="([^"]+)"')
        title = scrapertools.find_single_match(article, '<div class="spotlight_title">(.*?)</div>').strip()
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        year = scrapertools.find_single_match(article, '<span class="slqual sres">(\d{4})</span>')
        quality = 'HD' if '<span class="slqual-HD">HD</span>' in article else ''

        if 'data-cfemail' in title: title = scrapertools.clean_cfemail(title)

        if tipo == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb, qualities=quality, fmt_sufijo=sufijo,
                                        contentType='movie', contentTitle=title, infoLabels={'year': year} ))
        else:
            title = scrapertools.find_single_match(title, '(.*?)<br').strip()
            title = title[:1].upper() + title[1:]

            season = scrapertools.find_single_match(url, '-temp-(\d+)$')
            if season:
                titulo = '%s [COLOR gray](Temporada %s)[/COLOR]' % (title, season)
                itemlist.append(item.clone( action='episodios', url=url, title=titulo, thumbnail=thumb, qualities=quality, fmt_sufijo=sufijo, 
                                            contentType='season', contentSerieName=title, contentSeason=season, infoLabels={'year': year} ))
            else:
                itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb, qualities=quality, fmt_sufijo=sufijo, 
                                            contentType='tvshow', contentSerieName=title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title='Siguientes ...', page=item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_page_link = scrapertools.find_single_match(data, '<a href="([^"]+)" class="page-link" aria-label="Next"')
        if next_page_link:
            itemlist.append(item.clone( title='Siguientes ...', url=next_page_link, page=0, action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = scrapertools.find_multiple_matches(data, 'class="overviewPlay playLink" href="([^"]+)')

    #  cuantas temporadas
    tot_temp = 0

    for url in matches:
        season = scrapertools.find_single_match(url, '-temp-(\d+)$')
        if not season: continue

        tot_temp += 1
        if tot_temp > 1: break

    for url in matches:
        season = scrapertools.find_single_match(url, '-temp-(\d+)$')
        if not season: continue

        title = 'Temporada ' + season

        if tot_temp == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.url = url
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, url = url, contentType = 'season', contentSeason = season ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)

    dataid = scrapertools.find_single_match(data, 'data-id="([^"]+)"')
    datatype = '1'

    post = 'set=LoadOptionsEpisode&action=EpisodesInfo&id=%s&type=%s' % (dataid, datatype)
    data = do_downloadpage(host + 'playview', post=post)

    patron = ' data-episode="(\d+)"'
    patron += '.*?url\(([^)]+)\)'
    patron += '.*?<p class="ellipsized">(.*?)</p>'
    patron += '.*?<div class="episodeSynopsis">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PlayView', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for episode, thumb, title, plot in matches[item.page * item.perpage:]:
        titulo = '%sx%s %s' % (item.contentSeason, episode, title)
        itemlist.append(item.clone( action='findvideos', title=titulo, thumbnail=thumb, plot=plot, dataid=dataid, datatype=datatype,
                                    contentType='episode', contentEpisodeNumber=episode ))

        if len(itemlist) >= item.perpage:
            break

    if len(matches) == 0:
        post = 'set=LoadOptionsEpisode&action=EpisodeList&id=%s&type=%s' % (dataid, datatype)
        data = do_downloadpage(host + 'playview', post=post)

        patron = ' data-episode="(\d+)" value="[^"]*" title="([^"]+)'
        matches = re.compile(patron, re.DOTALL).findall(data)

        for episode, title in matches:
            title = re.sub('^\d+\s*-', '', title).strip()
            titulo = '%sx%s %s' % (item.contentSeason, episode, title)
            itemlist.append(item.clone( action='findvideos', title=titulo, dataid=dataid, datatype=datatype,
                                        contentType='episode', contentEpisodeNumber=episode ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['CAM', 'TS', 'TSHQ', 'SD', 'DVDRip', 'HDTC', 'HDLine', 'HDLine 720p', 'HD 720p', 'HD 1080p']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1



def corregir_servidor(servidor):
    servidor = servertools.corregir_servidor(servidor)
    if servidor == 'youtvgratis': return 'fembed'
    return servidor


def findvideos(item):
    logger.info()
    itemlist = []

    IDIOMAS = {'Latino': 'Lat', 'Español': 'Esp', 'Subtitulado': 'Vose'}

    if item.dataid:
        tipo = item.datatype
        post = 'set=LoadOptionsEpisode&action=Step1&id=%s&type=%s&episode=%s' % (item.dataid, item.datatype, item.contentEpisodeNumber)
    else:
        data = do_downloadpage(item.url)

        dataid = scrapertools.find_single_match(data, 'data-id="([^"]+)"')
        tipo = 'Movie'
        post = 'set=LoadOptions&action=Step1&id=%s&type=%s' % (dataid, tipo)

    data = do_downloadpage(host + 'playview', post=post)
    
    calidades = scrapertools.find_multiple_matches(data, 'data-quality="([^"]+)"')
    for calidad in calidades:
        if item.dataid:
            post = 'set=LoadOptionsEpisode&action=Step2&id=%s&type=%s&quality=%s&episode=%s' % (item.dataid, item.datatype, calidad.replace(' ', '+'), item.contentEpisodeNumber)
        else:
            post = 'set=LoadOptions&action=Step2&id=%s&type=%s&quality=%s' % (dataid, tipo, calidad.replace(' ', '+'))
        data = do_downloadpage(host + 'playview', post=post)

        enlaces = scrapertools.find_multiple_matches(data, 'data-id="([^"]+)">\s*<h4>([^<]+)</h4>\s*<small><img src="https://www\.google\.com/s2/favicons\?domain=([^"]*)')
        for linkid, lang, servidor in enlaces:
            servidor = servidor.replace('https://', '').replace('http://', '').replace('www.', '').lower()
            servidor = servidor.split('.', 1)[0]
            servidor = corregir_servidor(servidor)

            calidad = calidad.replace('(', '').replace(')', '').strip()

            itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '',
                                  linkid = linkid, linktype = tipo, linkepi = item.contentEpisodeNumber if item.dataid else -1,
                                  language = IDIOMAS.get(lang, lang), quality = calidad, quality_num = puntuar_calidad(calidad) ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    if item.linkepi == -1:
        post = 'set=LoadOptions&action=Step3&id=%s&type=%s' % (item.linkid, item.linktype)
    else:
        post = 'set=LoadOptionsEpisode&action=Step3&id=%s&type=%s&episode=%s' % (item.linkid, item.linktype, str(item.linkepi))

    data = do_downloadpage(host + 'playview', post=post)

    url = scrapertools.find_single_match(data, 'data-url="([^"]+)"><span class="pull-left">Link directo')
    if 'http' not in url: url = None

    if not url: url = scrapertools.find_single_match(data, '<iframe class="[^"]*" src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, '<iframe src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, 'data-url="([^"]+)')

    if url.startswith(host):
        url = do_downloadpage(url, follow_redirects=False, only_headers=True).get('location', '')

        url = url.replace('youtvgratis', 'fembed')

        if url and 'http' not in url:
            if item.server == 'jetload': url = 'https://jetload.net/e/' + url
            else: url = None

    if url:
        if not item.servidor:
            servidor = servertools.get_server_from_url(url)
            servidor = servertools.corregir_servidor(servidor)

            if servidor and servidor != 'directo':
                url = servertools.normalize_url(servidor, url)
                itemlist.append(item.clone( url=url, server=servidor ))
        else:   
            itemlist.append(item.clone(url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
       item.url = host + 'search/' + texto.replace(" ", "+")
       return list_all(item)
    except:
       import sys
       for line in sys.exc_info():
           logger.error("%s" % line)
       return []

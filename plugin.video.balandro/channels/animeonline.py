# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://www1.animeonline.ninja/'


def do_downloadpage(url, post=None, headers=None):
    # ~ por si viene de enlaces guardados
    url = url.replace('https://animeonline1.ninja/', host)

    data = httptools.downloadpage(url, post=post).data
    return data


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_anime = config.get_setting('descartar_anime', default=False)

    if descartar_anime: return itemlist

    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False: return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'online/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all',  url = host + 'genero/en-emision/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'list_all', url = host + 'episodio/', group = 'last_epis', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistos', action = 'list_all', url = host + 'tendencias/?get=tv', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'ratings/?get=tv', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Sin censura', action = 'list_all', url = host + 'genero/sin-censura/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Live action', action = 'list_all', url = host + 'genero/live-action/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En blu-ray / dvd', action = 'list_all', url = host + 'genero/blu-ray/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Amazon prime video', action = 'list_all', url = host + 'genero/amazon-prime-video/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Dragon ball', action = 'dragons', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'pelis', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por idioma', action = 'idiomas', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def dragons(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'genero/anime-castellano/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'genero/audio-latino/', search_type = 'tvshow' ))

    return itemlist


def pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Catálogo (Películas)', action = 'list_all', url = host + 'pelicula/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + 'tendencias/?get=movies', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'ratings/?get=movies', search_type = 'movie' ))

    return itemlist

def idiomas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'genero/anime-castellano/', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'genero/audio-latino/', search_type = 'tvshow' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    url_anio = url = host + 'release/'

    tope_year = 1985

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        url = url_anio + str(x) + '/'

        itemlist.append(item.clone( title = str(x), url = url, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if '<header><h1>' in data: parte = '<header><h1>'
    else: parte = '<h1>'

    bloque = scrapertools.find_single_match(data, parte + '(.*?)</h2>')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        thumb = scrapertools.find_single_match(match, 'data-src="(.*?)"')
        title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        lang = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>')
        lang = lang.replace('Audio', '').lower().strip()

        if lang == 'latino' or lang == 'laninofinal': lang = 'Lat'
        elif lang == 'castellano' or lang == 'español': lang = 'Esp'
        elif lang == 'multi': lang = 'Multi-Audio'
        elif lang == 'triple': lang = 'Triple-Audio'
        else: lang = ''

        qlty = scrapertools.find_single_match(match, '<span class="quality">(.*?)</span>').lower()
        if 'audio' in qlty: qlty = ''
        elif 'castellano' in qlty: qlty = ''
        elif 'español' in qlty: qlty = ''

        if qlty == 'final' or qlty == 'corto' or qlty == 'sin censura': qlty = ''

        year = scrapertools.find_single_match(match, '</h3><span>(.*?)</span>')
        if not year: year = '-'

        if item.group == 'last_epis' or item.search_type == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, qualities=qlty, languages=lang,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, qualities=qlty, languages=lang,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<span class="current">.*?' + "<a href='(.*?)'")
        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

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
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = int(tempo)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = int(tempo), page = 0 ))

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

    bloque = scrapertools.find_single_match(data, "<span class='se-t.*?'>%s</span>(.*?)</div></div>" % (item.contentSeason))

    epis = re.compile("<li class='mark-(.*?)</li>", re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(epis)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('AnimeOnline', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for epi in epis[item.page * item.perpage:]:
        epi_num = scrapertools.find_single_match(epi, "(.*?)'>")

        thumb = scrapertools.find_single_match(epi, "data-src='(.*?)'")
        url = scrapertools.find_single_match(epi, "<a href='(.*?)'")

        title = scrapertools.find_single_match(epi, "<div class='episodiotitle'>.*?<a href=.*?'>(.*?)</a>")

        titulo = '%sx%s - %s' % (str(item.contentSeason), epi_num, title)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb, 
                                    contentType = 'episode', contentSeason = 1, contentEpisodeNumber = epi_num ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(epis) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    players = scrapertools.find_multiple_matches(data, "<li id='player-option-(.*?)</ul>")

    ses = 0

    for datos in players:
        ses += 1

        _server = scrapertools.find_single_match(datos, "<span class='server'>(.*?)</span>")

        if not 'saidochesto' in _server: continue

        data_type = scrapertools.find_single_match(datos, "data-type='(.*?)'")
        data_post = scrapertools.find_single_match(datos, "data-post='(.*?)'")
        data_nume = scrapertools.find_single_match(datos, "data-nume='(.*?)'")

        if not data_type or not data_post or not data_nume: continue

        url = host + '/wp-json/dooplayer/v1/post/' + data_post + '?type=' + data_type + '&source=' + data_nume

        data = httptools.downloadpage(url).data

        link = scrapertools.find_single_match(data, '"embed_url":"(.*?)"')

        if not link: continue

        link = link.replace('\\/', '/')

        servers = httptools.downloadpage(link).data

        _servers = scrapertools.find_multiple_matches(servers, '<li onclick="go_(.*?)</li>')

        for dat_server in _servers:
            ses += 1

            url = scrapertools.find_single_match(dat_server, "to_player.*?'(.*?)'")

            if '/netu.' in url or '/hqq.' in url or '/waaw.' in url: continue

            if url:
                if url == 'undefined': continue

                if 'Sub Español' in dat_server: lang = 'Vose'
                elif 'Sub Latino' in dat_server: lang = 'Vose'
                elif 'Latino' in dat_server: lang = 'Lat'
                elif 'Castellano' in dat_server or 'español' in dat_server: lang = 'Esp'
                else: lang = ''

                servidor = servertools.get_server_from_url(url)
                servidor = servertools.corregir_servidor(servidor)

                url = servertools.normalize_url(servidor, url)

                link_other = ''

                if config.get_setting('developer_mode', default=False):
                    try:
                       link_other = url.split('//')[1]
                       link_other = link_other.split('/')[0]
                    except:
                        link_other = url

                    link_other = link_other.replace('www.', '').replace('.com', '').replace('.net', '').replace('.org', '').replace('.co', '').replace('.cc', '').replace('.sh', '')
                    link_other = link_other.replace('.to', '').replace('.tv', '').replace('.ru', '').replace('.io', '').replace('.eu', '').replace('.ws', '').replace('.sx', '')

                    link_other = servertools.corregir_servidor(link_other)

                    if link_other == servidor: link_other = ''
                    link_other = link_other.capitalize()

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, url = url, language = lang, other = link_other ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

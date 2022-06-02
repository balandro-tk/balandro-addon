# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = "https://henaojara.com/"


def mainlist(item):
    return mainlist_animes(item)


def mainlist_animes(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if descartar_xxx: return itemlist
    if config.get_setting('adults_password'):
        from modules import actions
        if actions.adults_password(item) == False:
            return itemlist

    itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color='springgreen' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'ver/category/categorias/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host + 'ver/category/emision/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + 'ver/category/estrenos/?tr_post_type=2', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En castellano', action = 'list_all', url = host + 'ver/category/categorias/espanol-castellano/?tr_post_type=2',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En latino', action = 'list_all', url = host + 'ver/category/categorias/latino/?tr_post_type=2',
                                search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host + 'ver/category/pelicula/?tr_post_type=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos',  search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    bloque = scrapertools.find_single_match(data, '<div id="categories-3"(.*?)</select>')

    matches = scrapertools.find_multiple_matches(bloque, '<option class="level-0".*?">(.*?)</option>')

    for title in matches:
        if title == 'EMISION': continue
        elif title == 'ESPAÑOL CASTELLANO': continue
        elif title == 'ESPAÑOL LATINO': continue
        elif title == 'ESTRENOS': continue
        elif title == 'PELICULAS': continue

        title = title.lower()
        url = host + 'ver/category/categorias/' + title + '/'

        title = title.capitalize()

        itemlist.append(item.clone( title = title, action = 'list_all', url = url ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    for match in matches:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, ' <h3 class="Title">(.*?)</h3>')

        if not url or not title: continue

        nro_season = ''
        if 'Temporada' in title:
            nro_season = scrapertools.find_single_match(title, 'Temporada (.*?) ').strip()
            if nro_season: nro_season = ' T' + nro_season

        title = re.sub(r"Sub |Español|Latino|Castellano|HD|Temporada \d+|\(\d{4}\)", "", title).strip()

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title + nro_season, thumbnail = thumb, titulo = title,
                                    contentType = 'tvshow', contentSerieName = title, infoLabels={'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        next_page = scrapertools.find_single_match(data,'<link rel="next" href="(.*?)"')
        if next_page:
            itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    matches = re.compile('data-tab="(.*?)"', re.DOTALL).findall(data)

    if not matches:
        if '<div class="TPlayer">' in data:
            if not item.search_type == 'movie':
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'sin [COLOR tan]Temporadas[/COLOR]')

            itemlist.append(item.clone( action='findvideos', url = item.url, title = '[COLOR yellow]Servidores[/COLOR] ' + item.titulo,
                                        thumbnail = item.thumbnail, contentType='movie', contentTitle=item.title ))

            return itemlist

    for season in matches:
        title = 'Temporada ' + season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]Una Temporada[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = season ))

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    bloque = scrapertools.find_single_match(data, 'data-tab="' + str(item.contentSeason) + '".*?<tbody>(.*?)</tbody>')

    matches = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(bloque)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('HenaOjara', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for match in matches[item.page * item.perpage:]:
        epis = scrapertools.find_single_match(match,'<td><span class="Num">(.*?)</span>')

        url = scrapertools.find_single_match(match,'<a href="(.*?)"')

        thumb = scrapertools.find_single_match(match,'<img src="(.*?)"')

        titulo = '%sx%s - Episodio %s' % (item.contentSeason, epis, epis)

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage:
            break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page=item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    lang = scrapertools.find_single_match(data, '<h1 class="Title">(.*?)<span>')

    if 'castellano' in lang.lower(): lang = 'Esp'
    elif 'latino' in lang.lower(): lang = 'Lat'
    elif 'subtitulado' in lang.lower(): lang = 'Vose'
    elif 'sub español' in lang.lower(): lang = 'Vose'
    else: lang = 'VO'

    matches = re.compile('id="Opt(.*?)">(.*?)</div>', re.DOTALL).findall(data)

    ses = 0

    for option, datos in matches:
        ses += 1

        url = scrapertools.find_single_match(datos, 'src="(.*?)"')
        if not url: url = scrapertools.find_single_match(datos, 'src=&quot;(.*?)&quot;')

        if not url: continue

        other = scrapertools.find_single_match(data, 'data-tplayernv="Opt' + str(option) + '"><span>(.*?)</span>')
        other = other.replace('<strong>', '').replace('</strong>', '')

        if other.lower() == 'hqq' or other.lower() == 'waaw'  or other.lower() == 'netu': continue

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = lang, other = other ))

    # Descargas
    matches = re.compile('<td><span class="Num">(.*?)</span>.*?href="(.*?)"', re.DOTALL).findall(data)

    for nro, url in matches:
        ses += 1

        other = 'D' + str(nro)

        itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', url = url, language = lang, other = other ))

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

    if '/?trdownload=' in url:
        try:
           url = httptools.downloadpage(url, follow_redirects=False).headers['location']
        except:
           url = ''

    else:
        data = httptools.downloadpage(url).data

        new_url = scrapertools.find_single_match(data, '<div class="Video">.*?src="(.*?)"')

        if new_url:
            if new_url.startswith('//'): new_url = 'https:' + new_url

            url = new_url

            if '/player/go.php?v=' in new_url:
                new_url = new_url.replace('/player/go.php?v=', '/player/go_player.php?v=')

                data = httptools.downloadpage(new_url).data

                url = scrapertools.find_single_match(data, 'src="(.*?)"')
                if url.startswith('//'): url = 'https:' + url

    if '/hqq.' in url or '/waaw.' in url or '/netu' in url:
        return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

    elif '.mystream.' in url:
        return 'Servidor [COLOR tan]Cerrado[/COLOR]'

    elif '/streamium.xyz/' in url: url = ''

    if url:
        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        itemlist.append(item.clone( url=url, server=servidor))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url =  host + "?s=" + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

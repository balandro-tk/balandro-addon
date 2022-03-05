# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://peliculasyserieslatino.me'

lnks_host = 'https://peliseries.live'

perpage = 30


def do_downloadpage(url, post=None, headers=None):
    headers = {'Referer': host}

    data = httptools.downloadpage(url, post=post, headers=headers).data

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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/Peliculas.html?page=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/Estrenos.html?page=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Recientes', action = 'list_all', url = host + '/Agregados.html?page=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + '/Top30dias.html?page=1', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Marvel', action = 'list_all', url = host + '/Buscar.html?s=Marvel', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'DC', action = 'list_all', url = host + '/Buscar.html?s=DC', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/Series.html?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Estrenos', action = 'list_all', url = host + '/Estrenos.html?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Recientes', action = 'list_all', url = host + '/Agregados.html?page=1', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Actualizadas', action = 'list_all', url = host + '/Actualizados.html?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más vistas', action = 'list_all', url = host + '/Top30dias.html?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Novelas', action = 'list_all', url = host + '/Novelas.html?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Anime', action = 'list_all', url = host + '/Anime.html?page=1', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Anime más vistas', action = 'list_all', url = host + '/AnimeTop.html?page=1', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, '<div class="item lazybg"(.*?)</a></div>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, ' href="(.*?)"')
        title = scrapertools.find_single_match(match, '<div class="title">(.*?)</div>')

        if not url or not title: continue

        title = title.replace('&ntilde;', 'ñ')

        tipo = 'tvshow' if "<div class='ln'>Serie</div>" in match else 'movie'
        if tipo == 'movie':
            if "<div class='ln'>Anime</div>" in match: tipo = 'tvshow'
            elif "<div class='ln'>Novela</div>" in match: tipo = 'tvshow'

        sufijo = '' if item.search_type != 'all' else tipo

        url = host + url

        thumb = scrapertools.find_single_match(match, 'img="(.*?)"')

        lngs = scrapertools.find_multiple_matches(match,'<div class="idioma-icons(.*?)">')

        langs = []

        for lng in lngs:
            lng = lng.strip()

            if lng == 'esp': langs.append('Esp')
            if lng == 'lat': langs.append('Lat')
            if lng == 'sub': langs.append('Vose')
            if lng == 'ing': langs.append('VO')

        year = scrapertools.find_single_match(match,'<div class="post_info">.*?Estreno: (\d{4})-')
        if not year: year = '-'

        if tipo == 'tvshow':
            if item.search_type != 'all':
                 if item.search_type == 'movie': continue

            tv_tipo = ''
            if "<div class='ln'>Serie</div>" in match: tv_tipo = 'Serie'
            elif "<div class='ln'>Anime</div>" in match: tv_tipo = 'Anime'
            elif "<div class='ln'>Novela</div>" in match: tv_tipo = 'Novela'

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, tv_tipo = tv_tipo, fmt_sufijo=sufijo,
                                        languages = ', '.join(langs), contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        else:
            if item.search_type != 'all':
                 if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo=sufijo,
                                        languages = ', '.join(langs), contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if not '/Buscar.html' in item.url:
        buscar_next = True
        if num_matches > perpage:
            hasta = (item.page * perpage) + perpage
            if hasta < num_matches:
                itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))
                buscar_next = False

        if buscar_next:
            if itemlist:
                next_page = scrapertools.find_single_match(data, "<li class='num active'>.*?<li class='num'>.*?<a href='(.*?)'")
                if next_page:
                    next_page = host + next_page

                    itemlist.append(item.clone (url = next_page, page = 0, title = 'Siguientes ...', action = 'list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    if not item.tv_tipo:
        if config.get_setting('developer_mode', default=False): platformtools.dialog_notification('PeliSeries', '[COLOR red]Falta Tipo TV[/COLOR]')
        return itemlist

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    pid = scrapertools.find_single_match(data, "'pid':(.*?),")

    if not pid:
        if config.get_setting('developer_mode', default=False): platformtools.dialog_notification('PeliSeries', '[COLOR red]Falta Pid[/COLOR]')
        return itemlist

    post = 'pid=%s&tipo=%s&temp=-1&cap=-1' % (str(pid), str(item.tv_tipo))

    data = do_downloadpage(host + '/LoadTempCap', post = post)

    temporadas = re.compile('"link_temp": "(.*?)"', re.DOTALL).findall(data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.pid = pid
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, pid = pid, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    post = 'pid=%s&tipo=Serie&tmp=%s&cap=-1' %(str(item.pid), str(item.contentSeason))

    data = do_downloadpage(host + '/LoadTempCap', post = post)

    matches = re.compile('"link_cap": "(.*?)".*?"link_path": "(.*?)"', re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PeliSeries', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for epis, url in matches[item.page * item.perpage:]:
        url = url.replace('\\/', '/')

        url = host + url

        titulo = str(item.contentSeason) + 'x' + str(epis) + ' ' + item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'")

        itemlist.append(item.clone( action='findvideos', url = url, title = titulo,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = epis ))

        if len(itemlist) >= item.perpage: break

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def puntuar_calidad(txt):
    orden = ['CAM', '360p', '480p', 'RHDTV', 'HDTV', 'HD', '720p', 'HD720p', '1080p', 'HD1080p', 'BRRip']
    txt = txt.replace('CAM ', '').replace('HD ', '').replace('BRRip ', '').replace('SD', '').replace('S', '').strip()
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    if not item.pid:
        data = do_downloadpage(item.url)
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

        pid = scrapertools.find_single_match(data, '<iframe class="iplayer".*?pid=(.*?)&token')
        if not pid: pid = scrapertools.find_single_match(data, '<div class="" style="overflow: hidden">.*?pid=(.*?)&token')

        if not pid:
            if config.get_setting('developer_mode', default=False): platformtools.dialog_notification('PeliSeries', '[COLOR red]Pid Inexistente[/COLOR]')
            return itemlist

        post = 'pid=%s&tipo=Pelicula&temp=-1&cap=-1' % str(pid)
    else:
        post = 'pid=%s&tipo=Serie&temp=%s&cap=%s' %(str(item.pid), str(item.contentSeason), str(item.contentEpisodeNumber))

    data = do_downloadpage(lnks_host + '/?v=Opciones', post = post)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = scrapertools.find_multiple_matches(data, 'onclick="OpenPlayer(.*?)</a></div>')

    ses = 0

    for match in matches:
        ses += 1

        match = match + '</i>'

        code = scrapertools.find_single_match(match, 'code="(.*?)"')
        pid = scrapertools.find_single_match(match, 'pid="(.*?)"')
        lid = scrapertools.find_single_match(match, 'lid="(.*?)"')
        hst = scrapertools.find_single_match(match, 'hst="(.*?)"')
        pos = scrapertools.find_single_match(match, "pos='(.*?)'")

        lang = scrapertools.find_single_match(match, "</i>(.*?)</i>").lower()
        lang = lang.strip()

        if 'latino' in lang: lang = 'Lat'
        elif 'castellano' in lang or 'español' in lang: lang = 'Esp'
        elif 'subtitulado' in lang or 'sub' in lang: lang = 'Vose'
        elif 'ing.' in lang or 'ingles' in lang: lang = 'VO'
        else: lang = '?'

        qlty = scrapertools.find_single_match(match, "</i>.*? (.*?)</i>")
        if not qlty: qlty = scrapertools.find_single_match(match, "</i>(.*?)</i>")
        qlty = qlty.strip()

        if 'play_' in match:
            play_down = ''
            url = '%s/?v=Player&pid=%s&lid=%s&h=%s&pos=%s&u=%s' % (host, pid, lid, hst, pos, code)

            if 'clicknupload' in hst:
                url += '&port=80'
            elif 'myurlshort' in hst:
                url = '%s/?v=Player&pid=%s&lid=%s&h=%s&pos=%s&u=%s' % (host, pid, lid, hst, pos, code)

        elif '_download' in match:
            play_down = ' d'
            url = 'pid=%s&lid=%s&hst=%s&code=%s' % (pid, lid, hst, code)
        else:
            play_down = ' o'
            url = '%s/?v=Player&pid=%s&lid=%s&h=%s&pos=%s&u=%s' % (host, pid, lid, hst, pos, code)

        if hst:
            hst = hst.lower()

            if 'hqq.' in hst or 'waaw.' in hst or 'netu.' in hst: continue
            elif 'youtube' in hst: continue

            elif 'megaplay' in hst: continue
            elif 'megavideo' in hst: continue

            elif 'cuevana3' in hst: continue
            elif 'repelis24' in hst: continue
            elif 'flixplayer' in hst: continue
            elif 'vidcloud' in hst: continue
            elif 'mystream' in hst: continue
            elif 'stormo' in hst: continue
            elif 'moovies' in hst: continue
            elif '1fichier' in hst: continue
            elif 'mediafire' in hst: continue
            elif 'pandafiles' in hst: continue
            elif 'myfiles' in hst: continue
            elif 'dropapk' in hst: continue
            elif 'nitroflare' in hst: continue
            elif 'owndrives' in hst: continue
            elif 'hopigrarn' in hst: continue
            elif 'homoluath' in hst: continue
            elif 'primeuploads' in hst: continue

            elif 'openload' in hst: continue
            elif 'powvideo' in hst: continue
            elif 'streamplay' in hst: continue
            elif 'rapidvideo' in hst: continue
            elif 'streamango' in hst: continue
            elif 'verystream' in hst: continue
            elif 'vidtodo' in hst: continue

            elif 'drive' in hst: continue
            elif 'hls' in hst: continue
            elif 'indishare' in hst: continue
            elif 'apialfa' in hst: continue

            other = hst
            other = other.replace('www.', '').replace('www', '').replace('fe.', '')
            other = other.replace('.com', '').replace('.net', '').replace('.live', '').replace('api.', '').replace('.io', '').replace('.me', '').replace('.am', '')
            other = other.replace('.co', '').replace('.tv', '').replace('.ru', '').replace('.to', '').replace('.cc', '').replace('.nz', '').replace('.xyz', '')
            other = other.replace('.site', '').replace('.live', '').replace('.club', '').replace('.org', '').replace('.info', '')
            other = other.replace('.pelisplay', '').replace('.google', '').replace('player.', '').replace('play.', '').replace('.playerd', '')

            other = other.capitalize() + play_down

            itemlist.append(Item( channel = item.channel, action = 'play', server = 'directo', title = '', url = url, other = other,
                                  language = lang, quality = qlty, quality_num = puntuar_calidad(qlty) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    item.url = item.url.replace('/peliculasyserieslatino.me/', '/peliseries.live/')

    url = item.url

    if not ' d' in item.other and not ' o' in item.other:
        data = do_downloadpage(item.url)

        url = scrapertools.find_single_match(data, "<iframe src='(.*?)'")

        if not url: url = scrapertools.find_single_match(data, "<IFRAME SRC='(.*?)'")
        if not url: url = scrapertools.find_single_match(data, '<iframe id="myframe" data-src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, '<iframe style=.*?src="(.*?)"')
        if not url: url = scrapertools.find_single_match(data, "var Original='(.*?)'")
        if not url: url = scrapertools.find_single_match(data, "var video_url='(.*?)'")
        if not url: url = scrapertools.find_single_match(data, 'sources:.*?"src":.*?"(.*?)"')

        if url:
            if '//femax20.com/' in url:
                if 'code=' in url:
                    id = scrapertools.find_single_match(url, 'code=(.*?)&')
                    if id: url = 'https://femax20.com/v/%s' % id

    elif ' d' in item.other:
        data = do_downloadpage(lnks_host + '/?m=Descargas', post=item.url)
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

        url = scrapertools.find_single_match(data, 'Array.*?=>(.*?)$').strip()

        if url:
            if '[output]' in url: url = url.replace('[output]', '').strip()
         
        else:
            new_url = scrapertools.find_single_match(data, host + '(.*?)"')
            if not new_url: new_url = scrapertools.find_single_match(data, host + '(.*?)"')

            new_url = host + new_url
            new_url = new_url.replace('/peliculasyserieslatino.me/', '/peliseries.live/')

            data = do_downloadpage(new_url)

            if 'Fembed' in item.other:
                new_url = scrapertools.find_single_match(data, "location.href='([^']+)'")
                if new_url:
                    if 'code=' in new_url:
                        id = scrapertools.find_single_match(new_url, 'code=(.*?)&')
                        if id: url = 'https://femax20.com/v/%s' % id
            else:
                url = scrapertools.find_single_match(data, '<div class="cont">.*?href="(.*?)"')

    if url:
        if '/hqq.' in url or '/waaw.' in url or '/netu.' in url:
            return 'Requiere verificación [COLOR red]reCAPTCHA[/COLOR]'

        url = url.replace('\\/', '/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if not servidor == 'directo':
            url = servertools.normalize_url(servidor, url)

            itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/Buscar.html?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


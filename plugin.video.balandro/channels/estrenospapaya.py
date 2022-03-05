# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urlparse
else:
    import urllib.parse as urlparse


import re, string

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb

host = "https://www.estrenospapaya.com/"

IDIOMAS = {'es': 'Esp', 'lat': 'Lat', 'in': 'Eng', 'ca': 'Cat', 'sub': 'Vose',
           'Español Latino': 'Lat', 'Español Castellano': 'Esp', 'Sub Español': 'Vose'}


def do_downloadpage(url, post=None, referer=None):
    headers = {'Referer': host}
    if referer: headers['Referer'] = referer

    data = httptools.downloadpage(url, post=post, headers=headers).data
    return data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title='Buscar serie ...', action='search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title='Nuevas al azar', action='list_all', url= host + 'lista-series-estrenos/' ))

    itemlist.append(item.clone( title='Capítulos estreno en castellano', action='estrenos', url = host + 'estreno-serie-castellano/' ))
    itemlist.append(item.clone( title='Capítulos estreno en latino', action='estrenos', url = host + 'estreno-serie-espanol-latino/' ))
    itemlist.append(item.clone( title='Capítulos estreno subtitulado', action='estrenos', url = host + 'estreno-serie-sub-espanol/' ))

    itemlist.append(item.clone( title='Más vistas', action='list_all', url = host + 'lista-series-populares/' ))
    itemlist.append(item.clone( title='Recomendadas', action='list_all', url = host + 'lista-series-recomendadas/' ))

    itemlist.append(item.clone( title='Por letra (A - Z)', action='alfabetico' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []
    data = do_downloadpage(item.url)

    patron = '<div class="esimagen">\s*<img style="width:60px" src="([^"]+)'
    patron += '.*? href="([^"]+)" class="esenla">(.*?)</a> \((\d{4})\)'
    patron += '.*?<div class="essin">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for img, url, name, year, plot in matches:
        url = urlparse.urljoin(host, url)
        thumb = httptools.get_url_headers(urlparse.urljoin(host, img))

        itemlist.append(item.clone( action='temporadas', url=url, title=name, thumbnail=thumb,
                                    contentType = 'tvshow', contentSerieName = name, infoLabels={'year': year, 'plot': plot} ))

    tmdb.set_infoLabels(itemlist)

    if '/lista-series-estrenos/' in item.url:
        itemlist.append(item.clone( title = 'Mostrar más al azar', action = 'list_all', text_color='coral' ))

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(action = "series_por_letra", title = "0-9"))

    for letra in string.ascii_uppercase:
        itemlist.append(item.clone(action="letras", title=letra))

    return itemlist


def letras(item):
    logger.info()

    item.letter = 'num' if item.title == '0-9' else item.title.lower()
    item.page = 0

    return series_por_letra(item)


def series_por_letra(item):
    logger.info()
    itemlist = []

    url = urlparse.urljoin(host, "autoload_process.php")

    post_request = {"group_no": item.page, "letra": item.letter}

    data = do_downloadpage(url, post=post_request)

    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    patron = '<div class=list_imagen><img src=(.*?) \/>.*?<div class=list_titulo><a href=(.*?) style=.*?inherit;>(.*?)<.*?justify>(.*?)<.*?Año:<\/b>.*?(\d{4})<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for img, url, name, plot, year in matches:
        url = urlparse.urljoin(host, url)
        thumb = httptools.get_url_headers(urlparse.urljoin(host, img))

        new_item = item.clone( action='temporadas', url=url, title=name, thumbnail=thumb,
                               contentType = 'tvshow', contentSerieName = name, infoLabels={'year': year, 'plot': plot} )

        itemlist.append(new_item)

    tmdb.set_infoLabels(itemlist)

    if len(matches) >= 8:
        itemlist.append(item.clone( title = 'Siguientes ...', action = 'series_por_letra', page=item.page + 1, text_color='coral' ))

    return itemlist


def estrenos(item):
    logger.info()
    itemlist = []

    language = 'Esp' if 'castellano' in item.url else 'Lat' if 'latino' in item.url else 'Vose'

    if item.page == '': item.page = 0
    perpage = 10

    data = do_downloadpage(item.url)

    patron = '<div class="capitulo-caja" style="[^"]*" onclick="location.href=\'([^\']*)\''
    patron += '.*?url\(\'([^\']*)\''
    patron += '.*?<strong>(\d+)</strong>x<strong>(\d+)</strong>'
    patron += '.*?<div style="[^"]*">([^<]*)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, img, season, episode, show in matches[item.page * perpage:]:
        show = show.replace('\n', '').strip()

        if show.startswith('"') and show.endswith('"'): show = show[1:-1]

        originaltitle = scrapertools.find_single_match(show, '\((.*)\)$')
        if originaltitle: show = show.replace('(%s)' % originaltitle, '').strip()

        titulo = '%s %sx%s' % (show, season, episode)

        # Menú contextual acceso a temporada / serie
        slug_serie = scrapertools.find_single_match(url, '/ver/([^/]*)/')
        url_serie = urlparse.urljoin(host, 'serie/%s.html' % slug_serie)
        if not url.startswith(host):
            url = urlparse.urljoin(host, url)

        context = []
        context.append({ 'title': '[COLOR pink]Listar temporada %s[/COLOR]' % season, 
                         'action': 'episodios', 'url': url_serie, 'context': '', 'folder': True, 'link_mode': 'update' })

        context.append({ 'title': '[COLOR pink]Listar temporadas[/COLOR]',
                         'action': 'temporadas', 'url': url_serie, 'context': '', 'folder': True, 'link_mode': 'update' })

        thumb = httptools.get_url_headers(urlparse.urljoin(host, img))

        itemlist.append(item.clone( action='findvideos', title=titulo, url=url, thumbnail=thumb,
                                    contentType='episode', contentSerieName=show, contentSeason=season, contentEpisodeNumber=episode, context=context ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if len(matches) > (item.page + 1) * perpage:
        itemlist.append(item.clone( title= 'Siguientes ...', action="estrenos", page=item.page + 1, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    if item.contentEpisodeNumber: item.__dict__['infoLabels'].pop('episode')
    if item.contentSeason: item.__dict__['infoLabels'].pop('season')

    temporadas = re.findall('&rarr; Temporada (\d*)', data)

    for tempo in temporadas:
        title = 'Temporada ' + tempo

        if len(temporadas) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = tempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = tempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def tracking_all_episodes(item):
    return episodios(item)


def episodios(item):
    logger.info()
    itemlist = []

    color_lang = config.get_setting('list_languages_color', default='red')

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 100

    data = do_downloadpage(item.url)

    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    patron = '<a class=visco.*?href=(.*?)>.*?>(.*?)-(.*?)</a>.*?<div class=ucapaudio>(.*?)</div>'

    episodes = re.findall(patron, data, re.MULTILINE | re.DOTALL)

    total_epis = 0

    for url, temp_epis, title, langs in episodes:
        season = scrapertools.find_single_match(temp_epis, '(.*?)x').strip()
        episode = scrapertools.find_single_match(temp_epis, '.*?x(.*?)$').strip()

        if item.contentSeason:
            if not str(item.contentSeason) == season: continue

        total_epis += 1

    if item.page == 0:
        sum_parts = total_epis
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('EstrenosPapaya', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, temp_epis, title, langs in episodes[item.page * item.perpage:]:
        season = scrapertools.find_single_match(temp_epis, '(.*?)x').strip()
        episode = scrapertools.find_single_match(temp_epis, '.*?x(.*?)$').strip()

        if item.contentSeason:
            if not str(item.contentSeason) == season: continue

        languages = ', '.join([IDIOMAS.get(lang, lang) for lang in re.findall('images/s-([^\.]+)', langs)])
        titulo = '%s [COLOR %s][%s][/COLOR]' % (title, color_lang, languages)

        url = urlparse.urljoin(host, url)

        ord_epis = str(episode)

        if len(str(ord_epis)) == 1:
            ord_epis = '0000' + ord_epis
        elif len(str(ord_epis)) == 2:
            ord_epis = '000' + ord_epis
        elif len(str(ord_epis)) == 3:
            ord_epis = '00' + ord_epis
        else:
            if total_epis > 50:
                ord_epis = '0' + ord_epis

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, contentType = 'episode',
                                    orden = ord_epis, contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if total_epis > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage,
                            orden = '10000', text_color='coral' ))

    return sorted(itemlist, key=lambda i: i.orden)


def puntuar_calidad(txt):
    orden = ['360p', '480p', '720p HD', '1080p HD']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = 'mtos' + '.+?' + \
             '<div.+?images/(?P<lang>[^\.]+)' + '.+?' + \
             '<div[^>]+>\s+(?P<date>[^\s<]+)' + '.+?' + \
             '<div.+?img.+?>\s*(?P<server>.+?)</div>' + '.+?' + \
             '<div.+?href="(?P<url>[^"]+).+?images/(?P<type>[^\.]+)' + '.+?' + \
             '<div[^>]+>\s*(?P<quality>.*?)</div>' + '.+?' + \
             '<div.+?<a.+?>(?P<uploader>.*?)</a>'

    links = re.findall(patron, data, re.MULTILINE | re.DOTALL)

    typeListStr = ["Descargar", "Ver"]

    ses = 0

    for lang, date, server, url, linkType, quality, uploader in links:
        linkTypeNum = 0 if linkType == "descargar" else 1
        if linkTypeNum != 1 and server != 'Clicknupload' and server != 'Uptobox': continue

        ses += 1

        if '.' in server: server = server.split('.')[0]
        server = servertools.corregir_servidor(server)

        url = urlparse.urljoin(host, url)

        itemlist.append(Item(channel = item.channel, action = 'play', server=server, referer=item.url, title = '', url = url,
                             language = IDIOMAS.get(lang,lang), quality = quality, quality_num = puntuar_calidad(quality), age = date, other = uploader ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return sorted(itemlist, key=lambda it: it.age, reverse=True)


def play(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url, referer=item.referer)

    new_url = scrapertools.find_single_match(data, "location.href='([^']+)")
    if new_url:
        itemlist.append(item.clone(server='', url=new_url))
        itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def search_post(item, texto):
    itemlist = []
    data = do_downloadpage(host + 'busqueda/', post = 'searchquery=%s' % texto)

    patron = 'onclick="location.href=\'([^\']+)\''
    patron += '.*? background-image: url\(\'([^\']+)\''
    patron += '.*?<div style="display: table-cell; vertical-align: middle; width: 165px; ">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for url, img, name in matches:
        name = name.strip()
        url = httptools.get_url_headers(urlparse.urljoin(host, img))
        thumb = urlparse.urljoin(host, img)
        itemlist.append(item.clone( action='temporadas', url=url, title=name, contentType = 'tvshow', contentSerieName = name, thumbnail=thumb ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        data = do_downloadpage(urlparse.urljoin(host, "/buscar.php?term=%s" % texto))
        data_dict = jsontools.load(data)
        if 'myData' not in data_dict: return search_post(item, texto)

        tvshows = data_dict['myData']

        itemlist = []

        for show in tvshows:
            url = urlparse.urljoin(host, show["urla"])
            thumb = httptools.get_url_headers(urlparse.urljoin(host, show["img"]))

            itemlist.append(item.clone( action='temporadas', url=url,
                                        contentType='tvshow', contentSerieName=show["titulo"],
                                        title=show["titulo"], thumbnail=thumb ))

        tmdb.set_infoLabels(itemlist)
        return itemlist
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


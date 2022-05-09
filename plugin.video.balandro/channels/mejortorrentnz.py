# -*- coding: utf-8 -*-

import os, re

from platformcode import logger, config
from core.item import Item
from core import httptools, scrapertools, tmdb


host = 'https://mejortorrent.cc'


perpage = 30


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, headers=None, raise_weberror=True):
    # ~ por si viene de enlaces guardados
    ant_hosts = ['https://mejortorrent.nz']

    for ant in ant_hosts:
        url = url.replace(ant, host)

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=raise_weberror).data
    data = httptools.downloadpage_proxy('mejortorrentnz', url, post=post, headers=headers, raise_weberror=raise_weberror).data

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

    itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
    itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
    itemlist.append(item.clone( title = 'Documentales', action = 'list_all', url = host + '/documentales-3/',
	                            search_type = 'documentary', text_color = 'cyan' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/peliculas-13/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host + '/ultimos-torrents-4-x/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/peliculas-hd-3/', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + '/series-3/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host + '/ultimos-torrents-4-x/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'En HD', action = 'list_all', url = host + '/series-hd-2/', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Documentales', action = 'list_all', url = host + '/documentales-3/', search_type = 'documentary' ))

    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'tvshow' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '<center>(.*?)</h2>')

    matches = scrapertools.find_multiple_matches(bloque, r'<a href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)"')

    num_matches = len(matches)

    for url, thumb, title, in matches[item.page * perpage:]:
        if title == 'Documentales': continue

        if not url or not title: continue

        title = title.replace('[720p]', '').strip()

        titulo = title.split('-')[0].strip()
        if item.search_type == 'tvshow': 
            if '&#' in titulo: titulo = scrapertools.find_single_match(titulo, '(.*?) ')

        title = re.sub(r' \(.*?\)', '', title)

        if item.search_type == 'movie':
            itemlist.append(item.clone( action='findvideos', url=url, title=title, thumbnail=thumb,
                                        contentType='movie', contentTitle=titulo, infoLabels={'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url=url, title=title, thumbnail=thumb,
                                        contentType='tvshow', contentSerieName=titulo, infoLabels={'year': '-'} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_all', text_color='coral' ))
            buscar_next = False

    if buscar_next:
        next_page = scrapertools.find_single_match(data, "class='nopaginar'>.*?href='(.*?)'")
        if next_page:
            if '/page/' in next_page:
                itemlist.append(item.clone( title='Siguientes ...', page = 0, action='list_all', url=next_page, text_color='coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    if item.search_type == 'movie':
        fin_movies = 'Series:' if 'Series:' in data else 'Juegos:'
        if fin_movies == 'Juegos:' and not 'Juegos:' in data: fin_movies = '</table>'

        data = scrapertools.find_single_match(data, r'Peliculas:(.*?)' + fin_movies)
    else:
        fin_tvshows = 'Variados:' if 'Variados:' in data else '</table>>'
        data = scrapertools.find_single_match(data, r'Series:(.*?)' + fin_tvshows)

    matches = scrapertools.find_multiple_matches(data, r"href='([^']+)'.*?>(.*?)<.*?'>(.*?)<")

    for url, title, qlty in matches:
        title = title.replace('[720p]', '').strip()

        titulo = title.split('-')[0].strip()
        if item.search_type == 'tvshow': 
           if '&#' in titulo: titulo = scrapertools.find_single_match(titulo, '(.*?) ')

        title = re.sub(r' \(.*?\)', '', title)

        qlty = qlty.replace('(', '').replace(')', '').strip()

        if '[' in title:
            if qlty: title = title.replace('[' + qlty + ']', '').strip()

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = qlty, 
                                       contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url = url, title = title,  qualities = qlty,
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def alfabetico(item):
    logger.info()
    itemlist = []

    for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if item.search_type == 'tvshow':
            url = host + '/listado/?cat=series&letra=' + letra
        else:
            url = host + '/listado/?cat=peliculas&letra=' + letra

        itemlist.append(item.clone( title = letra, action = 'list_alfa', url = url, letra = letra ))

    return itemlist


def list_alfa(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, r'Mostrando(.*?)</table>')

    matches = scrapertools.find_multiple_matches(bloque, r"href='([^']+)'.*?>(.*?)<")

    num_matches = len(matches)

    for url, title in matches[item.page * perpage:]:
        title = title.replace('[720p]', '').strip()

        titulo = title.split('-')[0].strip()
        if item.search_type == 'tvshow': 
           if '&#' in titulo: titulo = scrapertools.find_single_match(titulo, '(.*?) ')

        title = re.sub(r' \(.*?\)', '', title)

        if not title: continue

        if item.search_type == 'movie':
            refer = scrapertools.find_single_match(url, '/peli-descargar-torrent-(.*?)-')

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = refer,
                                       contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url = url, title = title, grupo = 'selecc',
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_alfa', text_color='coral' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    i = 0

    if item.search_type == 'documentary':
         bloque = scrapertools.find_single_match(data, 'Listado de los episodios(.*)Marcar/Desmarcar Todos')

         matches = scrapertools.find_multiple_matches(bloque, "bgcolor='#C8DAC8'.*?</td>.*?'>(.*?)</td>.*?name='(.*?)'.*?value='(.*?)'")

         for title, id, value in matches:
             title = title.strip()
             if item.grupo == 'selecc': title = title + '  ' + item.title

             i += 1

             itemlist.append(item.clone( action='findvideos', id = id, value = value, ref = item.url, title = title,
                                         contentType='episode', contentSeason = 1, contentEpisodeNumber = i ))

         return itemlist


    bloque = scrapertools.find_single_match(data, 'Listado de los episodios(.*)Descargar Seleccionados')

    matches = scrapertools.find_multiple_matches(bloque, "bgcolor='#C8DAC8'.*?" + '<a href="(.*?)">(.*?)</a>.*?' + "name='(.*?)'.*?value='(.*?)'")

    for url, title, id, value in matches:
        title = title.strip()

        if item.grupo == 'selecc': title = title + '  ' + item.title

        i += 1

        itemlist.append(item.clone( action='findvideos', id = id, value = value, ref = item.url, title = title,
                                    contentType='episode', contentSeason = 1, contentEpisodeNumber = i ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    url = ''

    if item.search_type == 'movie':
        data = do_downloadpage(item.url)

    else:
        if not item.id or not item.value: return itemlist

        if item.search_type == 'documentary':
            data = do_downloadpage(item.url)

            id_post = scrapertools.find_single_match(data, '<input type="hidden" value="(.*?)" name="id_post">')
            if id_post: item.value = id_post

        post = {item.id : item.value}

        data = do_downloadpage( host + '/download_tv.php', post = post, headers = {'Referer': item.ref}, raise_weberror = False)

    hash = scrapertools.find_single_match(data, '<input type="hidden".*?<input type="hidden".*?value="(.*?)"')
    if not hash: hash = scrapertools.find_single_match(data, '<a class="opcion.*?u=(.*?)"')

    if not hash: return itemlist

    lang = 'Esp'

    qlty = scrapertools.find_single_match(data, "<b>Formato.*?</b>(.*?)<br>").strip()
    qlty = qlty.replace('&nbsp;', '').strip()

    size = scrapertools.find_single_match(data, "<b>Tamaño.*?</b>(.*?)<br>").strip()
    size = size.replace('&nbsp;', '').strip()

    itemlist.append(Item( channel = item.channel, action = 'play', title = '', hash = hash, server = 'torrent', language = lang, quality = qlty,
                          other = size ))

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url = item.url

    if item.hash:
        url = host + '/torrent_dmbk.php?u=' + item.hash

        data = do_downloadpage(url)

        if data:
            if '<h1>Not Found</h1>' in str(data) or '<!DOCTYPE html>' in str(data) or '<!DOCTYPE>' in str(data):
                return 'Archivo [COLOR red]Inexistente[/COLOR]'

            file_local = os.path.join(config.get_data_path(), "temp.torrent")
            with open(file_local, 'wb') as f: f.write(data); f.close()

            itemlist.append(item.clone( url = file_local, server = 'torrent' ))

    return itemlist


def list_search(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, r'Has realizado una búsqueda(.*?)</table>')

    matches = scrapertools.find_multiple_matches(bloque, r"href='(.*?)'.*?>(.*?)</a>.*?'>(.*?)<.*?<td.*?>(.*?)<")

    num_matches = len(matches)

    for url, title, qlty, type in matches[item.page * perpage:]:
        if not type == 'Peliculas' and not type == 'Series' and not type == 'Capitulos' and not type == 'Documentales': continue

        if item.search_type != 'all':
            if item.search_type == 'movie':
                if type == 'Series' or type == 'Capitulos': continue
                elif type == 'Documentales': continue
            else:
                if type == 'Peliculas': continue
                elif type == 'Documentales': continue

        sufijo = ''

        if item.search_type == 'all':
            search_type = item.search_type

            if type == 'Peliculas': sufijo = 'movie'
            elif type == 'Series' or type == 'Capitulos': sufijo = 'tvshow'
            else:
               sufijo = '[COLOR cyan]Documental[/COLOR]'
               search_type = 'documentary'

        title = title.replace("<font Color='darkblue'>", '').replace('</font>', '').replace("<span style='color:gray;'>", '').replace('</span>', '').strip()

        titulo = title.split('-')[0].strip()
        title = re.sub(r' \(.*?\)', '', title)

        qlty = qlty.replace('(', '').replace(')', '').strip()

        if item.search_type == 'movie':
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, qualities = qlty, fmt_sufijo = sufijo,
                                       contentType = 'movie', contentTitle = titulo, infoLabels = {'year': '-'} ))
        else:
            itemlist.append(item.clone( action='episodios', url = url, title = title, qualities = qlty, fmt_sufijo = sufijo, search_type = search_type,
                                        contentType = 'tvshow', contentSerieName = titulo, infoLabels = {'year': '-'} ))

        if len(itemlist) >= perpage: break

    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action='list_search', text_color='coral' ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + '/?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

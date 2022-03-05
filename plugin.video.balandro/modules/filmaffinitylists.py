# -*- coding: utf-8 -*-
import re

from datetime import datetime

from platformcode import config, logger
from core.item import Item
from modules import search
from core import httptools, scrapertools, tmdb

host = "https://www.filmaffinity.com/es/"


ruta_sel = 'topgen.php?country=%s&genre=%s&fromyear=%s&toyear=%s'

current_year = int(datetime.today().year)

perpage = 30


def mainlist(item):
    logger.info()
    itemlist = []

    por_plataforma = False
    por_tema = False

    presentar = True
    if item.search_type == 'tvshow': presentar = False
    elif item.search_type == 'documentary': presentar = False
    elif item.extra == 'mixed':
       if item.search_type == 'movie': presentar = False

    if presentar:
        por_plataforma = True
        por_tema = True

        itemlist.append(item.clone( title = 'Películas', thumbnail=config.get_thumb('movie'), action = '', text_color='deepskyblue' ))

        itemlist.append(item.clone( title = ' - En cartelera', action = 'list_all', url = host + 'cat_new_th_es.html' ))

        itemlist.append(item.clone( title = ' - Por plataforma', action = 'plataformas' ))
        itemlist.append(item.clone( title = ' - Por género', action = 'generos' ))
        itemlist.append(item.clone( title = ' - Por país', action = 'paises' ))
        itemlist.append(item.clone( title = ' - Por año', action = 'anios' ))
        itemlist.append(item.clone( title = ' - Por tema', action = 'temas', url = host + 'topics.php' ))

        itemlist.append(item.clone( title = ' - Premios Oscar', action = 'oscars', url = host + 'oscar_data.php' ))

        itemlist.append(item.clone( title = ' - Sagas y colecciones', action = 'sagas', url = host + 'movie-groups-all.php', page = 1 ))

        itemlist.append(item.clone( title = ' - Las mejores películas', action = 'list_sel', url = host + ruta_sel + '&notvse=1&nodoc=1' ))

    presentar = True
    if item.search_type == 'movie': presentar = False
    elif item.search_type == 'documentary': presentar = False
    elif item.extra == 'mixed':
       if item.search_type == 'tvshow': presentar = False

    if presentar:
        if not por_plataforma:
            por_plataforma = True
            itemlist.append(item.clone( title = ' - Por plataforma', action = 'plataformas' ))

        if not por_tema:
            por_tema = True
            itemlist.append(item.clone( title = ' - Por tema', action = 'temas', url = host + 'topics.php' ))

        itemlist.append(item.clone( title = 'Series', thumbnail=config.get_thumb('tvshow'), action = '', text_color='hotpink' ))

        itemlist.append(item.clone( title = ' - Premios Emmy', action = 'emmy_ediciones', url = host + 'awards.php?award_id=emmy&year=' ))

        itemlist.append(item.clone( title = ' - Las mejores series', action = 'list_sel', url = host + ruta_sel + '&nodoc=1', cod_genre = 'TV_SE' ))

    presentar = True
    if item.search_type == 'movie': presentar = False
    elif item.search_type == 'tvshow': presentar = False
    elif item.extra == 'mixed': presentar = False

    if presentar:
        if not por_tema:
            itemlist.append(item.clone( title = ' - Por tema', action = 'temas', url = host + 'topics.php' ))

        itemlist.append(item.clone( title = 'Documentales', thumbnail=config.get_thumb('documentary'), action = '', text_color='cyan' ))

        itemlist.append(item.clone( title = ' - Los mejores documentales', action = 'list_sel', url = host + ruta_sel + '&notvse=1', cod_genre = 'DO' ))

    if not item.search_type:
        itemlist.append(item.clone( title = 'Películas y Series', thumbnail=config.get_thumb('heart'), action = '', text_color='yellow' ))

        itemlist.append(item.clone( title = ' - Novedades a la venta', action = 'list_all', url = host + 'cat_new_sa_es.html' ))
        itemlist.append(item.clone( title = ' - Novedades en alquiler', action = 'list_all', url = host + 'cat_new_re_es.html' ))

    return itemlist
 

def plataformas(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Amazon prime', action = 'list_all', url = host + 'cat_new_amazon_es.html' ))
    itemlist.append(item.clone( title = 'Apple TV+', action = 'list_all', url = host + 'cat_apple_tv_plus.html' ))
    itemlist.append(item.clone( title = 'Disney+', action = 'list_all', url = host + 'cat_disneyplus.html' ))
    itemlist.append(item.clone( title = 'Filmin', action = 'list_all', url = host + 'cat_new_filmin.html' ))
    itemlist.append(item.clone( title = 'HBO', action = 'list_all', url = host + 'cat_new_hbo_es.html' ))
    itemlist.append(item.clone( title = 'Movistar+', action = 'list_all', url = host + 'cat_new_movistar_f.html' ))
    itemlist.append(item.clone( title = 'Netflix', action = 'list_all', url = host + 'cat_new_netflix.html' ))
    itemlist.append(item.clone( title = 'Rakuten TV', action = 'list_all', url = host + 'cat_new_rakuten.html' ))

    return itemlist


def oscars(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Películas con Más Oscars', action = 'list_oscars', url = item.url, grupo = 'Películas con más Oscars' ))
    itemlist.append(item.clone( title = 'Películas con Más Nominaciones (sin Oscar a la mejor película)', action = 'list_oscars', url = item.url, grupo = 'Películas con más nominaciones' ))
    itemlist.append(item.clone( title = 'Películas con Más Nominaciones y Ningún Oscar', action = 'list_oscars', url = item.url, grupo = 'Películas con más nominaciones y ningún Oscar' ))
    itemlist.append(item.clone( title = 'Películas Ganadoras de los 5 Oscars principales', action = 'list_oscars', url = item.url, grupo = 'Películas ganadoras de los 5 Oscars principales' ))
    itemlist.append(item.clone( title = 'Últimas Películas Ganadoras del Oscar principal', action = 'list_oscars', url = item.url, grupo = 'Últimas películas ganadoras del Oscar principal' ))
    itemlist.append(item.clone( title = 'Ediciones Premios Oscar', action = 'oscars_ediciones', url = host + 'award_data.php?award_id=academy_awards' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<div class="movie-poster" data-movie-id=.*?src="(.*?)".*?title="(.*?)"')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for thumb, title in matches[desde:hasta]:
        title = title.strip()

        thumb = thumb.replace('-mtiny', '-large') + '|User-Agent=Mozilla/5.0'

        if '(Serie de TV)' in title or '(Miniserie de TV)' in title:
            name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow',
                                        name = name, contentSerieName = name ))
        else:
            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'movie',
                                        name = title, contentTitle = title, infoLabels = {'year': '-'} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_all', text_color='coral' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    labels_generos = [
          ('Accion', 'AC'),
          ('Animación', 'AN'),
          ('Aventuras', 'AV'),
          ('Bélico', 'BE'),
          ('Ciencia ficción', 'C-F'),
          ('Cine negro', 'F-N'),
          ('Comedia', 'CO'),
          ('Documental', 'DO'),
          ('Drama', 'DR'),
          ('Fantástico', 'FAN'),
          ('Infantil', 'INF'),
          ('Intriga', 'INT'),
          ('Musical', 'MU'),
          ('Romance', 'RO'),
          ('Serie de TV', 'TV_SE'),
          ('Terror', 'TE'),
          ('Thriller', 'TH'),
          ('Western', 'WE')
    ]

    ruta_gen = 'topgen.php?country=%s&genres=%s&fromyear=%s&toyear=%s'

    for genero in labels_generos:
        url = host + ruta_gen

        if not genero[0] == 'Serie de TV': url = url + '&notvse=1'
        elif not genero[0] == 'Documental': url = url + '&nodoc=1'

        itemlist.append(item.clone ( title = genero[0], action = 'list_sel', url = url, cod_genre = genero[1] ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    labels_paises = [
          ('Argentina','AR'), 
          ('Australia','AU'), 
          ('Bolivia','BO'), 
          ('Canadá','CA'), 
          ('Chile','CL'), 
          ('Colombia','CO'), 
          ('Costa Rica','CR'), 
          ('Ecuador','EC'), 
          ('España','ES'), 
          ('Estados Unidos','US'), 
          ('Irlanda','IE'), 
          ('México','MX'), 
          ('Perú','PE'), 
          ('Reino Unido','gb'), 
          ('Uruguay','UY'), 
          ('Venezuela','VE') 
    ]

    for pais in labels_paises:
        itemlist.append(item.clone ( title = pais[0], action = 'list_sel', url = host + ruta_sel + '&notvse=1&nodoc=1', cod_country = pais[1] ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    for x in range(current_year, 1899, -1):
        anyo = str(x)
        itemlist.append(item.clone( title = anyo, action='list_sel', url = host + ruta_sel + '&notvse=1&nodoc=1', fromyear = anyo, toyear = anyo  ))

    return itemlist


def temas(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    perpage = 150

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<li><a class="topic" href="(.*?)">(.*?)<em>')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for url, title in matches[desde:hasta]:
        title = title.strip()

        url = url + '&attr=all&order=BY_YEAR'

        search_type = 'movie'

        if title.startswith('Documental ') == True:
            url = url.replace('&nodoc', '')
            search_type = 'documentary'
        elif title == 'Serie [Alfred Hitchcock presenta]': search_type = 'tvshow'
        elif title == 'Serie [Colombo]': search_type = 'tvshow'
        elif title == 'Serie [Pesadillas y alucinaciones]': search_type = 'tvshow'
        elif title == 'Serie [What a Cartoon!]': search_type = 'tvshow'

        itemlist.append(item.clone( action = 'list_temas', title = title, url = url, page = 1, search_type = search_type))

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'temas', text_color='coral' ))

    return itemlist


def list_temas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    patron = '<div class="movie-card.*?movie-card-0" data-movie-id=".*?src="(.*?)".*?title="(.*?)">.*?</a>[^\d+]+(\d+)[^<]+'
    matches = scrapertools.find_multiple_matches(data, patron)

    for thumb, title, year in matches:
        if year:
            if year > str(current_year): continue

        if not year: year = '-'

        title = title.strip()

        if thumb.startswith('/imgs/') == True: thumb = 'https://www.filmaffinity.com' + thumb

        thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        if item.search_type == 'tvshow':
            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = item.search_type,
                                        name = title, contentSerieName = title, infoLabels={'year': year} ))
        elif item.search_type == 'documentary':
            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = item.search_type,
                                        name = title, contentSerieName = title, infoLabels={'year': year} ))
        elif '(Serie de TV)' in title or '(Miniserie de TV)' in title:
            name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow',
                                        name = name, contentSerieName = name, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = item.search_type,
                                        name = title, contentTitle = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if '<div class="pager">' in data:
           not_last_page = scrapertools.find_single_match(data, '<span class="current">.*?</span> <a href="(.*?)"')

           if not_last_page:
               url = item.url

               prev_page = '&p=' + str(item.page)
               url = url.replace(prev_page, '')

               next_page = item.page + 1
               itemlist.append(item.clone( title = '>> Página siguiente', url = url + '&p=' + str(next_page), action = 'list_temas',
                                           page = next_page, text_color='coral' ))

    return itemlist


def list_oscars(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    grupo = scrapertools.find_single_match(data, item.grupo + '(.*?)</table>')

    if item.grupo == 'Películas con más Oscars' or item.grupo == 'Últimas películas ganadoras del Oscar principal': 
        matches = scrapertools.find_multiple_matches(grupo, '">(.*?)</a>.*?title="(.*?)".*?<td>.*?<td>(.*?)</td>')
    else: matches = scrapertools.find_multiple_matches(grupo, '">(.*?)</a>.*?title="(.*?)".*?<td>(.*?)</td>')

    for year, title, premios in matches:
        title = title.strip()
        premios = premios.replace('Oscar', '').strip()
        titulo = '[COLOR tan][' + premios + '][/COLOR]  ' + title

        itemlist.append(item.clone( action = 'find_search', title = titulo, search_type = 'movie', name = title, contentType='movie',
                                    contentTitle = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def oscars_ediciones(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<td><a href="(.*?)" title="(.*?)">(.*?)</a>')

    for url, title, anyo in matches:
        title = title.strip()
        itemlist.append(item.clone( action = 'list_premios_anyo', title = title, url = url, anyo = anyo ))

    return sorted(itemlist, key = lambda it: it.anyo, reverse = True)


def list_premios_anyo(item):
    logger.info()
    itemlist = []

    premiadas = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'class="win-label">Ganador/a</span>.*?src="(.*?)".*?href="(.*?)".*?title="(.*?)"')

    for thumb, url, title in matches:
        title = title.strip()

        thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        if not url in premiadas:
            premiadas.append(url)

            if '(Serie de TV)' in title or '(Miniserie de TV)' in title:
                name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '')

                itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow',
                                            name = name, contentSerieName = name, infoLabels = {'year': item.anyo} ))
            else:
                itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'movie',
                                            name = title, contentTitle = title, infoLabels = {'year': item.anyo} ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def emmy_ediciones(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<a class="award-years-link" title="(.*?)" href="(.*?)">(.*?)</a>')

    for title, url, anyo in matches:
        title = title.replace('(Principales categorías)', '').replace('(principales categorías)', '').strip()

        itemlist.append(item.clone( action = 'list_premios_anyo', title = title, url = url, anyo = anyo ))

    return sorted(itemlist, key = lambda it: it.anyo, reverse = True)


def sagas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<li class="fa-shadow">.*?href="(.*?)".*?<div class="group-name">(.*?)</div>.*?src="(.*?)".*?<div class="count-movies">(.*?)</div>')

    for url, title, thumb, count in matches:
        thumb = thumb.replace('-med', '-large') + '|User-Agent=Mozilla/5.0'

        count = count.replace('películas', '').strip()
        if count: count = '  (' + count + ')'

        itemlist.append(item.clone( action = 'list_sagas', title = title + count, url = url, thumbnail = thumb, page = 0 ))

    if '<div class="pager">' in data:
        not_last_page = scrapertools.find_single_match(data, '<span class="current">.*?</span> <a href="(.*?)"')

        if not_last_page:
            url = item.url

            prev_page = '?p=' + str(item.page)
            url = url.replace(prev_page, '')

            next_page = item.page + 1
            itemlist.append(item.clone( title = '>> Página siguiente', url = url + '?p=' + str(next_page), action = 'sagas',
                                        page = next_page, text_color='coral' ))

    return itemlist


def list_sagas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<div class="movie-card.*?movie-card-0" data-movie-id=".*?src="(.*?)".*?title="(.*?)">.*?</a>[^\d+]+(\d+)[^<]+'
    matches = scrapertools.find_multiple_matches(data, patron)

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for thumb, title, year in matches[desde:hasta]:

        if year:
            if year > str(current_year):
                num_matches = num_matches - 1
                continue

        if not year: year = '-'

        title = title.strip()

        thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        if '(Serie de TV)' in title or '(Miniserie de TV)' in title:
            name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow', 
                                        name = name, contentSerieName = name, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'movie',
                                        name = title, contentTitle = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if num_matches > hasta:
            itemlist.append(item.clone( title = '>> Página siguiente', page = item.page + 1, action = 'list_sagas', text_color='coral' ))

    return itemlist


def list_sel(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    url = item.url

    cod_country = ''
    cod_genre = ''

    if item.cod_country: cod_country = item.cod_country

    if item.cod_genre:
        if not item.cod_genre == 'TV_SE': 
           if not item.cod_genre == 'DO':
               cod_genre = '%2B' + item.cod_genre

    if item.fromyear: fromyear = item.fromyear
    else: fromyear = '1874'

    if item.toyear: toyear = item.toyear
    else: toyear = str(current_year)

    url = url % (cod_country, cod_genre, fromyear, toyear)

    if item.cod_genre == 'TV_SE':
        url = url + '&chv=1&orderby=avg&movietype=serie%7C&ratingcount=3&runtimemin=0&runtimemax=4'
    elif item.cod_genre == 'DO':
        url = url + '&chv=1&orderby=avg&movietype=documentary%7C&ratingcount=3&runtimemin=0&runtimemax=8'
    else:
        url = url + '&chv=1&orderby=avg&movietype=movie%7C&ratingcount=3&runtimemin=0&runtimemax=4'

    post = {'from': item.page}
    data = httptools.downloadpage(url, post = post).data

    matches = scrapertools.find_multiple_matches(data, '<li class="position">(.*?)</ul>')

    if not matches:
        matches = scrapertools.find_multiple_matches(data, '<li>(.*?)</li>')

    for match in matches:
        title = scrapertools.find_single_match(match, ' title="(.*?)"').strip()

        year = scrapertools.find_single_match(match, ' title=.*?</a>(.*?)<img').strip()
        year = year.replace('(', '').replace(')', '').strip()

        if not year: year = '-'

        thumb = scrapertools.find_single_match(match, ' src="(.*?)"')
        thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        if '(Serie de TV)' in title or '(Miniserie de TV)' in title or cod_genre == 'TV_SE':
            name = title.replace('(Serie de TV)', '').replace('(Miniserie de TV)', '')

            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'tvshow', 
                                        name = name, contentSerieName = name, infoLabels={'year': year} ))
        elif '&genre=DO&' in url:
            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'documentary',
                                        name = title, contentTitle = title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action = 'find_search', title = title, thumbnail = thumb, search_type = 'movie',
                                        name = title, contentTitle = title, infoLabels={'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if matches:
        num_matches = len(matches)

        if num_matches >= 30:
            next_page = item.page + 30
            itemlist.append(item.clone( title = '>> Página siguiente', url = item.url, page = next_page, action = 'list_sel', text_color='coral' ))

    return itemlist


def _oscars(item):
    logger.info()
    itemlist = []

    url = host + 'awards.php?award_id=academy_awards&year=' + str(current_year)

    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<div class="full-content"><div class="header" id="([^"]+)">([^<]+)').findall(data)

    for oscars_id, title in matches:
        itemlist.append(item.clone( action = '_oscars_categories', title = title, oscars_id = oscars_id))

    return itemlist

def _oscars_categories(item):
    logger.info()
    itemlist = []
    
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque_patron = '(<div class="full-content"><div class="header" id="%s">.*?</div></div></li></ul></div></div>)' % (item.oscars_id)

    bloque = scrapertools.find_single_match(data, bloque_patron)

    matches = scrapertools.find_multiple_matches(bloque, '<li class="(fa-shadow.*?)">(.*?)</li>')

    for info, match in matches:
        titulo = ''
        title = scrapertools.find_single_match(match, '<a class="movie-title-link" href="[^"]+" title="([^"]+)\W+"')
        titulo += title

        nominated = scrapertools.find_single_match(match, '<div class="nom-text">([^<]+)</div>')
        if nominated:
            titulo += ' - ' + nominated

        nominations = scrapertools.find_single_match(match, '<b>(.*?)</a>')
        if nominations:
            nominations = re.sub('<.*?>', '', nominations) if scrapertools.find_single_match(nominations, '(<.*?>)') else nominations
            titulo += ' - ' + nominations
        else:
            nominations = '1 nominación'

        if 'win' in info:
            titulo = ''.join(("[COLOR pink]", titulo, "[/COLOR]"))

        itemlist.append(item.clone( action = 'find_search', title = titulo, search_type = 'movie', name = title, contentTitle = title, infoLabels={'year': '-'} ))
        
    tmdb.set_infoLabels(itemlist)

    return itemlist


def _emmys(item):
    logger.info()

    item.url = host + 'awards.php?award_id=emmy&year='
    if item.origen == 'mnu_esp':
        return emmy_ediciones(item)

    item.url = item.url + str(current_year)

    return list_premios_anyo(item)


def _oscars(item):
    logger.info()

    item.url = host + 'oscar_data.php'
    item.page = 1

    return oscars(item)

def _sagas(item):
    logger.info()

    item.url = host + 'movie-groups-all.php'
    item.page = 1

    return sagas(item)


def _bestmovies(item):
    logger.info()

    item.url = host + ruta_sel + '&notvse=1&nodoc=1'

    return list_sel(item)


def _besttvshows(item):
    logger.info()

    item.url = host + ruta_sel + '&nodoc=1'
    item.cod_genre = 'TV_SE'

    return list_sel(item)


def _bestdocumentaries(item):
    logger.info()

    item.url = host + ruta_sel + '&notvse=1'
    item.cod_genre = 'DO'

    return list_sel(item)


def _genres(item):
    logger.info()

    return generos(item)


def _years(item):
    logger.info()

    return anios(item)


def _themes(item):
    logger.info()

    item.url = host + 'topics.php'

    return temas(item)


def find_search(item):
    logger.info()
    itemlist = []

    itemlist = search.search(item, item.name)

    return itemlist


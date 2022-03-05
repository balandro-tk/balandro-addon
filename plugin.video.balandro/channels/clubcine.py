# -*- coding: utf-8 -*-

import os

from platformcode import config, logger
from core.item import Item
from core import httptools, scrapertools, tmdb, servertools


host = 'https://mycinedesiempre.blogspot.com/'

perpage = 25


labels_generos = [
      ('007'),
      ('Acción'),
      ('Abogados'),
      ('Abusos sexuales'),
      ('Acoso escolar'),
      ('Adolescencia'),
      ('Adopción'),
      ('Ajedrez'),
      ('Alcoholismo'),
      ('Alzheimer'),
      ('Amistad'),
      ('Animación'), 
      ('Animales'),
      ('AsesinosEnSerie'),
      ('Autismo'),
      ('Aventura espacial'),
      ('Aventuras'),
      ('Baile'),
      ('Ballet'),
      ('Bandas/pandillas'),
      ('Basado en hechos reales'),
      ('Biográfica'),
      ('Bélico'),
      ('Boxeo'),
      ('Brujería'),
      ('Celos'),
      ('Ciencia ficción'),
      ('Cinenegro'),
      ('CineDCine'),
      ('CineMudo'),
      ('CineQuinqui'),
      ('Colegios/Universidad'),
      ('Comedia'),
      ('Comedia dramática'),
      ('Comedia negra'),
      ('Comedia romántica'),
      ('Crimen'),
      ('Cuentos'),
      ('Deporte'),
      ('Dictadura argentina'),
      ('Dictadura chilena'),
      ('Dictadura uruguaya'),
      ('Discapacidad'),
      ('Distopía'),
      ('Documental'),
      ('Drama'),
      ('Drama carcelario'),
      ('Drama judicial'),
      ('Drama psicológico'),
      ('Drama romántico'),
      ('Drama social'),
      ('Drogas'),
      ('Episodios'),
      ('ETA'),
      ('Ejército'),
      ('Enfermedad'),
      ('Enseñanza'),
      ('Erótico'),
      ('Esclavitud'),
      ('Espionaje'),
      ('Experimental'),
      ('ExpresionismoAlemán'),
      ('Extraterrestres'),
      ('Familia'),
      ('Fantástico'),
      ('Feminismo'),
      ('Gore'),
      ('Guerra Civil española'),
      ('Guerra fría'),
      ('Historias cruzadas'),
      ('Histórica'),
      ('Holocausto'),
      ('Homosexualidad.'),
      ('I guerra mundial'),
      ('II guerra mundial'),
      ('Infancia'),
      ('Inmigración'),
      ('Intriga'),
      ('Juego'),
      ('Literatura'),
      ('Mafia'),
      ('Medicina'),
      ('Mediometraje'),
      ('Melodrama'),
      ('Musical'),
      ('Música'),
      ('Naturaleza'),
      ('Nazismo'),
      ('Neo-noir'),
      ('Parodia'),
      ('Periodismo'),
      ('Pintura'),
      ('Piratas'),
      ('Pobreza'),
      ('Policiaco'),
      ('Politica'),
      ('Postguerra Española'),
      ('Prostitución'),
      ('Racismo'),
      ('Religión'),
      ('Remake'),
      ('Road Movie'),
      ('Robos & Atracos'),
      ('Romance'),
      ('Sátira'),
      ('Secuela'),
      ('Secuestros%2FDesapariciones'),
      ('SerieB'),
      ('Sobrenatural'),
      ('Surrealismo'),
      ('Teatro'),
      ('Terror'),
      ('Terrorismo'),
      ('Thriller'),
      ('Trabajo/empleo'),
      ('Trenes/metros'),
      ('Vampiros'),
      ('Vejez'),
      ('Venganza'),
      ('Vida rural'),
      ('Vietnam'),
      ('Western')
      ]


labels_epocas = [
      ('Siglo XVII'),
      ('Siglo XIX'),
      ('1900-1920'),
      ('Años 20'),
      ('Años 30'),
      ('Años 40'),
      ('Años 50'),
      ('Años 60'),
      ('Años 70'),
      ('Años 80'),
      ('Años 90'),
      ('2000%2F2010'),
      ('2011%2F2020')
      ]


labels_paises = [
      ('Africa'),
      ('África'),
      ('Alemania'),
      ('Argentina'),
      ('Asiático'),
      ('Australia'),
      ('Brasil'),
      ('Cuba'),
      ('Dinamarca'),
      ('España'),
      ('Europeo'),
      ('Francia'),
      ('Grecia'),
      ('Holanda'),
      ('Italia'),
      ('Latino'),
      ('Mexico'),
      ('Polonia'),
      ('Reino Unido'),
      ('Rusia'),
      ('Suecia')
      ]


def mainlist(item):
    return mainlist_pelis(item)


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
    thumb_imdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'imdb.jpg')

    itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host ))

    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por época', action ='generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action ='generos', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por dirección', action = 'list_labels', url = host, group = 'DIRECTORES'))
    itemlist.append(item.clone( title = 'Por interprete', action = 'list_labels', url = host, group = 'ACTORES' ))

    itemlist.append(item.clone( title = 'Las mejores de la historia', action = 'list_best', thumbnail = thumb_filmaffinity,
                                url = host + '2018/11/ver-las-150-mejores-peliculas-de-la.html' ))
    itemlist.append(item.clone( title = 'Las mejores del cine negro', action = 'list_best', thumbnail = thumb_imdb,
                                url = host + '2020/10/ver-las-150-mejores-peliculas-de-cine.html' ))

    itemlist.append(item.clone( title = 'Las mejores del cine español', action = 'list_best',
                                url = host + '2021/04/ver-las-100-mejores-peliculas-de-la.html' ))


    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    thumb_tumblr = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'cinedesiempre.jpg')

    itemlist.append(item.clone( title = 'Cine español', action = 'list_all', url = host + 'search/label/España/' ))
    itemlist.append(item.clone( title = 'Cine europeo', action = 'list_all', url = host + 'search/label/Europeo/' ))
    itemlist.append(item.clone( title = 'Cine latino', action = 'list_all', url = host + 'search/label/Latino/' ))
    itemlist.append(item.clone( title = 'Cine asiático', action = 'list_all', url = host + 'search/label/Asiático/' ))
    itemlist.append(item.clone( title = 'Cine de culto', action = 'list_all', url = host + 'search/label/Culto/' ))
    itemlist.append(item.clone( title = 'Cine independiente', action = 'list_all', url = host + 'search/label/Independiente/' ))
    itemlist.append(item.clone( title = 'Cine premiado', action = 'list_all', url = host + 'search/label/Premiada/' ))

    itemlist.append(item.clone( title = 'Cine de siempre', action = 'list_tumblr', url = 'https://cinedesiempre.tumblr.com', thumbnail = thumb_tumblr ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    opciones = []

    if item.title == 'Por época': 
        opciones = labels_epocas
        grupo = 'epocas'
    elif item.title == 'Por país':
        opciones = labels_paises
        grupo = 'paises'
    else:
        opciones = labels_generos
        grupo = 'generos'

    for label in opciones:
        title = label.replace('%2F', '-')

        title = title.replace('Cinenegro', 'Cine negro')
        title = title.replace('AsesinosEnSerie', 'Asesinos en serie').replace('ExpresionismoAlemán', 'Expresionismo Alemán')
        title = title.replace('CineDCine', 'Cine D Cine').replace('CineMudo', 'Cine Mudo').replace('CineQuinqui', 'Cine Quinqui')

        if grupo == 'generos':
            if title == 'Erótico':
                if descartar_xxx: continue

        label = label.replace('/', '%2F')

        itemlist.append(item.clone( title = title, url = host + 'search/label/' + label, action = 'list_all', grupo = grupo ))

    return itemlist

# Por si viene del menu de Agrupaciones
def paises(item):
    logger.info()

    item.title = 'Por país'
    return generos(item)


def list_all(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, "<div class='post bar hentry'>(.*?)<span class='post-labels'>")

    for match in matches:
        url = scrapertools.find_single_match(match, " href='(.*?)'")

        if '/ver-las-150-mejores-peliculas-de-la.html' in url: continue
        elif '/ver-las-150-mejores-peliculas-de-cine.html' in url: continue
        elif '/mejores-250-peliculas-de-la-historia.html' in url: continue

        title = scrapertools.find_single_match(match, "itemprop='name'>.*?>(.*?)</a>").strip()

        if not url or not title: continue

        title = title.lower()
        title = title.capitalize()

        title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ').replace('Ü', 'ú')

        if 'itemprop="datePublished"' in match: year = scrapertools.find_single_match(match, 'itemprop="datePublished".*?">(.*?)</dd>')
        else: year = scrapertools.find_single_match(match, '>Año<.*?">(.*?)</dd>')

        year = year.replace('<b>', '').replace('</b>', '')

        if len(year) > 4:
            year = scrapertools.find_single_match(match, '</dd><dd itemprop="datePublished".*?">(.*?)</dd>')
            if len(year) > 4: year = scrapertools.find_single_match(match, '</dd><dd itemprop="datePublished".*?</dd><dd itemprop="datePublished".*?">(.*?)</dd>')

        if len(year) > 4:
            year = year.replace('<b>', '').replace('</b>', '')
            if len(year) > 4: year = ''

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')

        if 'filmaffinity.com/' in thumb: thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        part_title = title.split(' - ')[0].strip()
        part_title = part_title.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

        if year:
            if ' (' + year + ')' in part_title: part_title = part_title.split(' (' + year + ')')[0].strip()
            elif ' ' + year + ')' in part_title: part_title = part_title.split(' ' + year + ')')[0].strip()
            elif year in part_title: part_title = part_title.split(year)[0].strip()

            if ' (' + year + ')' in title: title = title.replace(' (' + year + ')', '').strip()
            elif ' ' + year + ')' in title: title = title.replace(' ' + year + ')', ')').strip()
            elif year in title: title = title.replace(year, '').strip()

        if not year: year = '-'

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie',
                                    contentTitle = part_title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if "<a class='blog-pager-older-link' href='" in data:
        next_page = scrapertools.find_single_match(data, "<a class='blog-pager-older-link' href='(.*?)'")
        next_page = next_page.replace('&amp;', '&')

        if next_page:
            data_next = httptools.downloadpage(next_page).data
            matches = scrapertools.find_multiple_matches(data_next, "<div class='post bar hentry'>(.*?)<span class='post-labels'>")
            if matches:
               itemlist.append(item.clone( title = 'Siguientes ...', url = next_page, action = 'list_all', text_color='coral' ))

    return itemlist


def list_labels(item): 
    logger.info()
    itemlist = []

    sort_labels = []

    perpage = 50

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    final = '<h2>'
    if item.group == 'ACTORES':
        final = '>TRIBUNA'

    bloque = scrapertools.find_single_match(data, ">" + str(item.group) + "(.*?)" + final)

    matches = scrapertools.find_multiple_matches(bloque, "<a dir='ltr'.*?href='(.*?)'>(.*?)</a>")

    i = 0

    for url, title in matches:
        title = title.replace('&amp;', '&')

        title = title.replace(';', '')

        i +=1

        sort_labels.append([url, title])

    if not i == 0:
        num_matches = i -1
        desde = item.page * perpage
        hasta = desde + perpage

        sort_labels = sorted(sort_labels, key = lambda x: x[1])

        for url, title in sort_labels[desde:hasta]:
             itemlist.append(item.clone( action = 'list_all', url = url, title = title ))

        if i > perpage:
            if num_matches > hasta:
                next_page = item.page + 1
                itemlist.append(item.clone( title = 'Siguientes ...', page = next_page, action = 'list_labels', text_color='coral' ))

    return itemlist


def list_best(item): 
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'data-movie-id="(.*?)<div class="credits">')

    num_matches = len(matches)
    desde = item.page * perpage
    hasta = desde + perpage

    for match in matches[desde:hasta]:
        url = scrapertools.find_single_match(match, '<div class="mc-title" style="margin-bottom.*?<a href="' + host + '([^"]+)"')

        title = scrapertools.find_single_match(match, '<img alt="([^"]+)"').strip()

        title = title.replace('Á', 'á').replace('É', 'é').replace('Í', 'í').replace('Ó', 'ó').replace('Ú', 'ú').replace('Ñ', 'ñ').replace('Ü', 'ú')

        if not url:
            if title == 'El tercer hombre': url = '2018/10/el-tercer-hombre-1949-carol-reed.html'
            elif title == 'Apur Sansar (El mundo de Apu)': url = '2018/10/apur-sansar-el-mundo-de-apu-1959.html'

        if '2018/10/cinema-paradiso-1988-vose-y-castellano.html' in url: url = ''
        elif '2017/08/uno-dos-tres-one-two-three-billy-wilder.html' in url: url = ''

        if not url or not title: continue

        if url == '2017/07/el-caballero-oscuro-2008.html': url = '2020/05/el-caballero-oscuro.html'

        url = host + url

        thumb = scrapertools.find_single_match(match, 'src="(.*?)"')

        if 'filmaffinity.com/' in thumb: thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        year = scrapertools.find_single_match(match, '</span>&nbsp;(.*?)&nbsp;')
        if not year: year = scrapertools.find_single_match(match, '</a>&nbsp;(.*?)&nbsp;')
        if not year: year = scrapertools.find_single_match(match, '</span>(.*?)&nbsp;')
        if not year: year = scrapertools.find_single_match(match, '&nbsp;</a>(.*?)&nbsp;')
        if not year: year = scrapertools.find_single_match(match, '&nbsp;(.*?)&nbsp;')
        if not year: year = scrapertools.find_single_match(match, '&nbsp;</b></span>(.*?)&nbsp;')

        year = year.replace('</span>', '').replace('(', '').replace(')', '').strip()

        if not year: year = '-'

        mod_title = title.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie',
                                    contentTitle = mod_title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if num_matches > hasta:
        next_page = item.page + 1
        itemlist.append(item.clone( title = 'Siguientes ...', page = next_page, action = 'list_best', text_color='coral' ))

    return itemlist


def list_tumblr(item): 
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<article class="post-link" id="(.*?)</article>')

    i = 0

    for article in matches:
        url_redir = scrapertools.find_single_match(article, ' href="([^"]+)')
        url_redir = url_redir.replace('https://href.li/?', '').replace('&amp;', '&').strip()
        if not url_redir: continue

        if not 'mycinedesiempre.blogspot.com' in url_redir: continue
        elif not '.html' in url_redir: continue

        url = url_redir.replace('%3A', ':').replace('%2F', '/')

        title = scrapertools.find_single_match(article, '<h2>(.*?)<i').strip()
        if not title: continue

        if 'ver las 150 mejores' in title.lower(): continue
        elif 'las mejores 200' in title.lower(): continue

        title = title.lower()
        title = title.capitalize()

        if title.startswith('&') == True:
            title = title.replace('&aacute;', 'Á').replace('&eacute;', 'É').replace('&iacute;', 'Í').replace('&oacute;', 'Ó').replace('&uacute;', 'Ú').replace('&ntilde;', 'Ñ')

        thumb = scrapertools.find_single_match(article, ' src="([^"]+)')

        if 'filmaffinity.com/' in thumb: thumb = thumb.replace('-msmall', '-large') + '|User-Agent=Mozilla/5.0'

        year = scrapertools.find_single_match(title, '(\d{4})')
        if not year:
            year = scrapertools.find_single_match(article, '"post-link-excerpt">(.*?)</p>')
            year = scrapertools.find_single_match(year, '(\d{4})')

        if year:
            title = title.replace(year, '').replace('()', '').replace(', )', ')')

        if not year: year = '-'

        mod_title = title.replace('&aacute;', 'á').replace('&eacute;', 'é').replace('&iacute;', 'í').replace('&oacute;', 'ó').replace('&uacute;', 'ú').replace('&ntilde;', 'ñ')
        mod_title = mod_title.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

        if '(' in mod_title: mod_title = mod_title.split('(')[0].strip()
        elif '-' in mod_title: mod_title = mod_title.split('-')[0].strip()

        i += 1

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, contentType = 'movie',
                                    contentTitle = mod_title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if not i == 0:
        if '<div class="pagination ">' in data:
            next_page = scrapertools.find_single_match(data, '<div class="pagination ">.+?class="scroll-top"></a>.*?<a href="([^"]+)"')

            if next_page:
                if not next_page == '/page/16':
                   url = 'https://cinedesiempre.tumblr.com' + next_page
                   itemlist.append(item.clone( title = 'Siguientes ...', url = url, action = 'list_tumblr', text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    if '/filmografia-' in item.url:
        return itemlist
    elif '/ver-coleccion-' in item.url:
        return itemlist

    items_play = []

    data = httptools.downloadpage(item.url).data

    if '>Sinopsis<' in data:
        part_data = scrapertools.find_single_match(data, '>Sinopsis<(.*?)Share this article')
    elif "<h1 class='post-title entry-title' itemprop='name'>": 
        part_data = scrapertools.find_single_match(data, "<h1 class='post-title entry-title' itemprop='name'>(.*?)Share this article")
    else: part_data = data

    langs = find_idioma_cast(part_data)
    if not langs:
        langs = find_idioma_cast(part_data.lower())
        if not langs:
            if '>vose<' in part_data.lower(): 
                matches = scrapertools.find_multiple_matches(part_data.lower(), '>enlace(.*?)</a>')
                if matches: langs = 'Esp'

    if '>latino</dd>' in part_data.lower(): langs = find_idiomas(part_data, langs, 'latino', 'Lat')

    langs = find_idiomas(part_data, langs, 'vose', 'Vose')

    if not langs:
        titulo = scrapertools.find_single_match(data, "<h1 class='post-title entry-title' itemprop='name'>(.*?)</h1>").strip()
        titulo = titulo.lower()
        if 'v.o.s.e.' in titulo or 'vose' in titulo: langs = 'Vose'

    if '<iframe allow="autoplay' in data:
        matches = scrapertools.find_multiple_matches(data, '<iframe allow="autoplay.*?src="([^"]+)"')
        if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

        matches = scrapertools.find_multiple_matches(data, '<iframe allow="autoplay.*?<a href="([^"]+)"')
        if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))
    elif '<iframe src=' in data:
        matches = scrapertools.find_multiple_matches(data, '<iframe src="([^"]+)"')
        if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

        matches = scrapertools.find_multiple_matches(data, "<iframe src='([^']+)'")
        if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

    elif '<iframe <a href=' in data:
        matches = scrapertools.find_multiple_matches(data, '<iframe <a href="([^"]+)"')
        if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

    if '>Sinopsis<' in data:
        bloque = scrapertools.find_single_match(data, '>Sinopsis<(.*?)Share this article')
        matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
        if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

        if '<iframe allow="accelerometer' in data:
           matches = scrapertools.find_multiple_matches(data, '<iframe allow="accelerometer.*?src="([^"]+)"')
           if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))
           else:
              matches = scrapertools.find_multiple_matches(data, '<iframe.*?allow=".*?src="([^"]+)"')
              if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist), items_play, langs)

        elif 'allow="accelerometer' in data:
           bloque = scrapertools.find_single_match(data, 'allow="accelerometer(.*?)Share this article')
           matches = scrapertools.find_multiple_matches(bloque, 'src="([^"]+)"')
           if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

    else:

        if '<div class="movie-info-sinopsis"' in data:
            bloque = scrapertools.find_single_match(data, '<div class="movie-info-sinopsis(.*?)Share this article')
            matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
            if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

            if not '<iframe allowfullscreen=' in data:
                if '<iframe allow="accelerometer' in data:
                    matches = scrapertools.find_multiple_matches(data, '<iframe allow="accelerometer.*?src="([^"]+)"')
                    if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

        elif '<iframe allow="accelerometer' in data:
           if '<iframe allowfullscreen=' in data: bloque = scrapertools.find_single_match(data, '<iframe allow="accelerometer(.*?)<iframe allowfullscreen=')
           else: bloque = scrapertools.find_single_match(data, '<iframe allow="accelerometer(.*?)</div>')

           matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
           if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

           if not bloque:
               if '<iframe allowfullscreen=' in data:
                   bloque = scrapertools.find_single_match(data, '<iframe allowfullscreen=(.*?)Share this article')
                   matches = scrapertools.find_multiple_matches(bloque, 'src="([^"]+)"')
                   if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

        elif '<dl class="margin-top movie-info' in data:
           matches = scrapertools.find_multiple_matches(data, '<dl class="margin-top movie-info.*?<a href="([^"]+)"')
           if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

    if '<iframe allowfullscreen=' in data:
        if not '>Sinopsis<' in data:
            if not '<div class="movie-info-sinopsis"' in data:
               if not '<iframe allow="accelerometer' in data:
                   matches = scrapertools.find_multiple_matches(data, '<b><a href="([^"]+)"')
                   if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))
                   else:
                      matches = scrapertools.find_multiple_matches(data, '<br />.*?<a href="([^"]+)"')
                      itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

        matches = scrapertools.find_multiple_matches(data, '<iframe allowfullscreen=.*?<a href="([^"]+)"')
        if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

        matches = scrapertools.find_multiple_matches(data, '<iframe allowfullscreen=.*?src="([^"]+)"')
        if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

    else:

        if not '>Sinopsis<' in data:
            if not '<div class="movie-info-sinopsis"' in data:
                if not '<iframe allow="accelerometer' in data:
                   bloque = scrapertools.find_single_match(data, '<br />(.*?)Share this article')
                   matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
                   if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

                   if 'charset="UTF-8"' in data:
                      bloque = scrapertools.find_single_match(data, 'charset="UTF-8"(.*?)Share this article')
                      matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
                      if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

                   if "<h1 class='post-title entry-title'" in data:
                      bloque = scrapertools.find_single_match(data, "<h1 class='post-title entry-title'(.*?)Share this article")
                      matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
                      if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

                else:

                   bloque = scrapertools.find_single_match(data, '<b><span(.*?)Share this article')
                   matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
                   if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

                   bloque = scrapertools.find_single_match(data, '<br />(.*?)Share this article')
                   matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
                   if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

                   bloque = scrapertools.find_single_match(data, '<iframe allow="accelerometer(.*?)Share this article')
                   matches = scrapertools.find_multiple_matches(bloque, 'src="([^"]+)"')
                   if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

    if not itemlist:
        if '>sinopsis<' in data.lower():
            bloque = scrapertools.find_single_match(data.lower(), '>sinopsis<(.*?)share this article')
            matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
            if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))
        elif "<div class='post-body entry-content'>" in data:
            bloque = scrapertools.find_single_match(data, "<div class='post-body entry-content'>(.*?)Share this article")
            matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)"')
            if matches: itemlist, items_play = (get_enlaces(item, matches, itemlist, items_play, langs))

    return itemlist


def get_enlaces(item, matches, itemlist, items_play, langs):
    logger.info()

    if not langs: langs = 'Esp, Vo'

    for url in matches:
        if not url: continue

        if url.startswith('//') == True: url = 'https:' + url

        if 'https://draft.blogger.com/%22http' in url: url = url.replace('https://draft.blogger.com/%22http', 'http')

        if not url.startswith('http') == True: continue

        if '/cloudvideo.tv/emb.html?' in url:
            if '=' in url:
                url = url.split('=')[0]
                url = url.replace('/emb.html?', '/embed-') + '.html'
        elif '/video.tlencloud.com/' in url: url = url.replace('/video.tlencloud.com/', '/tlencloud.com/')

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        if servidor == 'directo':
            link_other = normalize_other(url)
            if not link_other: continue
        else: link_other = ''

        url = servertools.normalize_url(servidor, url)

        if '/www.ccplm.cl/' in url: url = get_link_ccplm(url)

        if url:
            if not url in items_play:
                url = url.replace('https://www.adf.ly/6680622/banner/', '').replace('&amp;', '&')

                if items_play:
                    if 'youtube.com/' in url: continue

                items_play.append(url)

                itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = langs, other = link_other ))

    return itemlist, items_play


def get_link_ccplm(url):
    try:
        data = httptools.downloadpage(url).data
        url_link = scrapertools.find_single_match(data, '<iframe class="embed-responsive-item".*?src="(.*?)"').strip()

        if url_link.startswith('//') == True: url_link = 'https:' + url_link

        url_link = url_link.replace('&amp;', '&')

        data_link = httptools.downloadpage(url_link).data
        url = scrapertools.find_single_match(data_link, '"mp4":"(.*?)"')
    except:
        url = ''

    return url


def normalize_other(url):
    if url == '/': return ''
    elif 'martin%20hache%20pelicula' in url: return ''
    elif 'straight%20shootin' in url: return ''
    elif url.endswith(".jpg") == True: return ''
    elif url.endswith(".jpeg") == True: return ''
    elif url.endswith(".png") == True: return ''
    elif url.endswith(".gif") == True: return ''
    elif url.endswith(".js") == True: return ''

    elif 'vimeo.com' in url:
          if not '/video/' in url: return ''
          else: return 'vimeo'

    elif 'mega.nz/' in url: return 'mega'
    elif 'my.mail.ru/' in url: return 'mailru'
    elif 'myvi.ru/' in url: return 'myvi'
    elif 'ok.ru/' in url: return 'okru'
    elif 'vk.com/' in url: return 'vk'
    elif 'archive.org/' in url: return'archiveorg'
    elif 'gloria.tv/' in url: return 'gloria'
    elif '2000peliculassigloxx.com/' in url: return 'sigloxx'

    else:
         if '%20' in url: return ''

         try:
             if config.get_setting('developer_mode', default=False):
                 if 'filmaffinity.' in url or 'blogspot.' in url or 'blogger.' in url: url = ''
                 elif 'facebook.' in url or 'twitter.' in url or 'google.' in url or '.perfil.' in url: url = ''
                 elif 'film/reviews/' in url or 'filmreviews/' in url or '/reviews/' in url or '/webstore/' in url: url = ''
                 elif 'documaniatv.' in url or 'cinemania.' in url or 'cineypsicologia.' in url or 'lasmejorespeliculasdelahistoriadelcine.' in url: url = ''
                 elif 'youtube.com/playlist' in url or 'youtube.com/channel' in url: url = ''

                 if not url: return ''

                 link_other = url.split('//')[1]
                 link_other = link_other.split('/')[0]

                 link_other = link_other.replace('www.', '').replace('.com', '').replace('.net', '').replace('.org', '').replace('.co', '').replace('.cc', '')
                 link_other = link_other.replace('.to', '').replace('.tv', '').replace('.ru', '').replace('.io', '').replace('.eu', '').replace('.ws', '')

                 link_other = servertools.corregir_servidor(link_other)

                 if link_other == 'netutv': link_other = ''
                 elif link_other == 'powvideo': link_other = ''
                 elif link_other == 'streamplay': link_other = ''
                 elif link_other == 'uploadedto': link_other = ''

                 elif 'openload' in link_other: link_other = ''
                 elif '/oload.' in link_other: link_other = ''
                 elif 'rapidvideo' in link_other: link_other = ''
                 elif 'streamango' in link_other: link_other = ''
                 elif 'streamcloud' in link_other: link_other = ''
                 elif '/thevid.' in link_other: link_other = ''
                 elif 'thevideo.' in link_other: link_other = ''
                 elif 'uploadmp4' in link_other: link_other = ''
                 elif 'jetload' in link_other: link_other = ''
                 elif 'vidcloud' in link_other: link_other = ''
                 elif 'rapidvid' in link_other: link_other = ''
                 elif 'onlystream' in link_other: link_other = ''
                 elif 'verystream' in link_other: link_other = ''

                 return link_other

             servidor = servertools.get_server_from_url(url)
             servidor = servertools.corregir_servidor(servidor)

             if servidor and servidor != 'directo': return servidor
             return ''
         except:
             if '+d[e].link+' in url: return ''
             return '?'

    return url


def find_idioma_cast(part_data):
    langs = find_idiomas(part_data, '', 'castellano', 'Esp')

    if not langs: langs = find_idiomas(part_data, langs, 'cast', 'Esp')
    if not langs: langs = find_idiomas(part_data, langs, 'spanish', 'Esp')

    return langs


def find_idiomas(part_data, langs, texto, valor):
    langs_idioma = langs_idiomas(texto)

    if texto == 'vose': langs_idioma.append ('enlace v.o.s.e.')

    elem = len(langs_idioma)

    i = 0

    while i < elem:
       if langs_idioma[i] in part_data.lower():
           if langs: langs = langs + ', ' + valor
           else: langs = valor
           return langs

       i += 1
       if i == elem: break

    return langs


def langs_idiomas(tex):
    langs = [
          ('<b>' + tex + '</b>'),
          ('<b>' + tex + '<script'),
          ('<u>' + tex + '</u>'),
          ('<i>' + tex + '</i>'),
          ('>online ' + tex),
          ('-' + tex + ' '),
          (' ' + tex + '-'),
          ('online ' + tex),
          ('ver en ' + tex),
          ('online-' + tex),
          ('online 1 ' + tex),
          ('online 1-' + tex),
          ('online 2 ' + tex),
          ('online 2-' + tex),
          ('descarga ' + tex),
          ('descarga-' + tex),
          ('enlace ' + tex),
          ('enlace 1 ' + tex),
          ('enlace 1-' + tex),
          ('enlace 1 - ' + tex),
          ('enlace 2 ' + tex),
          ('enlace 2-' + tex),
          ('enlace 2 - ' + tex),
          ('1-' + tex),
          ('1 - ' + tex),
          ('2-' + tex),
          ('2 - ' + tex),
          ('online/desc ' + tex),
          ('online/desc.' + tex),
          ('online/' + tex),
          ('online/descarga ' + tex),
          ('online / descarga ' + tex),
          ('>' + tex + ' ver'),
          ('>' + tex + ' online'),
          ('>' + tex + ' '),
          ('>' + tex + '</span>'),
          (tex + '-online'),
          (tex + ' on line'),
          (tex + ', enlace'),
          (tex + '<br />'),
          (tex + '</b>'),
          (tex + '</div>'),
          ('>' + tex + '<'),
          (';' + tex + '<'),
          (' ' + tex + ' '),
          ('&nbsp; ' + tex),
          ('&nbsp;' + tex),
          (tex + '&nbsp;'),
          ('&#161;' + tex),
          (';&#161;     ' + tex),
          (tex + '#161;'),
          ('--' + tex),
          (tex)
          ]

    return langs


def _besthistoria(item):
    logger.info()

    item.url = host + '2018/11/ver-las-150-mejores-peliculas-de-la.html'

    return list_best(item)

def _bestcinespa(item):
    logger.info()

    item.url = host + '2021/04/ver-las-100-mejores-peliculas-de-la.html'

    return list_best(item)

def _bestcinenegro(item):
    logger.info()

    item.url = host + '2020/10/ver-las-150-mejores-peliculas-de-cine.html'

    return list_best(item)

def _bestcinedesiempre(item):
    logger.info()

    item.url = 'https://cinedesiempre.tumblr.com'

    return list_tumblr(item)


def search(item, texto):
    logger.info()
    try:
        texto = texto.replace(" ", "+")
        item.url = host + 'search?q=' + texto
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

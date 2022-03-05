# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, jsontools, tmdb


host = 'https://verpeliculasgratis.in/'

ruta_pelis  = 'browse?type=movie'
ruta_series = 'browse?type=series'


def do_downloadpage(url, post=None, headers=None):
    data = httptools.downloadpage(url, post=post, headers=headers, timeout = 20).data

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

    itemlist.append(item.clone( title = 'Últimas (fecha lanzamiento)', action = 'list_all', url = host + ruta_pelis, orden = 'release_date:desc', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más recientes (agregadas)', action = 'list_all', url = host + ruta_pelis, orden = 'created_at:desc', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + ruta_pelis, orden = 'popularity:desc', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + ruta_pelis, orden = 'user_score:desc', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por calificación de edad', action = 'edades', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Últimas (fecha lanzamiento)', action = 'list_all', url = host + ruta_series, orden = 'release_date:desc', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más recientes (agregadas)', action = 'list_all', url = host + ruta_series, orden = 'created_at:desc', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Más populares', action = 'list_all', url = host + ruta_series, orden = 'popularity:desc', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + ruta_series, orden = 'user_score:desc', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por calificación de edad', action = 'edades', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist=[]

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if item.search_type not in ['movie', 'tvshow']: item.search_type = 'movie'
    url = host + (ruta_pelis if item.search_type == 'movie' else ruta_series)

    generos = [
       'acción',
       'animación',
       'aventura',
       'bélica',
       'ciencia-ficción', 
       'comedia',
       'crimen',
       'documental',
       'drama',
       'familia',
       'fantasía',
       'historia',
       'kids',
       'misterio',
       'música',
       'reality',
       'romance',
       'soap',
       'suspense',
       'terror',
       'thriller',
       'western'
       ]

    for genero in generos:
        if item.search_type == 'movie':
            if genero == 'kids': continue
            elif genero == 'reality': continue
            elif genero == 'soap': continue

        itemlist.append(item.clone( action = 'list_all', title = genero.capitalize(), url = url, genero = genero ))

    if item.search_type == 'movie' and not descartar_xxx:
        itemlist.append(item.clone( action = 'list_all', title = 'xxx / adultos', url = host + ruta_pelis, calificacion = 'nc-17' ))

    return itemlist


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    url = host + (ruta_pelis if item.search_type == 'movie' else ruta_series)
    to_year = 1979 if item.search_type == 'tvshow' else 1935

    for x in range(current_year, to_year, -1):
        itemlist.append(item.clone( title=str(x), url = url, orden = '&released=' + str(x) + ',' + str(x), action='list_all' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist=[]

    web_paises = [
       ['af', 'Afghanistan'],
       ['ax', 'Åland Islands'],
       ['al', 'Albania'],
       ['dz', 'Algeria'],
       ['as', 'American Samoa'],
       ['ad', 'Andorra'],
       ['ao', 'Angola'],
       ['ai', 'Anguilla'],
       ['aq', 'Antarctica'],
       ['ag', 'Antigua & Barbuda'],
       ['ar', 'Argentina'],
       ['am', 'Armenia'],
       ['aw', 'Aruba'],
       ['ac', 'Ascension Island'],
       ['au', 'Australia'],
       ['at', 'Austria'],
       ['az', 'Azerbaijan'],
       ['bs', 'Bahamas'],
       ['bh', 'Bahrain'],
       ['bd', 'Bangladesh'],
       ['bb', 'Barbados'],
       ['by', 'Belarus'],
       ['be', 'Belgium'],
       ['bz', 'Belize'],
       ['bj', 'Benin'],
       ['bm', 'Bermuda'],
       ['bt', 'Bhutan'],
       ['bo', 'Bolivia'],
       ['ba', 'Bosnia & Herzegovina'],
       ['bw', 'Botswana'],
       ['br', 'Brazil'],
       ['io', 'British Indian Ocean Territory'],
       ['vg', 'British Virgin Islands'],
       ['bn', 'Brunei'],
       ['bg', 'Bulgaria'],
       ['bf', 'Burkina Faso'],
       ['bi', 'Burundi'],
       ['kh', 'Cambodia'],
       ['cm', 'Cameroon'],
       ['ca', 'Canada'],
       ['ic', 'Canary Islands'],
       ['cv', 'Cape Verde'],
       ['bq', 'Caribbean Netherlands'],
       ['ky', 'Cayman Islands'],
       ['cf', 'Central African Republic'],
       ['ea', 'Ceuta & Melilla'],
       ['td', 'Chad'],
       ['cl', 'Chile'],
       ['cn', 'China'],
       ['cx', 'Christmas Island'],
       ['cc', 'Cocos (Keeling) Islands'],
       ['co', 'Colombia'],
       ['km', 'Comoros'],
       ['cg', 'Congo - Brazzaville'],
       ['cd', 'Congo - Kinshasa'],
       ['ck', 'Cook Islands'],
       ['cr', 'Costa Rica'],
       ['ci', 'Côte d’Ivoire'],
       ['hr', 'Croatia'],
       ['cu', 'Cuba'],
       ['cw', 'Curaçao'],
       ['cy', 'Cyprus'],
       ['cz', 'Czech Republic'],
       ['dk', 'Denmark'],
       ['dg', 'Diego Garcia'],
       ['dj', 'Djibouti'],
       ['dm', 'Dominica'],
       ['do', 'Dominican Republic'],
       ['ec', 'Ecuador'],
       ['eg', 'Egypt'],
       ['sv', 'El Salvador'],
       ['gq', 'Equatorial Guinea'],
       ['er', 'Eritrea'],
       ['ee', 'Estonia'],
       ['et', 'Ethiopia'],
       ['fk', 'Falkland Islands'],
       ['fo', 'Faroe Islands'],
       ['fj', 'Fiji'],
       ['fi', 'Finland'],
       ['fr', 'France'],
       ['gf', 'French Guiana'],
       ['pf', 'French Polynesia'],
       ['tf', 'French Southern Territories'],
       ['ga', 'Gabon'],
       ['gm', 'Gambia'],
       ['ge', 'Georgia'],
       ['de', 'Germany'],
       ['gh', 'Ghana'],
       ['gi', 'Gibraltar'],
       ['gr', 'Greece'],
       ['gl', 'Greenland'],
       ['gd', 'Grenada'],
       ['gp', 'Guadeloupe'],
       ['gu', 'Guam'],
       ['gt', 'Guatemala'],
       ['gg', 'Guernsey'],
       ['gn', 'Guinea'],
       ['gw', 'Guinea-Bissau'],
       ['gy', 'Guyana'],
       ['ht', 'Haiti'],
       ['hn', 'Honduras'],
       ['hk', 'Hong Kong SAR China'],
       ['hu', 'Hungary'],
       ['is', 'Iceland'],
       ['in', 'India'],
       ['id', 'Indonesia'],
       ['ir', 'Iran'],
       ['iq', 'Iraq'],
       ['ie', 'Ireland'],
       ['im', 'Isle of Man'],
       ['il', 'Israel'],
       ['it', 'Italy'],
       ['jm', 'Jamaica'],
       ['jp', 'Japan'],
       ['je', 'Jersey'],
       ['jo', 'Jordan'],
       ['kz', 'Kazakhstan'],
       ['ke', 'Kenya'],
       ['ki', 'Kiribati'],
       ['xk', 'Kosovo'],
       ['kw', 'Kuwait'],
       ['kg', 'Kyrgyzstan'],
       ['la', 'Laos'],
       ['lv', 'Latvia'],
       ['lb', 'Lebanon'],
       ['ls', 'Lesotho'],
       ['lr', 'Liberia'],
       ['ly', 'Libya'],
       ['li', 'Liechtenstein'],
       ['lt', 'Lithuania'],
       ['lu', 'Luxembourg'],
       ['mo', 'Macau SAR China'],
       ['mk', 'Macedonia'],
       ['mg', 'Madagascar'],
       ['mw', 'Malawi'],
       ['my', 'Malaysia'],
       ['mv', 'Maldives'],
       ['ml', 'Mali'],
       ['mt', 'Malta'],
       ['mh', 'Marshall Islands'],
       ['mq', 'Martinique'],
       ['mr', 'Mauritania'],
       ['mu', 'Mauritius'],
       ['yt', 'Mayotte'],
       ['mx', 'Mexico'],
       ['fm', 'Micronesia'],
       ['md', 'Moldova'],
       ['mc', 'Monaco'],
       ['mn', 'Mongolia'],
       ['me', 'Montenegro'],
       ['ms', 'Montserrat'],
       ['ma', 'Morocco'],
       ['mz', 'Mozambique'],
       ['mm', 'Myanmar (Burma)'],
       ['na', 'Namibia'],
       ['nr', 'Nauru'],
       ['np', 'Nepal'],
       ['nl', 'Netherlands'],
       ['nc', 'New Caledonia'],
       ['nz', 'New Zealand'],
       ['ni', 'Nicaragua'],
       ['ne', 'Niger'],
       ['ng', 'Nigeria'],
       ['nu', 'Niue'],
       ['nf', 'Norfolk Island'],
       ['kp', 'North Korea'],
       ['mp', 'Northern Mariana Islands'],
       ['no', 'Norway'],
       ['om', 'Oman'],
       ['pk', 'Pakistan'],
       ['pw', 'Palau'],
       ['ps', 'Palestinian Territories'],
       ['pa', 'Panama'],
       ['pg', 'Papua New Guinea'],
       ['py', 'Paraguay'],
       ['pe', 'Peru'],
       ['ph', 'Philippines'],
       ['pn', 'Pitcairn Islands'],
       ['pl', 'Poland'],
       ['pt', 'Portugal'],
       ['pr', 'Puerto Rico'],
       ['qa', 'Qatar'],
       ['re', 'Réunion'],
       ['ro', 'Romania'],
       ['ru', 'Russia'],
       ['rw', 'Rwanda'],
       ['ws', 'Samoa'],
       ['sm', 'San Marino'],
       ['st', 'São Tomé & Príncipe'],
       ['sa', 'Saudi Arabia'],
       ['sn', 'Senegal'],
       ['rs', 'Serbia'],
       ['sc', 'Seychelles'],
       ['sl', 'Sierra Leone'],
       ['sg', 'Singapore'],
       ['sx', 'Sint Maarten'],
       ['sk', 'Slovakia'],
       ['si', 'Slovenia'],
       ['sb', 'Solomon Islands'],
       ['so', 'Somalia'],
       ['za', 'South Africa'],
       ['gs', 'South Georgia & South Sandwich Islands'],
       ['kr', 'South Korea'],
       ['ss', 'South Sudan'],
       ['es', 'Spain'],
       ['lk', 'Sri Lanka'],
       ['bl', 'St. Barthélemy'],
       ['sh', 'St. Helena'],
       ['kn', 'St. Kitts & Nevis'],
       ['lc', 'St. Lucia'],
       ['mf', 'St. Martin'],
       ['pm', 'St. Pierre & Miquelon'],
       ['vc', 'St. Vincent & Grenadines'],
       ['sd', 'Sudan'],
       ['sr', 'Suriname'],
       ['sj', 'Svalbard & Jan Mayen'],
       ['sz', 'Swaziland'],
       ['se', 'Sweden'],
       ['ch', 'Switzerland'],
       ['sy', 'Syria'],
       ['tw', 'Taiwan'],
       ['tj', 'Tajikistan'],
       ['tz', 'Tanzania'],
       ['th', 'Thailand'],
       ['tl', 'Timor-Leste'],
       ['tg', 'Togo'],
       ['tk', 'Tokelau'],
       ['to', 'Tonga'],
       ['tt', 'Trinidad & Tobago'],
       ['ta', 'Tristan da Cunha'],
       ['tn', 'Tunisia'],
       ['tr', 'Turkey'],
       ['tm', 'Turkmenistan'],
       ['tc', 'Turks & Caicos Islands'],
       ['tv', 'Tuvalu'],
       ['um', 'U.S. Outlying Islands'],
       ['vi', 'U.S. Virgin Islands'],
       ['ug', 'Uganda'],
       ['ua', 'Ukraine'],
       ['ae', 'United Arab Emirates'],
       ['gb', 'United Kingdom'],
       ['us', 'United States'],
       ['uy', 'Uruguay'],
       ['uz', 'Uzbekistan'],
       ['vu', 'Vanuatu'],
       ['va', 'Vatican City'],
       ['ve', 'Venezuela'],
       ['vn', 'Vietnam'],
       ['wf', 'Wallis & Futuna'],
       ['eh', 'Western Sahara'],
       ['ye', 'Yemen'],
       ['zm', 'Zambia'],
       ['zw', 'Zimbabwe']
       ]

    url = host + (ruta_pelis if item.search_type == 'movie' else ruta_series)

    for x in web_paises:
        itemlist.append(item.clone( title = x[1], url = url, orden = '&country=' + str(x[0]), action = 'list_all' ))

    return itemlist


def edades(item):
    logger.info()
    itemlist=[]

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if item.search_type not in ['movie', 'tvshow']: item.search_type = 'movie'
    url = host + (ruta_pelis if item.search_type == 'movie' else ruta_series)

    itemlist.append(item.clone( title = 'G (General Audiences)', action = 'list_all', url = url, calificacion = 'g', plot='Admitido para todas las edades.' ))
    itemlist.append(item.clone( title = 'PG (Parental Guidance Suggested)', action = 'list_all', url = url, calificacion = 'pg', plot='Algunos contenidos pueden no ser apropiados para niños.' ))
    itemlist.append(item.clone( title = 'PG-13 (Parents Strongly Cautioned)', action = 'list_all', url = url, calificacion = 'pg-13', plot='Algunos materiales pueden ser inapropiados para niños de menos de 13 años.' ))
    itemlist.append(item.clone( title = 'R (Restricted)', action = 'list_all', url = url, calificacion = 'r', plot='Personas de menos de 17 años requieren acompañamiento de un adulto.' ))

    if item.search_type == 'movie':
       if not descartar_xxx:
           itemlist.append(item.clone( title = 'NC-17 (Adults Only)', action = 'list_all', url = url, calificacion = 'nc-17', plot='Solamente adultos. No admitido para menores de 18 años.' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = '1'
    if not item.orden: item.orden = 'popularity:desc'

    tipo = 'movie' if item.search_type == 'movie' else 'series'

    url = host + 'secure/titles?type=%s&order=%s&onlyStreamable=true&page=%s' % (tipo, item.orden, item.page)
    if item.genero: url += '&genre=' + item.genero
    if item.calificacion: url += '&certification=' + item.calificacion

    data = do_downloadpage(url)

    dict_data = jsontools.load(data)

    if 'pagination' not in dict_data: return itemlist

    for element in dict_data['pagination']['data']:
        thumb = element['poster'] if element['poster'] else item.thumbnail
        new_item = item.clone( title = element['name'], thumbnail = thumb, infoLabels = {'year':element['year'], 'plot': element['description']})

        new_item.url = host + 'secure/titles/' + str(element['id']) + '?titleId=' + str(element['id'])

        if not element['is_series']:
            new_item.action = 'findvideos'
            new_item.contentType = 'movie'
            new_item.contentTitle = element['name']
        else:
            new_item.action = 'temporadas'
            new_item.contentType = 'tvshow'
            new_item.contentSerieName = element['name']

        itemlist.append(new_item)

    tmdb.set_infoLabels(itemlist)

    if dict_data['pagination']['next_page_url']:
        itemlist.append(item.clone( title = 'Siguientes ...', page = dict_data['pagination']['next_page_url'].replace('/?page=', ''),
		                            action='list_all', text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    dict_data = jsontools.load(data)

    if 'title' not in dict_data: return itemlist

    # averiguar temporadas
    tot_temp = 0

    for element in dict_data['title']['seasons']:
        tot_temp += 1
        if tot_temp > 1: break

    for element in dict_data['title']['seasons']:
        title = 'Temporada ' + str(element['number'])

        numtempo = element['number']

        if tot_temp == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.page = 0
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = numtempo, page = 0 ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist=[]

    if not item.page: item.page = 0
    perpage = 50

    url = item.url + '&seasonNumber=' + str(item.contentSeason)

    data = do_downloadpage(url)

    dict_data = jsontools.load(data)

    if 'title' not in dict_data: return itemlist

    i = 0
    avisar = True

    for element in dict_data['title']['season']['episodes']:
        titulo = '%sx%s %s' % (element['season_number'], element['episode_number'], element['name'])

        itemlist.append(item.clone( action='findvideos', title = titulo, url = url + '&episodeNumber=' + str(element['episode_number']),
                                    contentType = 'episode', contentSeason = element['season_number'], contentEpisodeNumber = element['episode_number'] ))

        i += 1
        if avisar:
            if i >= 50:
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&'), '[COLOR plum]Cargando episodios[/COLOR]')
                avisar = False

    tmdb.set_infoLabels(itemlist)

    return itemlist


def puntuar_calidad(txt):
    if txt == None: txt = '?'
    txt = txt.lower()
    orden = ['?', 'cam', 'ts-scr', 'tc-scr', 'ts-screener', 'rip', 'dvd rip', 'sd', 'hd micro', 'hd rip', 'hd-tv', 'hd real', 'hd 720', 'hd 1080', 'hd']
    if txt not in orden: return 0
    else: return orden.index(txt) + 1


def _extraer_idioma(lang):
    lang = lang.lower()
    if 'es' in lang: return 'Esp'
    if 'la' in lang: return 'Lat'
    if 'lat' in lang: return 'Lat'
    if 'en' in lang: return 'Vose'
    return 'VO'


def findvideos(item):
    logger.info()
    itemlist=[]

    data = do_downloadpage(item.url)

    dict_data = jsontools.load(data)

    if 'title' not in dict_data: return itemlist

    elementos = []

    if 'episodeNumber=' in item.url and 'season' in dict_data['title'] and 'episodes' in dict_data['title']['season']:
        for epi in dict_data['title']['season']['episodes']:
            if epi['season_number'] == item.contentSeason and epi['episode_number'] == item.contentEpisodeNumber and 'videos' in epi:
                elementos = epi['videos']
                break

    if len(elementos) == 0:
        elementos = dict_data['title']['videos']

    ses = 0

    for element in elementos:
        ses += 1

        if '/z' in element['name'] and 'clicknupload' not in element['url']: continue # descartar descargas directas (menos clicknupload)
        if 'youtube.com/' in element['url']: continue

        url = element['url']
        if url.startswith('https://goo.gl/'):
            url = httptools.downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')
            if not url: continue
        elif 'streamcrypt.net/' in url:
            url = scrapertools.decode_streamcrypt(url)
            if not url: continue

        servidor = servertools.get_server_from_url(url)
        servidor = servertools.corregir_servidor(servidor)

        url = servertools.normalize_url(servidor, url)

        if servidor and servidor != 'directo':
            itemlist.append(Item(channel = item.channel, action = 'play', title = '', server = servidor,  url = url,
                                 language = _extraer_idioma(element['language']), 
                                 quality = element['quality'], quality_num = puntuar_calidad(element['quality']) ))

    itemlist = servertools.get_servers_itemlist(itemlist)

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def sub_search(item):
    logger.info()
    itemlist = []

    url = item.url + '?type=&limit=30'

    data = do_downloadpage(url)

    dict_data = jsontools.load(data)

    if 'results' not in dict_data: return itemlist

    for element in dict_data['results']:
        if 'is_series' not in element or 'name' not in element: continue

        if element['is_series'] and item.search_type == 'movie': continue
        if not element['is_series'] and item.search_type == 'tvshow': continue

        thumb = element['poster'] if element['poster'] else item.thumbnail
        new_item = item.clone( title = element['name'], thumbnail = thumb, infoLabels = {'year':element['year'], 'plot': element['description']})

        new_item.url = host + 'secure/titles/' + str(element['id']) + '?titleId=' + str(element['id'])

        if not element['is_series']:
            new_item.action = 'findvideos'
            new_item.contentType = 'movie'
            new_item.contentTitle = element['name']
        else:
            new_item.action = 'temporadas'
            new_item.contentType = 'tvshow'
            new_item.contentSerieName = element['name']

        new_item.fmt_sufijo = '' if item.search_type != 'all' else new_item.contentType

        itemlist.append(new_item)

    tmdb.set_infoLabels(itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    try:
        if item.search_type not in ['movie', 'tvshow', 'all']: item.search_type = 'all'
        item.url = host + 'secure/search/' + texto.replace(" ", "+")
        return sub_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

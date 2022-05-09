# -*- coding: utf-8 -*-

import re

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb, jsontools, servertools


host = 'https://www.dilo.nu/'

host_catalogue = host + 'catalogue'

IDIOMAS = {'la': 'Lat', 'es': 'Esp', 'en_es': 'Vose', 'en': 'VO'}


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ... [COLOR plum](si no hay resultados)[/COLOR]', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)

def do_downloadpage(url, post=None, headers=None, follow_redirects=True, only_headers=False, raise_weberror=True):
    headers = {'Referer': host}
    timeout = 30

    # ~ resp = httptools.downloadpage(url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers, raise_weberror=raise_weberror, timeout=timeout)
    resp = httptools.downloadpage_proxy('dilo', url, post=post, headers=headers, follow_redirects=follow_redirects, only_headers=only_headers, raise_weberror=raise_weberror, timeout=timeout)

    if only_headers: return resp.headers
    return resp.data


def mainlist(item):
    return mainlist_series(item)


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item_configurar_proxies(item))

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host_catalogue ))

    itemlist.append(item.clone( title = 'Nuevos episodios', action = 'last_episodes', url = host ))

    itemlist.append(item.clone( title = 'Las de la semana', action = 'list_all', url = host_catalogue+'?sort=mosts-week' ))
    itemlist.append(item.clone( title = 'Actualizadas', action = 'list_all', url = host_catalogue+'?sort=latest' ))

    itemlist.append(item.clone( title = 'En emisión', action = 'list_all', url = host_catalogue+'?status=0' ))
    itemlist.append(item.clone( title = 'Finalizadas', action = 'list_all', url = host_catalogue+'?status=1' ))

    itemlist.append(item.clone( title = 'Películas', action = 'list_all', url = host_catalogue + '?genre[]=pelicula', group ='pelis' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios' ))
    itemlist.append(item.clone( title = 'Por país', action = 'paises' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(host_catalogue)

    patron = '<input type="checkbox" class="[^"]+" id="[^"]+" value="([^"]+)" name="genre\[\]">'
    patron += '\s*<label class="custom-control-label" for="[^"]+">([^<]+)</label>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for valor, titulo in matches:
        if titulo == 'Libros': continue
        elif titulo == 'Pelicula': continue

        itemlist.append(item.clone( title=titulo.strip(), url=host_catalogue+'?genre[]='+valor, action='list_all' ))

    if not descartar_xxx:
        itemlist.append(item.clone( action = 'list_all', title = 'xxx / adultos', url = host + 'search?s=adultos' ))
        itemlist.append(item.clone( action = 'temporadas', title = 'xxx / adultos internacional', url = host + 'internacional-adultos/' ))

    return sorted(itemlist, key=lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, 1970, -1):
        itemlist.append(item.clone( title=str(x), url=host_catalogue+'?year[]='+str(x), action='list_all' ))

    return itemlist


def paises(item):
    logger.info()
    itemlist = []

    web_paises = [
       ['AR', 'Argentina'],
       ['AU', 'Australia'],
       ['AT', 'Austria'],
       ['BE', 'B\xc3\xa9lgica'],
       ['BO', 'Bolivia'],
       ['BR', 'Brasil'],
       ['BG', 'Bulgaria'],
       ['CA', 'Canad\xc3\xa1'],
       ['CL', 'Chile'],
       ['CN', 'China'],
       ['CO', 'Colombia'],
       ['CR', 'Costa Rica'],
       ['HR', 'Croacia'],
       ['CU', 'Cuba'],
       ['CZ', 'Rep\xc3\xbablica Checa'],
       ['DK', 'Dinamarca'],
       ['EC', 'Ecuador'],
       ['SV', 'El Salvador'],
       ['FI', 'Finlandia'],
       ['FR', 'Francia'],
       ['DE', 'Alemania'],
       ['GR', 'Grecia'],
       ['GT', 'Guatemala'],
       ['HN', 'Honduras'],
       ['HK', 'Hong Kong'],
       ['HU', 'Hungr\xc3\xada'],
       ['IS', 'Islandia'],
       ['IN', 'India'],
       ['IE', 'Irlanda'],
       ['IL', 'Israel'],
       ['IT', 'Italia'],
       ['JP', 'Jap\xc3\xb3n'],
       ['LT', 'Lituania'],
       ['MY', 'Malasia'],
       ['MX', 'M\xc3\xa9xico'],
       ['NL', 'Pa\xc3\xadses Bajos'],
       ['NZ', 'Nueva Zelanda'],
       ['NO', 'Noruega'],
       ['PA', 'Panam\xc3\xa1'],
       ['PY', 'Paraguay'],
       ['PE', 'Per\xc3\xba'],
       ['PL', 'Polonia'],
       ['PT', 'Portugal'],
       ['PR', 'Puerto Rico'],
       ['RO', 'Rumania'],
       ['RU', 'Rusia'],
       ['RS', 'Serbia'],
       ['SG', 'Singapur'],
       ['ES', 'Espa\xc3\xb1a'],
       ['SE', 'Suecia'],
       ['CH', 'Suiza'],
       ['TH', 'Tailandia'],
       ['TR', 'Turqu\xc3\xada'],
       ['UA', 'Ucrania'],
       ['GB', 'Reino Unido'],
       ['US', 'Estados Unidos'],
       ['UY', 'Uruguay'],
       ['VE', 'Venezuela']
       ]

    for x in sorted(web_paises, key=lambda x: x[1]):
        itemlist.append(item.clone( title=x[1], url=host_catalogue+'?country[]='+x[0], action='list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    data = do_downloadpage(item.url)

    matches = re.compile('<div class="col-lg-2 col-md-3 col-6 mb-3">\s*<a(.*?)</a>\s*</div>', re.DOTALL).findall(data)
    for article in matches:
        url = scrapertools.find_single_match(article, ' href="([^"]+)"')
        thumb = scrapertools.find_single_match(article, ' src="([^"]+)"')
        title = scrapertools.find_single_match(article, '<div class="text-white[^"]*">([^<]+)</div>').strip()
        year = scrapertools.find_single_match(article, '<div class="txt-gray-200 txt-size-\d+">(\d+)</div>')

        if descartar_xxx and ('/coleccion-adulto-espanol/' in url or '/internacional-adultos/' in url): continue

        title_alt = ''
        if item.group == 'pelis': title_alt = title

        itemlist.append(item.clone( action='temporadas', url=url, title=title, thumbnail=thumb,
                                    contentType='tvshow', contentSerieName=title, infoLabels={'year': year}, contentTitleAlt = title_alt))

    tmdb.set_infoLabels(itemlist)

    next_page_link = scrapertools.find_single_match(data, '<li class="page-item"><a href="([^"]+)" aria-label="(?:Netx|Next)"')
    if next_page_link:
        itemlist.append(item.clone( title='Siguientes ...', url = host_catalogue + next_page_link, action='list_all',
                                    group = item.group, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    item_id = scrapertools.find_single_match(data, 'data-json=\'\{"item_id": "([^"]+)')
    url = 'https://www.dilo.nu/api/web/seasons.php'
    post = 'item_id=%s' % item_id
    data = jsontools.load(do_downloadpage(url, post=post))

    # cuantas temporadas
    tot_temp = 0

    for tempo in data:
        tot_temp += 1
        if tot_temp > 1: break

    for tempo in data:
        title = 'Temporada %s' % tempo['number']

        numtempo = tempo['number']

        if tot_temp == 1:
            if not item.group == 'pelis':
                platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')

            item.id = item_id
            item.contentType = 'season'
            item.contentSeason = numtempo
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, item_id = item_id, contentType = 'season', contentSeason = numtempo ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    color_lang = config.get_setting('list_languages_color', default='red')

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    if not item.item_id:
        data = do_downloadpage(item.url)
        item.item_id = scrapertools.find_single_match(data, 'data-json=\'\{"item_id": "([^"]+)')

    url = 'https://www.dilo.nu/api/web/episodes.php'
    post = 'item_id=%s&season_number=%s' % (item.item_id, item.contentSeason)
    data = jsontools.load(do_downloadpage(url, post=post))

    title_peli = ''
    if item.group == 'pelis':
        if len(data) == 1: title_peli = item.contentSerieName

    if item.page == 0:
        sum_parts = len(data)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('Dilo', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for epi in data[item.page * item.perpage:]:
        titulo = '%sx%s %s' % (epi['season_number'], epi['number'], epi['name'])
        plot = epi['description']
        langs = re.findall('languajes/([^.]+).png', epi['audio'])
        if langs: titulo += ' [COLOR %s][%s][/COLOR]' % (color_lang, ','.join([IDIOMAS.get(lang, lang) for lang in langs]))
        thumb = '' if 'picture' not in epi or not epi['picture'] else 'https://cdn.dilo.nu/resize/episode/220x125@' + epi['picture']

        if title_peli: titulo = title_peli

        itemlist.append(item.clone( action='findvideos', url=host+epi['permalink']+'/', title=titulo, plot=plot, thumbnail=thumb,
                                    contentType='episode', contentSeason=epi['season_number'], contentEpisodeNumber=epi['number'] ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(data) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def last_episodes(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)

    if not item.page: item.page = 0

    perpage = 25

    data = do_downloadpage(item.url)

    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    bloque = scrapertools.find_single_match(data, '>Nuevos episodios<(.*?)>Nuevas series<')
    matches = scrapertools.find_multiple_matches(bloque, '<a class="media"(.*?)</a>')

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        if descartar_xxx and ('/coleccion-adulto-espanol/' in url or '/internacional-adultos/' in url): continue

        url = scrapertools.find_single_match(match, ' href="([^"]+)"')

        title = scrapertools.find_single_match(match, ' title="([^"]+)"')
        titulo = title.replace(' Online sub español', '').strip()

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')
        name = scrapertools.find_single_match(match, ' style="max.*?">(.*?)</div>')

        temp_epis = titulo.replace(titulo, name)

        season = scrapertools.find_single_match(temp_epis, '(.*?)x')
        episode = scrapertools.find_single_match(temp_epis, '.*?x(.*?)')

        itemlist.append(item.clone( action='findvideos', url=url, title=titulo, thumbnail=thumb, contentSerieName=name,
                                   contentType='episode', contentSeason=season, contentEpisodeNumber=episode ))

        if len(itemlist) >= perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if num_matches > ((item.page + 1) * perpage):
        itemlist.append(item.clone( title="Siguientes ...", action="last_episodes", page=item.page + 1, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    patron = '<a href="#" class="[^"]*" data-link="([^"]+)".*?\?domain=([^."]+).*?/languajes/([^.]+).png'
    matches = re.compile(patron, re.DOTALL).findall(data)

    ses = 0

    for url, servidor, language in matches:
        ses += 1

        if '/download?' in url:
            server = servertools.corregir_servidor(servidor)
            if server not in ['uptobox']: continue
        else:
            server = scrapertools.find_single_match(url, '/servers/([^.]+)')
            server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = IDIOMAS.get(language, language) ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url, raise_weberror=False)

    url = scrapertools.find_single_match(data, 'iframe class="" src="([^"]+)')
    if not url: url = scrapertools.find_single_match(data, 'a href="([^"]+)" target="_blank" class="player"')

    if not url:
        action = scrapertools.find_single_match(data, ' action="([^"]+)')
        token = scrapertools.find_single_match(data, ' name="token" value="([^"]+)')
        if action and token: url = host + action + '?token=' + token

    if host in url:
        url = do_downloadpage(url, follow_redirects=False, only_headers=True).headers.get('location', '')

    if url != '': 
        itemlist.append(item.clone(url = url))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

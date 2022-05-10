# -*- coding: utf-8 -*-

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb


host = 'https://tekilaz.co/'


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

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'movies/', grupo = 'Peliculas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Más destacadas', action = 'list_all', url = host + 'category/destacadas/?type=movies',
                                grupo = 'Destacadas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Recomendadas', action = 'list_all', url = host + 'category/peliculas-recomendadas/?type=movies',
                                grupo = 'peliculas recomendadas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Películas clásicas', action = 'list_all', url = host + 'category/peliculas-clasicas/?type=movies',
                                grupo = 'Peliculas clasicas', search_type = 'movie' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'movie' ))
    itemlist.append(item.clone( title = 'Por letra (A - Z)', action = 'alfabetico', search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', grupo = 'Series', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Últimos episodios', action = 'last_episodes', url = host + 'episodes/', grupo = 'Episodios', search_type = 'tvshow' ))

    # ~ No hay ninguna serie
    # ~ itemlist.append(item.clone( title = 'Destacadas', action = 'list_all', url = host + 'category/destacadas/?type=series',grupo = 'Destacadas', search_type = 'tvshow' ))

    itemlist.append(item.clone(action = 'list_all', title = 'Series clásicas', url = host + 'category/series-clasicas/?type=series', grupo = 'Series clasicas', search_type = 'tvshow' ))

    itemlist.append(item.clone( title = 'Por género', action = 'generos', search_type = 'tvshow' ))
    itemlist.append(item.clone( title = 'Por año', action = 'anios', search_type = 'tvshow' ))

    return itemlist


def generos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, 'category menu-item-.*?<a href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        grupo = title.replace('&#038;', '&amp;').strip()

        title = title.replace('&#038;', '&').strip()

        if '/peliculas-destacadas/' in url: continue

        if item.search_type == 'movie':
            if title == 'Anime': continue

            url = url + '?type=movies'
        else:
            if title == '3D': continue
            elif title == 'Película de TV': continue

            url = url + '?type=series'

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, grupo = grupo ))

    if item.search_type == 'movie':
        itemlist.append(item.clone(action = 'list_all', title = 'Peliculas Marvel', url = host + 'category/peliculas-marvel/?type=movies', grupo = 'Peliculas Marvel'))

    return sorted(itemlist, key = lambda it: it.title)


def anios(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, '<li><a class="btn sm" href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        title = title.strip()

        if item.search_type == 'tvshow':
            if not title >= '1989': continue

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, grupo = title ))

    return sorted(itemlist, key = lambda it: it.title, reverse = True)


def alfabetico(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(host).data

    matches = scrapertools.find_multiple_matches(data, '<li><a class="btn sm blk" href="([^"]+)">(.*?)</a>')

    for url, title in matches:
        title = title.strip()
        grupo = title

        if title == '#': grupo = '0-9'

        itemlist.append(item.clone( action = 'list_all', title = title, url = url, grupo = grupo ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<h1 class="section-title">' + item.grupo + '</h1>(.*?)<nav class="navigation pagination">')

    if not bloque:
        if item.grupo == 'Peliculas':
            if not '/movies/page/' in item.url:
                grupo = 'Movies'
                bloque = scrapertools.find_single_match(data, '<h1 class="section-title">' + grupo + '</h1>(.*?)<nav class="navigation pagination">')

    if not bloque:
         bloque = scrapertools.find_single_match(data.lower(), '<h1 class="section-title">' + item.grupo.lower() + '</h1>(.*?)<nav class="navigation pagination">')

    matches = scrapertools.find_multiple_matches(bloque, '<li id="post-(.*?)</article>')

    for match in matches:
        title = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>').strip()

        thumb = scrapertools.find_single_match(match, ' src="([^"]+)"')

        data_flags = scrapertools.find_single_match(match, '<span class="lang">(.*?)</span>')
        langs = languages_flags(data_flags)

        year = scrapertools.find_single_match(match, '<span class="year">(.*?)</span>')

        if not year: year = '-'

        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        tipo = 'movie' if '/movies/' in url else 'tvshow'
        sufijo = '' if item.search_type != 'all' else tipo

        if '/movies/' in url:
            if item.search_type == 'tvshow': continue

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail=thumb, languages = ', '.join(langs), fmt_sufijo=sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))
        else:
            if item.search_type == 'movie': continue

            itemlist.append(item.clone( action ='temporadas', url = url, title = title, thumbnail = thumb, languages = ', '.join(langs), fmt_sufijo=sufijo,
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

    tmdb.set_infoLabels(itemlist)

    if '<nav class="navigation pagination">' in data:
        if '>PROXIMO<' in data:
            next_page_link = scrapertools.find_single_match(data, 'class="extend">.*?<a class="page-link" href.*?<a href="([^"]+)".*?>PROXIMO</a>')
            if not next_page_link: next_page_link = scrapertools.find_single_match(data, '<a class="page-link" href.*?<a href="([^"]+)".*?>PROXIMO</a>')

            if next_page_link != '':
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all', url = next_page_link, text_color='coral' ))

    return itemlist


def last_episodes(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    bloque = scrapertools.find_single_match(data, '<h1 class="section-title">' + item.grupo + '</h1>(.*?)<nav class="navigation pagination">')

    matches = scrapertools.find_multiple_matches(bloque, '<article(.*?)</article>')

    for match in matches:
        thumb = scrapertools.find_single_match(match, '<img src="([^"]+)"')

        if thumb.startswith('//') == True: thumb = 'https:' + thumb

        temp_epis = scrapertools.find_single_match(match, '<span class="num-epi">(.*?)</span>')

        titulo = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')
        titulo = titulo.replace(temp_epis, '').strip()

        title = titulo
        titulo = temp_epis + ' ' + titulo

        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        nro_epis = scrapertools.find_single_match(temp_epis, '.*?x(.*?)$')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                   contentType = 'episode', contentSerieName = title, contentSeason = item.contentSeason, contentEpisodeNumber = nro_epis ))

    tmdb.set_infoLabels(itemlist)

    if '<nav class="navigation pagination">' in data:
        if '>NEXT<' in data:
            next_page_link = scrapertools.find_single_match(data, '<a class="next page-numbers" href="([^"]+)".*?>NEXT</a>')

            if next_page_link != '':
                itemlist.append(item.clone( title = 'Siguientes ...', action = 'last_episodes', url = next_page_link, text_color='coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, '<li class="sel-temp"><a data-post="(.*?)" data-season="(.*?)"')

    for data_post, nro_season in matches:
        title = 'Temporada ' + nro_season

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.item_id = data_post
            item.contentType = 'season'
            item.contentSeason = nro_season
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, item_id = data_post, contentType = 'season', contentSeason = nro_season ))

    tmdb.set_infoLabels(itemlist)

    return sorted(itemlist, key=lambda it: it.contentSeason)


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    post = {'action': 'action_select_season', 'season': item.contentSeason, 'post': item.item_id}

    url = host + "wp-admin/admin-ajax.php"

    data = httptools.downloadpage(url, post = post).data

    matches = scrapertools.find_multiple_matches(data, '<article(.*?)</article>')

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('Tekilaz', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for match in matches[item.page * item.perpage:]:
        thumb = scrapertools.find_single_match(match, '<img src="([^"]+)"')

        temp_epis = scrapertools.find_single_match(match, '<span class="num-epi">(.*?)</span>')

        titulo = scrapertools.find_single_match(match, '<h2 class="entry-title">(.*?)</h2>')
        titulo = titulo.replace(temp_epis, '').strip()

        titulo = temp_epis + ' ' + titulo

        url = scrapertools.find_single_match(match, '<a href="([^"]+)"')

        nro_epis = scrapertools.find_single_match(temp_epis, '.*?x(.*?)$')

        itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = item.contentSeason, contentEpisodeNumber = nro_epis ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title="Siguientes ...", action="episodios", page = item.page + 1, perpage = item.perpage, text_color='coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    matches = scrapertools.find_multiple_matches(data, 'href="#options-(.*?)".*?OPCION.*?class="server">(.*?)</span>')
    if not matches: matches = scrapertools.find_multiple_matches(data, 'href="#options-(.*?)".*?OPTION.*?class="server">(.*?)</span>')

    ses = 0

    for option, servidor in matches:
        ses += 1

        servidor = servidor.replace(" - ", "-")

        language = scrapertools.find_single_match(servidor, '-(.*)').strip()
        if language == 'Subtitulado': language = 'Vose'
        elif language == 'Latino': language = 'Lat'
        elif language == 'Español': language = 'Esp'

        servidor = scrapertools.find_single_match(servidor, '(.*)-').strip()

        if servidor:
           servidor = servidor.lower()

           servidor = normalize_other(servidor)
           if not servidor: continue

           play_other = ''

           if servidor == 'drive': servidor ='gvideo'
           elif servidor == 'player' or servidor == 'embed':
              play_other = servidor
              servidor = ''

           url = scrapertools.find_single_match(data, '<div id="options-' + option + '.*?src="([^"]+)"')

           url = url.replace('&#038;', '&')

           itemlist.append(Item( channel = item.channel, action = 'play', server = servidor, title = '', url = url, language = language,
                                 referer = item.url, other = play_other.capitalize() ))

    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def normalize_other(link_other):
    link_other = servertools.corregir_servidor(link_other)

    if link_other == 'netutv': link_other = ''
    elif link_other == 'powvideo': link_other = ''
    elif link_other == 'streamplay': link_other = ''
    elif link_other == 'uploadedto': link_other = ''

    elif link_other == 'jetload': link_other = ''
    elif link_other == 'vidcloud': link_other = ''
    elif link_other == 'openload': link_other = ''
    elif link_other == 'clicknupload': link_other = ''
    elif link_other == 'onlystream': link_other = ''
    elif link_other == 'rapidvideo': link_other = ''
    elif link_other == 'rapidvid': link_other = ''
    elif link_other == 'streamango': link_other = ''
    elif link_other == 'streamcherry': link_other = ''
    elif link_other == 'streamcloud': link_other = ''
    elif link_other == 'streamix': link_other = ''
    elif link_other == 'thevideo': link_other = ''
    elif link_other == 'thevid': link_other = ''
    elif link_other == 'uploadmp4': link_other = ''
    elif link_other == 'verystream': link_other = ''
    elif link_other == 'vidcloud': link_other = ''

    return link_other


def play(item):
    logger.info()
    itemlist = []

    url = item.url
    servidor = item.server

    url_final = ''

    host_player = host.replace('https://', 'https://fs.')

    if item.other.lower() == 'player':
       try:
           headers = {'Referer': item.referer}
           url_player = httptools.downloadpage(url, headers = headers, only_headers = True, follow_redirects = False).headers.get('location')
           url_final = url_player + '&ver=si'
       except:
           url_final = ''

    if url_final == '':
        data = httptools.downloadpage(url).data

        value_php = scrapertools.find_single_match(data, '<input type="hidden" name="data" value="([^"]+)"')

        if '/index.php?' in data:
            index_php = scrapertools.find_single_match(data, '/index.php.*?h=(.*?)"')

            post = {'h': index_php}

            url_final = httptools.downloadpage(host_player + 'r.php', post = post).url

            if not url_final:
                data_post = httptools.downloadpage(host_player + 'api.php', post = post).data

                url_final = scrapertools.find_single_match(str(data_post), '.*?":"(.*?)"')
                url_final = url_final.replace('\/', '/')

            if url_final: value_php = ''

        if value_php:
            post = {'data': value_php}

            url_final = httptools.downloadpage(host + 'r.php', post = post).url

            if '/index.php?' in url_final:
                index_php = url_final.replace( host_player + 'index.php?h=', '')

                post = {'h': index_php}

                url_final = httptools.downloadpage(host_player + 'r.php', post = post).url

                if not url_final:
                    data_post = httptools.downloadpage(host_player + 'api.php', post = post).data

                    url_final = scrapertools.find_single_match(str(data_post), '.*?":"(.*?)"')
                    url_final = url_final.replace('\/', '/')

    if url_final:
        if item.server == 'openplay':
            url_final = url_final.replace('/openplay.openplay.vip/player.php?data=', '/player.openplay.vip/player.php?id=')
        elif item.other.lower() == 'player':
            servidor, url_final = get_link_player(servidor, url_final)
        elif item.other.lower() == 'embed':
            if '.mystream.' in url_final: servidor = 'mystream'

        url = url_final

    if url:
        itemlist.append(item.clone(server = servidor, url = url))

    return itemlist


def get_link_player(servidor, url_final):
    referer = url_final.split('//', 1)

    data = httptools.downloadpage(url_final, headers = {'referer': referer[0] + '//' + referer[1]}).data

    url, type = scrapertools.find_single_match(data, '"file": "([^"]+)",\s+"type": "([^"]+)"')

    if type == 'mp4':
        headers = {'referer': url_final}
        url = httptools.downloadpage(url, headers = headers, only_headers=True, follow_redirects = False).headers.get("location", url)

        url_player = "%s|Referer=%s&User-Agent=%s" % (url, url_final, httptools.get_user_agent())
        servidor = 'directo'

    elif type == 'hls':
        url_player = url
        servidor = 'm3u8hls'

    else:
        url_player = url_final

    return servidor, url_player


def languages_flags(data_flags):
    logger.info()

    IDIOMAS = {'usa': 'Vose', 'espana': 'Esp', 'mexico': 'Lat', 'mx': 'Lat', 'dk': 'Latino', 'es': 'Esp', 'en': 'Eng', 'gb': 'Vo', 'de': 'De'}

    languages = []

    list_langs = scrapertools.find_multiple_matches(data_flags, '/flag-(.*?).jpg"?')

    for lang in list_langs:
        lang = IDIOMAS[lang]
        if lang not in languages: 
            if not languages: languages.append(lang)
            else: languages.append(' ' + lang)

    return languages


def search(item, texto):
    logger.info()
    try:
        item.grupo = texto.strip()
        item.url = host + '?s=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


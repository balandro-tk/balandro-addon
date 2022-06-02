# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3: PY3 = False
else: PY3 = True


import os, re, xbmcgui

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, servertools, tmdb, jsontools


host = 'https://playdede.nu/'


elepage = 40

perpage = 20


# ~ 31/5/2022 Solo funciona TODO en k19 el resto da error bad gateway

notification_d_ok = config.get_setting('notification_d_ok', default=True)

color_adver = config.get_setting('notification_adver_color', default='violet')


class login_dialog(xbmcgui.WindowDialog):
    def __init__(self):
        avis = True
        if config.get_setting('playdede_username', 'playdede', default=False): 
            if config.get_setting('playdede_password', 'playdede', default=False):
                if config.get_setting('playdede_login', 'playdede', default=False): avis = False

        if avis:
            self.login_result = False
            platformtools.dialog_ok("Recomendación Balandro - PlayDede", '[COLOR yellow]Sugerimos crear una nueva cuenta para registrarse en la web, no deberiais indicar ninguna de vuestras cuentas personales.[/COLOR]', 'Para más detalles al respecto, acceda a la Ayuda, apartado Canales, Información dominios que requieren registrarse.')

        self.background = xbmcgui.ControlImage(250, 150, 800, 355, filename=config.get_thumb('ContentPanel'))
        self.addControl(self.background)
        self.icon = xbmcgui.ControlImage(265, 220, 225, 225, filename=config.get_thumb('playdede', 'thumb', 'channels'))
        self.addControl(self.icon)
        self.username = xbmcgui.ControlEdit(530, 320, 400, 120, 'Indicar su usuario: ', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))
        self.addControl(self.username)
        if platformtools.get_kodi_version()[1] >= 18:
            self.password = xbmcgui.ControlEdit(530, 320, 400, 120, 'Indicar la contraseña: ', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))
        else:
            self.password = xbmcgui.ControlEdit(530, 320, 400, 120, 'Indicar la contraseña: ', font='font13', textColor='0xDD171717', focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'), isPassword=True)

        self.buttonOk = xbmcgui.ControlButton(588, 460, 125, 25, 'Confirmar', alignment=6, focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))
        self.buttonCancel = xbmcgui.ControlButton(720, 460, 125, 25, 'Cancelar', alignment=6, focusTexture=config.get_thumb('button-focus'), noFocusTexture=config.get_thumb('black-back2'))
        self.addControl(self.password)
        self.password.setVisible(True)
        self.password.controlUp(self.username)
        self.addControl(self.buttonOk)
        self.password.controlDown(self.buttonOk)
        self.username.setLabel('Indicar su usuario: ')
        if int(platformtools.get_kodi_version()[1]) >= 18: self.password.setType(xbmcgui.INPUT_TYPE_PASSWORD, 'Indicar la contraseña: ')

        self.password.setLabel('Indicar la contraseña: ')
        self.setFocus(self.username)
        self.username.controlUp(self.buttonOk)
        self.username.controlDown(self.password)
        self.buttonOk.controlUp(self.password)
        self.buttonOk.controlDown(self.username)
        self.buttonOk.controlRight(self.buttonCancel)
        self.buttonOk.controlLeft(self.buttonCancel)
        self.addControl(self.buttonCancel)
        self.buttonCancel.controlRight(self.buttonOk)
        self.buttonCancel.controlLeft(self.buttonOk)
        self.username.setPosition(500, 210)
        self.username.setWidth(500)
        self.username.setHeight(50)
        self.password.setPosition(500, 300)
        self.password.setWidth(500)
        self.password.setHeight(50)

        self.doModal()

        if self.username.getText() and self.password.getText():
            config.set_setting('playdede_username', self.username.getText(), 'playdede')
            config.set_setting('playdede_password', self.password.getText(), 'playdede')
            config.set_setting('playdede_login', True, 'playdede')
            self.login_result = True

    def onControl(self, control):
        control = control.getId()
        if control in range(3000, 30010): self.close()


def do_make_login_logout(url, post=None, headers=None):
    add_referer = True
    if '/user/' in url: add_referer = False

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, add_referer=add_referer, raise_weberror=False).data
    data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, add_referer=add_referer, raise_weberror=False).data

    if not PY3:
        if '<title>Please Wait... | Cloudflare</title>' in data:
            if notification_d_ok:
                platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Probable incompatibilidad con la versión de su Media Center.[/COLOR]', 'El canal no da respuesta adecuada.')
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Posible MediaCenter Incompatibile[/COLOR][/B]' % color_adver)

    return data


def login(item):
    logger.info()

    status = config.get_setting('playdede_login', 'playdede', default=False)

    username = config.get_setting('playdede_username', 'playdede', default='')
    password = config.get_setting('playdede_password', 'playdede', default='')

    if not username or not password:
        login = login_dialog()
        if not login.login_result: return False

        if not item:
            platformtools.dialog_notification(config.__addon_name, '[COLOR yellow]PlayDede Credenciales guardadas[/COLOR]')
            return False

    username = config.get_setting('playdede_username', 'playdede', default='')
    password = config.get_setting('playdede_password', 'playdede', default='')

    try:
       data = do_make_login_logout(host)

       user = scrapertools.find_single_match(data, username).strip()

       if user:
           if username:
               if username in user:
                   if not status: config.set_setting('playdede_login', True, 'playdede')

                   platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Login correcto[/COLOR]')

                   platformtools.itemlist_refresh()
                   return True

       if 'UserOn' in data:
           if not status:
               config.set_setting('playdede_login', True, 'playdede')
               platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Login correcto[/COLOR]')

           platformtools.itemlist_refresh()
           return True
    except:
       platformtools.dialog_notification(config.__addon_name, '[COLOR red]PlayDede Sin acceso Web[/COLOR]')
       return False

    post = {'user': username, 'pass': password, '_method': 'auth/login'}

    try:
       data = do_make_login_logout(host + 'ajax.php', post=post)

       jdata = jsontools.load(data)

       if not jdata['alert']:
           platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Login correcto[/COLOR]')
           config.set_setting('playdede_login', True, 'playdede')

           platformtools.itemlist_refresh()
           return True
       elif jdata['reload']:
           platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Login correcto[/COLOR]')
           config.set_setting('playdede_login', True, 'playdede')

           platformtools.itemlist_refresh()
           return True
       else:
           platformtools.dialog_notification(config.__addon_name, '[COLOR red]PlayDede Login incorrecto[/COLOR]')
           return False
    except:
       platformtools.dialog_notification(config.__addon_name, '[COLOR red]PlayDede Sin acceso Login[/COLOR]')
       return False

    if not httptools.get_cookie(host, 'MoviesWebsite'): do_make_login_logout(host)

    if httptools.get_cookie(host, 'utoken'):
        platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Login correcto[/COLOR]')
        config.set_setting('playdede_login', True, 'playdede')

        platformtools.itemlist_refresh()
        return True

    try:
       data = do_make_login_logout(host + 'ajax.php', post=post)
    except:
       platformtools.dialog_notification(config.__addon_name, '[COLOR red]PlayDede Sin acceso al Login[/COLOR]')
       return False

    if httptools.get_cookie(host, 'utoken'):
        platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Login correcto[/COLOR]')
        config.set_setting('playdede_login', True, 'playdede')

        platformtools.itemlist_refresh()
        return True

    platformtools.dialog_notification(config.__addon_name, '[COLOR red]PlayDede Login incorrecto[/COLOR]')
    return False


def logout(item):
    logger.info()

    username = config.get_setting('playdede_username', 'playdede', default='')

    if username:
        data = do_make_login_logout(host + 'user/' + username + '/salir/')

        config.set_setting('playdede_login', False, 'playdede')
        platformtools.dialog_notification(config.__addon_name, '[COLOR chartreuse]PlayDede Sesión cerrada[/COLOR]')

        platformtools.itemlist_refresh()
        return True

    platformtools.dialog_notification(config.__addon_name, '[COLOR red]PlayDede Sin cerrar Sesión[/COLOR]')
    return False


def item_configurar_proxies(item):
    plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
    plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'
    return item.clone( title = 'Configurar proxies a usar ...', action = 'configurar_proxies', folder=False, plot=plot, text_color='red' )

def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, post=None, referer=None):
    # ~ por si viene de enlaces guardados posteriores
    if url.startswith('/'): url = host + url[1:] # ~ solo v. 2.0.0

    ant_hosts = ['https://playdede.com/']

    for ant in ant_hosts:
        url = url.replace(ant, host)


    headers = {}

    if referer: headers = {'Referer': referer}
    else: headers = {'Referer': host}

    timeout = None
    if '?genre=' in url: timeout = 50

    # ~ data = httptools.downloadpage(url, post=post, headers=headers, raise_weberror=False).data
    data = httptools.downloadpage_proxy('playdede', url, post=post, headers=headers, raise_weberror=False, timeout=timeout).data

    if "data-showform='login'" in data:
        if not config.get_setting('playdede_login', 'playdede', default=False):
            platformtools.dialog_notification(config.__addon_name, '[COLOR yellow][B]PlayDede Debe iniciar Sesión[/B][/COLOR]')

        result = login('')
        if result == True: return do_downloadpage(url, post=post, referer=referer)

    if not PY3:
        if '<title>Please Wait... | Cloudflare</title>' in data:
            if notification_d_ok:
                platformtools.dialog_ok(config.__addon_name, '[COLOR yellow]Probable incompatibilidad con la versión de su Media Center.[/COLOR]', 'El canal no da respuesta adecuada.')
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Posible MediaCenter Incompatibile[/COLOR][/B]' % color_adver)

    return data


def acciones(item):
    logger.info()
    itemlist = []

    username = config.get_setting('playdede_username', 'playdede', default='')

    if username:
        itemlist.append(item_configurar_proxies(item))

    if not config.get_setting('playdede_login', 'playdede', default=False):
        if username:
            itemlist.append(item.clone( title = '[COLOR chartreuse]Iniciar sesión[/COLOR]', action = 'login' ))
        else:
            itemlist.append(item.clone( title = '[COLOR crimson][B]Credenciales cuenta[/B][/COLOR]', action = 'login' ))

            itemlist.append(Item( channel='helper', action='show_help_register', title='[B]Información para registrarse[/B]', thumbnail=config.get_thumb('help'), text_color='green' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = '[COLOR chartreuse]Cerrar sesión[/COLOR]', action = 'logout' ))

    platformtools.itemlist_refresh()

    return itemlist


def mainlist(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = 'Listas populares', action = 'list_listas', search_type = 'all', text_color = 'cyan' ))

        itemlist.append(item.clone( title = 'Buscar ...', action = 'search', search_type = 'all', text_color = 'yellow' ))

        itemlist.append(item.clone( title = 'Películas', action = 'mainlist_pelis', text_color = 'deepskyblue' ))
        itemlist.append(item.clone( title = 'Series', action = 'mainlist_series', text_color = 'hotpink' ))
        itemlist.append(item.clone( title = 'Animes', action = 'mainlist_animes', text_color = 'springgreen' ))

    return itemlist


def mainlist_pelis(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = 'Listas populares', action = 'list_listas', search_type = 'all', text_color = 'cyan' ))

        itemlist.append(item.clone( title = 'Buscar película ...', action = 'search', search_type = 'movie', text_color = 'deepskyblue' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'peliculas/', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host, _type = 'movies', nro_pagina = 1, search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'peliculas?orderBy=item_date', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))
        itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'peliculas?orderBy=score', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', slug = 'peliculas', nro_pagina = 1, search_type = 'movie' ))

    return itemlist


def mainlist_series(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = 'Listas populares', action = 'list_listas', search_type = 'all', text_color = 'cyan' ))

        itemlist.append(item.clone( title = 'Buscar serie ...', action = 'search', search_type = 'tvshow', text_color = 'hotpink' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'series/', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Nuevos episodios', action = 'list_last', url = host, _type = 'episodes', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Últimas', action = 'list_last', url = host, _type = 'series', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'series?orderBy=last_update', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Más valoradas', action = 'list_all', url = host + 'series?orderBy=score', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por plataforma', action= 'plataformas', slug = 'series', nro_pagina = 1, search_type='tvshow'))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', slug = 'series', nro_pagina = 1, search_type = 'tvshow' ))

    return itemlist


def mainlist_animes(item):
    logger.info()
    itemlist = []

    titulo = '[B]Acciones[/B]'
    if config.get_setting('playdede_login', 'playdede', default=False): titulo += ' [COLOR plum](si no hay resultados)[/COLOR]'

    itemlist.append(item.clone( action='acciones', title=titulo, text_color='goldenrod' ))

    if config.get_setting('playdede_login', 'playdede', default=False):
        itemlist.append(item.clone( title = 'Listas populares', action = 'list_listas', search_type = 'all', text_color = 'cyan' ))

        itemlist.append(item.clone( title = 'Buscar anime ...', action = 'search', search_type = 'tvshow', text_color = 'springgreen' ))

        itemlist.append(item.clone( title = 'Catálogo', action = 'list_all', url = host + 'animes/', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Novedades', action = 'list_all', url = host + 'animes?orderBy=last_update', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Más valorados', action = 'list_all', url = host + 'animes?orderBy=score', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

        itemlist.append(item.clone( title = 'Por género', action = 'generos', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))
        itemlist.append(item.clone( title = 'Por año', action = 'anios', group = 'anime', slug = 'animes', nro_pagina = 1, search_type = 'tvshow' ))

    return itemlist


def plataformas(item):
    logger.info()
    itemlist = []

    url = url = host + 'series/'

    data = do_downloadpage(url)
    data = re.sub('\\n|\\r|\\t|\\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="cfilter single-network.*?data-value="(.*?)".*?<img src="(.*?)"').findall(data)

    for id_network, thumb in matches:
        title = scrapertools.find_single_match(thumb, '/network/(.*?).png')
        title = title.capitalize()

        itemlist.append(item.clone(title = title, action = 'list_plataforma', thumbnail = thumb, url = url, id_network = id_network))

    return sorted(itemlist, key=(lambda x: x.title))


def list_plataforma(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub('\\n|\\r|\\t|\\s{2}|&nbsp;', '', data)

    matches = re.compile('<a href="([^"]+)"><i class[^<]+</i>([^<]+)').findall(data)

    for url, title in matches:
        title = title.capitalize()

        url = url.replace('?orderBy=last_update', '?network=' + item.id_network + '&orderBy=last_update')
        url = url.replace('?orderBy=score', '?network=' + item.id_network + '&orderBy=score')

        if '=score' in url: order = 'score'
        else: order = 'last_update'

        itemlist.append(item.clone(title = title, action = 'list_network', url = url, slug = 'series', order = order ))

    return sorted(itemlist, key=(lambda x: x.title))


def generos(item):
    logger.info()
    itemlist = []

    if item.group == 'anime': url_generos = host + 'animes/'
    else:
        if item.search_type == 'movie': url_generos = host + 'peliculas/'
        else: url_generos = host + 'series/'

    data = do_downloadpage(url_generos)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<li class="cfilter.*?data-type="genre".*?data-value="(.*?)">.*?<b>(.*?)</b>').findall(data)

    for genre, title in matches:
        genre = '?genre=' + genre

        itemlist.append(item.clone( title = title, action = 'list_all', genre = genre ))

    if item.search_type == 'movie':
        itemlist.append(item.clone( title = 'Aventura', action = 'list_all', genre = '?genre=aventura' ))
        itemlist.append(item.clone( title = 'Fantasía', action = 'list_all', genre = '?genre=fantasia' ))
        itemlist.append(item.clone( title = 'Historia', action = 'list_all', genre = '?genre=historia' ))

    if not item.group == 'anime':
        itemlist.append(item.clone( title = 'Documental', action = 'list_all', genre = '?genre=documental' ))

    return sorted(itemlist,key=lambda x: x.title)


def anios(item):
    logger.info()
    itemlist = []

    if item.search_type == 'movie': tope_year = 1934
    else: tope_year = 1969

    from datetime import datetime
    current_year = int(datetime.today().year)

    for x in range(current_year, tope_year, -1):
        year = '?year=' + str(x)

        itemlist.append(item.clone( title = str(x), year = year, action = 'list_all' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    # ~ Si venimos del menu pral. Grupos o Generos
    if not item.slug:
       if item.search_type == 'movie': item.slug = 'peliculas'
       elif item.search_type == 'tvshow': item.slug = 'series'

       if not item.genre:
          genre = scrapertools.find_single_match(item.url, '/?genre=(.*?)&')
          if genre: item.genre = '?genre=' + genre

       if not item.nro_pagina: item.nro_pagina = 1

    if not item.post: post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug}
    else: post = item.post

    data = do_downloadpage(host + 'ajax.php' + item.genre + item.year, post=post)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('\\/', '/')

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        match = match.replace('=\\', '=').replace('\\"', '/"')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        title = clean_title(title, url)

        if 'Tu directorio de' in title: continue

        id = scrapertools.find_single_match(match, 'data-id="(.*?)"')

        thumb = scrapertools.find_single_match(match, '<img src=(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if not year: year = '-'

        if '/pelicula/' in url:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))
        else:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_all', text_color = 'coral' ))
            buscar_next = False

    if num_matches < elepage: buscar_next = False

    if buscar_next:
        if itemlist:
             item.nro_pagina = item.nro_pagina + 1

             post = {'_method': 'items', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': item.slug}

             itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_all',
                                         nro_pagina = item.nro_pagina, post = post, page = 0, text_color = 'coral' ))

    return itemlist


def list_last(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if not item.post: post = {'_method': 'items', 'type': item._type, 'async': 'true', 'page': item.nro_pagina, 'ajaxName': 'main', 'slug': ''}
    else: post = item.post

    data = do_downloadpage(host + 'ajax.php', post=post)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('\\/', '/')

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        match = match.replace('=\\', '=').replace('\\"', '/"')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if item._type == 'episodes': title = scrapertools.find_single_match(match, 'alt="(.*?)"')

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        title = clean_title(title, url)

        if 'Tu directorio de' in title: continue

        id = scrapertools.find_single_match(match, 'data-id="(.*?)"')

        thumb = scrapertools.find_single_match(match, '<img src=(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if not year: year = '-'

        if '/pelicula/' in url:
            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                        contentType = 'movie', contentTitle = title, infoLabels={'year': year} ))

        elif '/serie/' in url:
            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels={'year': year} ))

        else:
            titulo = scrapertools.find_single_match(match, '<a href="(.*?)"')

            titulo = titulo.replace('/episodios/', '').replace('_1', '').replace('_', ' ').replace('-', ' ').strip()
            titulo = titulo.replace('//', '')

            titulo = titulo.capitalize()

            thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')
            thumb = thumb.replace('http:', 'https:')

            season = scrapertools.find_single_match(match, '<span>(.*?)-').strip()
            epis = scrapertools.find_single_match(match, '<span>.*?-(.*?)</span>').strip()

            itemlist.append(item.clone( action = 'findvideos', url = url, title = titulo, thumbnail = thumb,
                                        contentSerieName = titulo, contentType = 'episode', contentSeason = season, contentEpisodeNumber = epis ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_last', text_color = 'coral' ))

    return itemlist


def list_listas(item):
    logger.info()
    itemlist = []

    if not item.url: url = host + 'listas/'
    else: url = item.url

    data = do_downloadpage(url)
    data = re.sub('\\n|\\r|\\t|\\s{2}|&nbsp;', '', data)

    matches = re.compile('<article>.*?<a href="([^"]+)"[^<]+<h2>([^<]+)</h2>').findall(data)

    for url, title in matches:
        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        itemlist.append(item.clone( action = 'list_search', title = title, url = url ))

    if itemlist:
        if '<div class="pagPlaydede">' in data:
            if 'Pagina Anterior' in data: patron = '<div class="pagPlaydede">.*?Pagina Anterior.*?<a href="([^"]+)'
            else: patron = '<div class="pagPlaydede"><a href="([^"]+)'

            next_url = scrapertools.find_single_match(data, patron)
            if next_url:
                itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_listas', text_color = 'coral' ))

    return itemlist


def list_network(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    if not item.post:
        post = {'_method': 'items', 'page': item.nro_pagina, 'networks': item.id_network, 'ajaxName': 'main', 'slug': item.slug, 'orderBy=': item.order}
    else:
        post = item.post

    url_post = item.url.replace('/series', '/ajax.php')

    data = do_downloadpage(url_post, post=post, referer=item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = data.replace('\\/', '/')

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        match = match.replace('=\\', '=').replace('\\"', '/"')

        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        if 'Tu directorio de' in title: continue

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        title = clean_title(title, url)

        id = scrapertools.find_single_match(match, 'data-id="(.*?)"')

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        if not year: year = '-'

        itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, 
                                    contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_network', text_color = 'coral' ))
            buscar_next = False

    if num_matches < elepage: buscar_next = False

    if buscar_next:
        if itemlist:
             item.nro_pagina = item.nro_pagina + 1

             post = {'_method': 'items', 'page': item.nro_pagina, 'networks': item.id_network, 'ajaxName': 'main', 'slug': item.slug, 'orderBy=': item.order}

             itemlist.append(item.clone( title = 'Siguientes ...', action = 'list_network', url = item.url,
                                         nro_pagina = item.nro_pagina, post = post, page = 0, text_color = 'coral' ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)

    matches = re.compile("<div class='clickSeason(?: clickAc| )' data-season='(\d+)'", re.DOTALL).findall(data)

    if len(matches) > 25:
        platformtools.dialog_notification('PlayDede', '[COLOR blue]Cargando Temporadas[/COLOR]')

    for tempo in matches:
        title = 'Temporada ' + tempo

        if len(matches) == 1:
            platformtools.dialog_notification(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), 'solo [COLOR tan]' + title + '[/COLOR]')
            item.contentType = 'season'
            item.contentSeason = int(tempo)
            itemlist = episodios(item)
            return itemlist

        itemlist.append(item.clone( action = 'episodios', title = title, contentType = 'season', contentSeason = int(tempo) ))

    tmdb.set_infoLabels(itemlist)

    return itemlist


def episodios(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0
    if not item.perpage: item.perpage = 50

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    data = scrapertools.find_single_match(data, "<div class='se-c' data-season='%d'(.*?)<\/div><\/div>" % (item.contentSeason))

    patron = '<a href="([^"]+)"><div class="imagen">'
    patron += '<img src="([^"]+)"><\/div>.*?<div class="epst">([^<]+)'
    patron += '<\/div><div class="numerando">([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.page == 0:
        sum_parts = len(matches)
        if sum_parts > 250:
            if platformtools.dialog_yesno(item.contentSerieName.replace('&#038;', '&').replace('&#8217;', "'"), '¿ Hay [COLOR yellow][B]' + str(sum_parts) + '[/B][/COLOR] elementos disponibles, desea cargarlos en bloques de [COLOR cyan][B]250[/B][/COLOR] elementos?'):
                platformtools.dialog_notification('PlayDede', '[COLOR cyan]Cargando elementos[/COLOR]')
                item.perpage = 250

    for url, thumb, titulo, name in matches[item.page * item.perpage:]:
        s_e = scrapertools.get_season_and_episode(name)
        season = int(s_e.split("x")[0])
        episode = s_e.split("x")[1]

        title = str(season) + 'x' + str(episode) + ' ' + titulo

        itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb,
                                    contentType = 'episode', contentSeason = season, contentEpisodeNumber = episode ))

        if len(itemlist) >= item.perpage:
            break

    tmdb.set_infoLabels(itemlist)

    if itemlist:
        if len(matches) > ((item.page + 1) * item.perpage):
            itemlist.append(item.clone( title = "Siguientes ...", action = "episodios", page = item.page + 1, perpage = item.perpage, text_color = 'coral' ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    # ~ Reproductor
    patron = '<div class="playerItem.*?data-lang="(.*?)" data-loadPlayer="(.*?)".*?<h3>(.*?)</h3>.*?">Calidad:.*?">(.*?)</span>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    ses = 0

    for lang, sid, server, qlty in matches:
        ses += 1

        if not server or not sid: continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()
        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', id = sid, language = lang, quality = qlty ))

    # ~ Enlaces
    bloque = scrapertools.find_single_match(data, '<div class="linkSorter">(.*?)<div class="contEP contepID_3">')

    matches = re.compile('data-quality="(.*?)" data-lang="(.*?)".*?href="(.*?)".*?<span>.*?">(.*?)</b>', re.DOTALL).findall(bloque)

    for qlty, lang, url, server in matches:
        ses += 1

        if not url or not server: continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()
        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = lang, quality = qlty, other = 'E' ))

    # ~ Descargas
    bloque = scrapertools.find_single_match(data, '<div class="contEP contepID_3">(.*?)$')

    matches = re.compile('data-quality="(.*?)" data-lang="(.*?)".*?href="(.*?)".*?<span>.*?">(.*?)</b>', re.DOTALL).findall(bloque)

    for qlty, lang, url, server in matches:
        ses += 1

        if not url or not server: continue

        if '/ul.' in url: continue
        elif '/1fichier.' in url: continue
        elif '/ddownload.' in url: continue

        if 'https://netload.cc/st?' in url:
             url = scrapertools.find_single_match(url, '&url=(.*?)$')
             if not url: continue

        if lang.lower() == 'espsub': lang = 'Vose'

        lang = lang.capitalize()

        server = servertools.corregir_servidor(server)

        itemlist.append(Item( channel = item.channel, action = 'play', server = server, title = '', url = url, language = lang, quality = qlty, other = 'D' ))


    if not itemlist:
        if not ses == 0:
            platformtools.dialog_notification(config.__addon_name, '[COLOR tan][B]Sin enlaces Soportados[/B][/COLOR]')
            return

    return itemlist


def play(item):
    logger.info()
    itemlist = []

    url_play = ''

    if item.id:
        post = {'_method': 'getPlayer', 'id': item.id}
        data = do_downloadpage(host + 'ajax.php', post=post)

        url = scrapertools.find_single_match(data, r"src='([^']+)")
        url = url.replace('\\/', '/')

        if url:
            data = do_downloadpage(url)
            url_play = scrapertools.find_single_match(data, r"src='([^']+)")
    else:
        url_play = item.url

    if url_play:
        itemlist.append(item.clone(url = url_play.replace("\\/", "/")))

    return itemlist


def clean_title(title, url):
    logger.info()

    title = title.replace('\\u00e1', 'a').replace('\\u00c1', 'a').replace('\\u00e9', 'e').replace('\\u00ed', 'i').replace('\\u00f3', 'o').replace('\\u00fa', 'u')
    title = title.replace('\\u00f1', 'ñ').replace('\\u00bf', '¿').replace('\\u00a1', '¡').replace('\\u00ba', 'º')
    title = title.replace('\\u00eda', 'a').replace('\\u00f3n', 'o').replace('\\u00fal', 'u')

    if '\\u' in title:
        data = do_downloadpage(url)
        data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

        titulo = scrapertools.find_single_match(data, "<title>(.*?)</title>")
        titulo = titulo.replace('Ver película:', '').replace('Ver serie:', '').replace('Ver anime:', '').strip()

        if titulo: title = titulo

    return title


def list_search(item):
    logger.info()
    itemlist = []

    if not item.page: item.page = 0

    data = do_downloadpage(item.url)
    data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)

    matches = re.compile('<article(.*?)</article>').findall(data)

    num_matches = len(matches)

    for match in matches[item.page * perpage:]:
        url = scrapertools.find_single_match(match, '<a href="(.*?)"')
        title = scrapertools.find_single_match(match, '<h3>(.*?)</h3>')

        if not url or not title: continue

        if url.startswith('/'): url = host[:-1] + url
        elif not url.startswith('http'): url = host + url

        if not item.search_type == "all":
            if item.search_type == "movie":
                if '/serie/' in url: continue
            else:
                if '/pelicula/' in url: continue

        thumb = scrapertools.find_single_match(match, '<img src="(.*?)"')

        year = scrapertools.find_single_match(match, '<p>, (\d+)</p>')
        if not year: year = '-'

        if '/pelicula/' in url:
            sufijo = '' if item.search_type != 'all' else 'movie'

            itemlist.append(item.clone( action = 'findvideos', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo,
                                        contentType = 'movie', contentTitle = title, infoLabels = {'year': year} ))
        else:
            sufijo = '' if item.search_type != 'all' else 'tvshow'

            itemlist.append(item.clone( action = 'temporadas', url = url, title = title, thumbnail = thumb, fmt_sufijo = sufijo, 
                                        contentType = 'tvshow', contentSerieName = title, infoLabels = {'year': year} ))

        if len(itemlist) >= perpage: break

    tmdb.set_infoLabels(itemlist)

    buscar_next = True
    if num_matches > perpage:
        hasta = (item.page * perpage) + perpage
        if hasta < num_matches:
            itemlist.append(item.clone( title = 'Siguientes ...', page = item.page + 1, action = 'list_search', text_color = 'coral' ))
            buscar_next = False

    if buscar_next:
        if itemlist:
            if '<div class="pagPlaydede">' in data:
                if 'Pagina Anterior' in data: patron = '<div class="pagPlaydede">.*?Pagina Anterior.*?<a href="([^"]+)'
                else: patron = '<div class="pagPlaydede"><a href="([^"]+)'

                next_url = scrapertools.find_single_match(data, patron)
                if next_url:
                    itemlist.append(item.clone( title = 'Siguientes ...', url = next_url, action = 'list_search', page = 0, text_color = 'coral' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        item.url = host + 'search/?s=' + texto.replace(" ", "+")
        return list_search(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


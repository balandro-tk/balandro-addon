# -*- coding: utf-8 -*-

import os

from platformcode import logger, config, platformtools
from core.item import Item

from datetime import datetime

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')

cfg_search_excluded_movies = 'search_excludes_movies'
cfg_search_excluded_tvshows = 'search_excludes_tvshows'
cfg_search_excluded_documentaries = 'search_excludes_documentaries'
cfg_search_excluded_torrents = 'search_excludes_torrents'
cfg_search_excluded_mixed = 'search_excludes_mixed'
cfg_search_excluded_all = 'search_excludes_all'

channels_search_excluded_movies = config.get_setting(cfg_search_excluded_movies, default='')
channels_search_excluded_tvshows = config.get_setting(cfg_search_excluded_tvshows, default='')
channels_search_excluded_documentaries = config.get_setting(cfg_search_excluded_documentaries, default='')
channels_search_excluded_torrents = config.get_setting(cfg_search_excluded_torrents, default='')
channels_search_excluded_mixed = config.get_setting(cfg_search_excluded_mixed, default='')
channels_search_excluded_all = config.get_setting(cfg_search_excluded_all, default='')

current_year = int(datetime.today().year)
current_month = int(datetime.today().month)


def submnu_developer(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='[B]Tests Webs Canales:[/B]', thumbnail=config.get_thumb('tools'), text_color='gold' ))
    itemlist.append(item.clone( action='test_all_webs', title=' - Todos', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='test_all_webs', title=' - Insatisfactorios', thumbnail=config.get_thumb('stack'), unsatisfactory = True ))

    itemlist.append(item.clone( action='', title='[B]Tests Webs Servidores:[/B]', thumbnail=config.get_thumb('tools'), text_color='fuchsia' ))
    itemlist.append(item.clone( action='test_all_srvs', title=' - Todos', thumbnail=config.get_thumb('flame') ))
    itemlist.append(item.clone( action='test_all_srvs', title=' - Insatisfactorios', thumbnail=config.get_thumb('flame'), unsatisfactory = True ))

    itemlist.append(item.clone( action='', title='[B]Ver Ficheros:[/B]', thumbnail=config.get_thumb('tools'), text_color='violet' ))

    if os.path.exists(os.path.join(config.get_data_path(), 'servers_todo.log')):
        itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Log Servidores',
                                    todo = 'servers_todo.log', thumbnail=config.get_thumb('crossroads') ))

    if os.path.exists(os.path.join(config.get_data_path(), 'qualities_todo.log')):
        itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Log Calidades',
                                    todo = 'qualities_todo.log', thumbnail=config.get_thumb('quote') ))

    if os.path.exists(os.path.join(config.get_data_path(), 'proxies.log')):
        itemlist.append(item.clone( channel='helper', action='show_todo_log', title=' - Log Proxies',
                                    todo = 'proxies.log', thumbnail=config.get_thumb('dev') ))

    itemlist.append(item.clone( channel='helper', action='show_log', title=' - Log Sistema', thumbnail=config.get_thumb('computer') ))

    itemlist.append(item.clone( channel='helper', action='show_advs', title=' - AdvancedSettings', thumbnail=config.get_thumb('quote') ))

    if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developer.py')) or os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'test.py')):
        itemlist.append(item.clone( action='', title='[B]Gestionar:[/B]', thumbnail=config.get_thumb('tools'), text_color='teal' ))

        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developer.py')):
            itemlist.append(Item( channel='developer', action='mainlist', title=' - Géneros', thumbnail=config.get_thumb('genres') ))

        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'test.py')):
            itemlist.append(Item( channel='test', action='mainlist', title=' - Tests Canales y Servidores', thumbnail=config.get_thumb('tools') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= 'Configuración', thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

    return itemlist


def submnu_genres(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel='generos', action='mainlist', title='[B]Géneros[/B]', thumbnail=config.get_thumb('genres'), text_color='moccasin' ))

    itemlist.append(item.clone( action='', title= '[B]Canales que pueden necesitar proxies nuevamente:[/B]', text_color='red' ))

    itemlist.append(item.clone( channel='groups', action='ch_generos', title=' - Canales con películas', group = 'generos', extra = 'movies',
                                thumbnail=config.get_thumb('movie'), text_color='deepskyblue' ))

    itemlist.append(item.clone( channel='groups', action='ch_generos', title=' - Canales con series', group = 'generos', extra = 'tvshows',
                                thumbnail=config.get_thumb('tvshow'), text_color='hotpink' ))

    return itemlist


def submnu_special(item):
    logger.info()
    itemlist = []

    if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies':
        itemlist.append(item.clone( action='', title = '[COLOR deepskyblue][B]Películas[COLOR goldenrod] Recomendadas:[/B][/COLOR]',
                                    thumbnail=config.get_thumb('movie'), folder=False ))

        itemlist.append(Item( channel='cinedeantes', action='list_all', title=' - Las joyas del cine clásico',
                              url = 'https://cinedeantes2.weebly.com/joyas-del-cine.html', thumbnail=config.get_thumb('bestmovies'),search_type = 'movie' ))

        itemlist.append(Item( channel='adnstream', action='_ayer_y_siempre', title=' - Las mejores del cine de ayer y siempre', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='zoowomaniacos', action='_culto', title=' - Las mejores del cine de culto', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='cinequinqui', action='list_all', title=' - Las mejores del cine quinqui',
                              url = 'https://cinekinkihd.freesite.host/movies/', group = 'best', thumbnail=config.get_thumb('bestmovies'),search_type = 'movie' ))

        itemlist.append(Item( channel='zoowomaniacos', action='_las1001', title=' - Las 1001 que hay que ver', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(item.clone( action='', title='[COLOR deepskyblue][B]Películas[/COLOR] búsquedas a través de listas:[/B]',
                                        thumbnail=config.get_thumb('movie'), folder=False, text_color='pink' ))

            itemlist.append(Item( channel='tmdblists', action='listado', title= ' - En cartelera', extra='now_playing', thumbnail=config.get_thumb('movie'), search_type = 'movie' ))

            if not current_month == 4:
                itemlist.append(Item( channel='filmaffinitylists', action='_oscars', title=' - Premios Oscar', thumbnail=config.get_thumb('oscars'), search_type = 'movie' ))

            itemlist.append(Item( channel='filmaffinitylists', action='_sagas', title=' - Sagas y colecciones', thumbnail=config.get_thumb('bestsagas'), search_type = 'movie' ))

            itemlist.append(Item( channel='tmdblists', action='listado', title= ' - Más populares', extra='popular', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

            itemlist.append(Item( channel='tmdblists', action='listado', title= ' - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

            itemlist.append(Item( channel='filmaffinitylists', action='_bestmovies', title=' - Recomendadas', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

            itemlist.append(Item( channel='tmdblists', action='networks', title=' - Por productora', thumbnail=config.get_thumb('movie'), search_type = 'movie' ))

            itemlist.append(Item( channel='tmdblists', action='generos', title=' - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'movie' ))

            itemlist.append(Item( channel='tmdblists', action='anios', title=' - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'movie' ))

            if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'tvshows':
                itemlist.append(item.clone( action='', title = '[COLOR hotpink][B]Series[/COLOR] búsquedas a través de listas:[/B]',
                                            thumbnail=config.get_thumb('tvshow'), folder=False, text_color='pink' ))

                itemlist.append(Item( channel='tmdblists', action='listado', title= ' - En emisión', extra='on_the_air', thumbnail=config.get_thumb('tvshow'), search_type = 'tvshow' ))

                if not current_month == 10:
                    itemlist.append(Item( channel='filmaffinitylists', action='_emmys', title=' - Premios Emmy', thumbnail=config.get_thumb('emmys'),
                                          origen='mnu_esp', search_type = 'tvshow' ))

            itemlist.append(Item( channel='tmdblists', action='listado', title= ' - Más populares', extra='popular', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(Item( channel='tmdblists', action='listado', title= ' - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(Item( channel='filmaffinitylists', action='_besttvshows', title=' - Recomendadas', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

            itemlist.append(Item( channel='tmdblists', action='generos', title=' - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'tvshow' ))

            itemlist.append(Item( channel='tmdblists', action='anios', title=' - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'tvshow' ))

            if not item.no_docs:
                if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'documentaries':
                    itemlist.append(item.clone( action='', title = '[COLOR cyan][B]Documentales[/COLOR] búsquedas a través de listas:[/B]',
                                                thumbnail=config.get_thumb('documentary'), folder=False, text_color='pink' ))

                if config.get_setting('mnu_documentales', default=True):
                    itemlist.append(Item( channel='filmaffinitylists', action='_bestdocumentaries', title=' - Los Mejores',
                                          thumbnail=config.get_thumb('bestdocumentaries'), search_type = 'all' ))

            if not item.extra == 'documentaries':
                itemlist.append(item.clone( action='', title = '[COLOR yellow][B]Películas y Series[/COLOR] búsquedas a través de listas:[/B]',
                                            thumbnail=config.get_thumb('heart'), folder=False, text_color='pink' ))

                itemlist.append(Item( channel='filmaffinitylists', action='plataformas', title=' - Películas y series por plataforma', thumbnail=config.get_thumb('heart'), search_type = 'all' ))

                itemlist.append(Item( channel='filmaffinitylists', action='_genres', title=' - Películas y series por género', thumbnail=config.get_thumb('listgenres'), search_type = 'all' ))

                itemlist.append(Item( channel='filmaffinitylists', action='_years', title=' - Películas y series por año', thumbnail=config.get_thumb('listyears'), search_type = 'all' ))

                itemlist.append(Item( channel='filmaffinitylists', action='_themes', title=' - Películas y series por tema', thumbnail=config.get_thumb('listthemes'), search_type = 'all' ))

    return itemlist


def submnu_search(item):
    logger.info()
    itemlist = []

    if config.get_setting('search_extra_proxies', default=True):
        itemlist.append(item.clone( action='', title='[B]Búsquedas en canales con Proxies:[/B]', folder=False, text_color='red' ))

        itemlist.append(item.clone( channel='filters', title=' - Qué canales pueden usar proxies', action='with_proxies',
                                    thumbnail=config.get_thumb('stack'), new_proxies=True ))

        if config.get_setting('memorize_channels_proxies', default=True):
            itemlist.append(item.clone( channel='filters', title=  ' - Qué [COLOR red]canales[/COLOR] tiene con proxies memorizados', action='with_proxies',
                                        thumbnail=config.get_thumb('stack'), new_proxies=True, memo_proxies=True, test_proxies=True ))

        itemlist.append(item.clone( channel='actions', title= ' - Quitar los proxies en los canales [COLOR red](que los tengan memorizados)[/COLOR]',
                                    action = 'manto_proxies', thumbnail=config.get_thumb('flame') ))

        itemlist.append(item.clone( channel='proxysearch', title=' - Configurar proxies a usar [COLOR plum](en los canales que los necesiten)[/COLOR]',
                                    action='proxysearch_all', thumbnail=config.get_thumb('flame') ))

        itemlist.append(item.clone( channel='helper', action='show_help_proxies', title= ' - [COLOR green][B]Información Uso de proxies[/B][/COLOR]' ))

        if config.get_setting('proxysearch_excludes', default=''):
            itemlist.append(item.clone( channel='proxysearch', title=' - Anular los canales excluidos de Configurar proxies a usar',
                                        action='channels_proxysearch_del', thumbnail=config.get_thumb('flame'), text_color='coral' ))

    if item.only_options_proxies: return itemlist

    itemlist.append(item.clone( action='', title= '[B]Personalización búsquedas:[/B]', folder=False, text_color='moccasin' ))

    itemlist.append(item.clone( channel='search', action='show_help_parameters', title='[COLOR chocolate][B] - Qué ajustes tiene configurados para las búsquedas[/B][/COLOR]',
                                thumbnail=config.get_thumb('help') ))

    itemlist.append(item.clone( channel='filters', action='no_actives', title=' - Qué canales no intervienen en las búsquedas (están desactivados)',
                                thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='filters', action='channels_status', title=' - Personalizar canales (Desactivar o Re-activar)',
                                des_rea=True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='filters', action='only_prefered', title=' - Qué canales tiene marcados como preferidos',
                                thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='filters', action='channels_status', title=' - Personalizar canales Preferidos (Marcar o Des-marcar)',
                                des_rea=False, thumbnail=config.get_thumb('stack') ))

    if item.extra == 'movies':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR deepskyblue]Películas[/B][/COLOR]',
                                    extra='movies', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_movies:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR deepskyblue]Películas[/B][/COLOR]',
                                        extra='movies' ))

    elif item.extra == 'tvshows':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR hotpink]Series[[/B]/COLOR]',
                                    extra='tvshows', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_tvshows:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR hotpink]Series[/B][/COLOR]',
                                        extra='tvshows' ))

    elif item.extra == 'documentaries':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR cyan]Documentales[/B][/COLOR]',
                                    extra='documentaries', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_documentaries:
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR cyan]Documentales[/B][/COLOR]',
                                        extra='documentaries' ))

    elif item.extra == 'torrents':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales [COLOR blue]Torrent[/COLOR][COLOR tomato]en las búsquedas para [COLOR yellow]Películas y/o Series[/B][/COLOR]',
                                    extra='torrents', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_mixed:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales [COLOR blue]Torrent[/COLOR][COLOR coral]excluidos en las búsquedas para Películas y/o Series[/B][/COLOR]',
                                        extra='torrents' ))

    else:
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR tomato][B]Excluir canales en las búsquedas de [COLOR green]Todos[/B][/COLOR]',
                                    extra='all', thumbnail=config.get_thumb('stack') ))

        if channels_search_excluded_all:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral][B]Anular los canales excluidos en las búsquedas de [COLOR green]Todos[/B][/COLOR]',
                                        extra='all' ))

    itemlist.append(item.clone( action='', title= '[B]Configuración:[/B]', folder=False, text_color='goldenrod' ))

    itemlist.append(item.clone( channel='actions', title=' - Ajustes categorías [COLOR goldenrod](proxies y buscar)[/COLOR]', action = 'open_settings',
                                thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='search', action='show_help', title='[COLOR green][B]Información búsquedas[/B][/COLOR]',
                                thumbnail=config.get_thumb('help') ))

    return itemlist

def _marcar_canal(item):
    config.set_setting('status', item.estado, item.from_channel)
    platformtools.itemlist_refresh()

def _refresh_menu(item):
    platformtools.dialog_notification(config.__addon_name, 'Refrescando [B][COLOR %s]caché Menú[/COLOR][/B]' % color_exec)
    platformtools.itemlist_refresh()


def _dominios(item):
    logger.info()

    if item.from_channel == 'hdfull':
        from channels import hdfull
        item.channel = 'hdfull'
        hdfull.configurar_dominio(item)

def _credenciales_hdfull(item):
    logger.info()

    from core import filetools, jsontools

    channel_json = 'hdfull.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] HdFull') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    from channels import hdfull

    item.channel = 'hdfull'

    if config.get_setting('hdfull_login', 'hdfull', default=False): hdfull.logout(item)

    hdfull.login('')

    _refresh_menu(item)

def _credenciales_playdede(item):
    logger.info()

    from core import filetools, jsontools

    channel_json = 'playdede.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    data = filetools.read(filename_json)
    params = jsontools.load(data)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s] PlayDede') % color_avis
        platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    from channels import playdede

    item.channel = 'playdede'

    if config.get_setting('playdede_login', 'playdede', default=False): playdede.logout(item)

    playdede.login('')

    _refresh_menu(item)

def _proxies(item):
    logger.info()

    if item.from_channel == 'cinecalidad':
        from channels import cinecalidad
        item.channel = 'cinecalidad'
        cinecalidad.configurar_proxies(item)

    elif item.from_channel == 'cinetux':
        from channels import cinetux
        item.channel = 'cinetux'
        cinetux.configurar_proxies(item)

    elif item.from_channel == 'cliver':
        from channels import cliver
        item.channel = 'cliver'
        cliver.configurar_proxies(item)

    elif item.from_channel == 'cliversite':
        from channels import cliversite
        item.channel = 'cliversite'
        cliversite.configurar_proxies(item)

    elif item.from_channel == 'cuevana3':
        from channels import cuevana3
        item.channel = 'cuevana3'
        cuevana3.configurar_proxies(item)

    elif item.from_channel == 'cuevana3video':
        from channels import cuevana3video
        item.channel = 'cuevana3video'
        cuevana3video.configurar_proxies(item)

    elif item.from_channel == 'dilo':
        from channels import dilo
        item.channel = 'dilo'
        dilo.configurar_proxies(item)

    elif item.from_channel == 'divxtotal':
        from channels import divxtotal
        item.channel = 'divxtotal'
        divxtotal.configurar_proxies(item)

    elif item.from_channel == 'documaniatv':
        from channels import documaniatv
        item.channel = 'documaniatv'
        documaniatv.configurar_proxies(item)

    elif item.from_channel == 'dontorrents':
        from channels import dontorrents
        item.channel = 'dontorrents'
        dontorrents.configurar_proxies(item)

    elif item.from_channel == 'dontorrentsin':
        from channels import dontorrentsin
        item.channel = 'dontorrentsin'
        dontorrentsin.configurar_proxies(item)

    elif item.from_channel == 'entrepeliculasyseries':
        from channels import entrepeliculasyseries
        item.channel = 'entrepeliculasyseries'
        entrepeliculasyseries.configurar_proxies(item)

    elif item.from_channel == 'estrenoscinesaa':
        from channels import estrenoscinesaa
        item.channel = 'estrenoscinesaa'
        estrenoscinesaa.configurar_proxies(item)

    elif item.from_channel == 'gnula':
        from channels import gnula
        item.channel = 'gnula'
        gnula.configurar_proxies(item)

    elif item.from_channel == 'grantorrent':
        from channels import grantorrent
        item.channel = 'grantorrent'
        grantorrent.configurar_proxies(item)

    elif item.from_channel == 'hdfull':
        from channels import hdfull
        item.channel = 'hdfull'
        hdfull.configurar_proxies(item)

    elif item.from_channel == 'hdfullcom':
        from channels import hdfullcom
        item.channel = 'hdfullcom'
        hdfullcom.configurar_proxies(item)

    elif item.from_channel == 'hdfullse':
        from channels import hdfullse
        item.channel = 'hdfullse'
        hdfullse.configurar_proxies(item)

    elif item.from_channel == 'lilatorrent':
        from channels import lilatorrent
        item.channel = 'lilatorrent'
        lilatorrent.configurar_proxies(item)

    elif item.from_channel == 'megaserie':
        from channels import megaserie
        item.channel = 'megaserie'
        megaserie.configurar_proxies(item)

    elif item.from_channel == 'mejortorrentnz':
        from channels import mejortorrentnz
        item.channel = 'mejortorrentnz'
        mejortorrentnz.configurar_proxies(item)

    elif item.from_channel == 'movidytv':
        from channels import movidytv
        item.channel = 'movidytv'
        movidytv.configurar_proxies(item)

    elif item.from_channel == 'newpct1':
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Configurar proxies desde el canal[/COLOR][/B]' % color_avis)

    elif item.from_channel == 'pelisgratis':
        from channels import pelisgratis
        item.channel = 'pelisgratis'
        pelisgratis.configurar_proxies(item)

    elif item.from_channel == 'pelishouse':
        from channels import pelishouse
        item.channel = 'pelishouse'
        pelishouse.configurar_proxies(item)

    elif item.from_channel == 'pelispedia':
        from channels import pelispedia
        item.channel = 'pelispedia'
        pelispedia.configurar_proxies(item)

    elif item.from_channel == 'pelispedia2':
        from channels import pelispedia2
        item.channel = 'pelispedia2'
        pelispedia2.configurar_proxies(item)

    elif item.from_channel == 'pelisplanet':
        from channels import pelisplanet
        item.channel = 'pelisplanet'
        pelisplanet.configurar_proxies(item)

    elif item.from_channel == 'pelisplay':
        from channels import pelisplay
        item.channel = 'pelisplay'
        pelisplay.configurar_proxies(item)

    elif item.from_channel == 'pelisxd':
        from channels import pelisxd
        item.channel = 'pelisxd'
        pelisxd.configurar_proxies(item)

    elif item.from_channel == 'playdede':
        from channels import playdede
        item.channel = 'playdede'
        playdede.configurar_proxies(item)

    elif item.from_channel == 'playview':
        from channels import playview
        item.channel = 'playview'
        playview.configurar_proxies(item)

    elif item.from_channel == 'pornhub':
        from channels import pornhub
        item.channel = 'pornhub'
        pornhub.configurar_proxies(item)

    elif item.from_channel == 'ppeliculas':
        from channels import ppeliculas
        item.channel = 'ppeliculas'
        ppeliculas.configurar_proxies(item)

    elif item.from_channel == 'repelishd':
        from channels import repelishd
        item.channel = 'repelishd'
        repelishd.configurar_proxies(item)

    elif item.from_channel == 'rojotorrent':
        from channels import rojotorrent
        item.channel = 'rojotorrent'
        rojotorrent.configurar_proxies(item)

    elif item.from_channel == 'seriesyonkis':
        from channels import seriesyonkis
        item.channel = 'seriesyonkis'
        subtorrents.configurar_proxies(item)

    elif item.from_channel == 'subtorrents':
        from channels import subtorrents
        item.channel = 'subtorrents'
        subtorrents.configurar_proxies(item)

    elif item.from_channel == 'torrentdivx':
        from channels import torrentdivx
        item.channel = 'torrentdivx'
        torrentdivx.configurar_proxies(item)

    elif item.from_channel == 'verdetorrent':
        from channels import verdetorrent
        item.channel = 'verdetorrent'
        verdetorrent.configurar_proxies(item)

    elif item.from_channel == 'xvideos':
        from channels import xvideos
        item.channel = 'xvideos'
        xvideos.configurar_proxies(item)

def _quitar_proxies(item):
    el_canal = ('Quitando proxies [B][COLOR %s]' + item.from_channel.capitalize() + '[/COLOR][/B]') % color_avis
    platformtools.dialog_notification(config.__addon_name, el_canal)

    config.set_setting('proxies', '', item.from_channel)
    platformtools.itemlist_refresh()


def _test_webs(item):
    el_canal = ('Test web canal [B][COLOR %s]' + item.from_channel.capitalize() + '[/COLOR][/B]') % color_adver
    platformtools.dialog_notification(config.__addon_name, el_canal)

    from modules import tester
    tester.test_channel(item.from_channel)


def test_all_webs(item):
    logger.info()

    config.set_setting('developer_test_channels', '')

    if item.unsatisfactory: text = '¿ Iniciar el Test Web de los Canales INSATISFACTORIOS ?'
    else: text = '¿ Iniciar el Test Web de TODOS los Canales ?'

    if not platformtools.dialog_yesno(config.__addon_name, text):
        return

    if item.unsatisfactory: config.set_setting('developer_test_channels', 'unsatisfactory')

    from core import channeltools

    from modules import tester

    filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        i += 1
        tester.test_channel(ch['name'])

    if i > 0: platformtools.dialog_ok(config.__addon_name, 'Canales Testeados ' + str(i))

    config.set_setting('developer_test_channels', '')


def test_all_srvs(item):
    logger.info()

    config.set_setting('developer_test_servers', '')

    if item.unsatisfactory: text = '¿ Iniciar el Test Web de los Servidores INSATISFACTORIOS ?'
    else: text = '¿ Iniciar el Test Web de TODOS los Servidores ?'

    if not platformtools.dialog_yesno(config.__addon_name, text):
        return

    if item.unsatisfactory: config.set_setting('developer_test_servers', 'unsatisfactory')

    from core import filetools, jsontools

    from modules import tester

    path = os.path.join(config.get_runtime_path(), 'servers')

    servidores = os.listdir(path)

    i = 0

    for server in servidores:
        if not server.endswith('.json'): continue

        path_server = os.path.join(config.get_runtime_path(), 'servers', server)

        if not os.path.isfile(path_server): continue

        data = filetools.read(path_server)
        dict_server = jsontools.load(data)

        if dict_server['active'] == False: continue

        i += 1

        tester.test_server(dict_server['name'])

    if i > 0: platformtools.dialog_ok(config.__addon_name, 'Servidores Testeados ' + str(i))

    config.set_setting('developer_test_servers', '')

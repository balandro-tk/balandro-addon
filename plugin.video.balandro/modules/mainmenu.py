# -*- coding: utf-8 -*-

import os

from datetime import datetime

from platformcode import config, logger, updater
from core.item import Item

from core import channeltools


color_list_prefe = config.get_setting('channels_list_prefe_color', default='gold')
color_list_proxies = config.get_setting('channels_list_proxies_color', default='red')
color_list_inactive = config.get_setting('channels_list_inactive_color', default='gray')

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')

current_year = int(datetime.today().year)
current_month = int(datetime.today().month)


def mainlist(item):
    logger.info()
    item.category = config.__addon_name

    itemlist = []

    if config.get_setting('developer_mode', default=False):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_developer', title = '[B]Desarrollo[/B]', thumbnail=config.get_thumb('team'), text_color='darkorange' ))

    if config.get_setting('mnu_search_proxy_channels', default=False):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='Buscar Nuevos Proxies',
                                    only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

    if current_month == 4:
        itemlist.append(Item( channel='filmaffinitylists', action='_oscars', title='Premios Oscar ' + str(current_year), text_color='orchid',
                              thumbnail=config.get_thumb('oscars'), plot = 'Las películas nominadas a los premios Oscars' ))

    elif current_month == 10:
        itemlist.append(Item( channel='filmaffinitylists', action='_emmys', title='Premios Emmy ' + str(current_year), text_color='orchid',
                              thumbnail=config.get_thumb('emmys'), plot = 'Las Series nominadas a los premios Emmy' ))

    elif current_month == 11:
         itemlist.append(Item( channel='tmdblists', action='descubre', title='Halloween', text_color='orchid', extra = 27, search_type = 'movie',
                               thumbnail=config.get_thumb('halloween'), plot = 'Películas del género Terror' ))

    if config.get_setting('sub_mnu_special', default=True):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='Especiales', extra='all',
                                    thumbnail=config.get_thumb('heart'), text_color='pink' ))

    context = []
    tit = '[COLOR %s][B]Información Ajustes actuales[/B][/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'search', 'action': 'show_help_parameters'})

    tit = '[COLOR %s][B]Global configurar proxies[/B][/COLOR]' % color_list_proxies
    context.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

    if config.get_setting('proxysearch_excludes', default=''):
        tit = '[COLOR %s]Anular canales excluidos en Proxies[/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

    tit = '[COLOR %s]Información proxies[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

    tit = '[COLOR %s][B]Quitar los proxies actuales[/B][/COLOR]' % color_list_proxies
    context.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

    tit = '[COLOR %s]Información búsquedas[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

    tit = '[COLOR %s]Ajustes categoría buscar y proxies[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    itemlist.append(Item( channel='search', action='mainlist', title='Buscar', context=context, thumbnail=config.get_thumb('search'), text_color='yellow' ))

    context = []
    tit = '[COLOR %s]Información Parámetros Menús[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

    tit = '[COLOR %s]Ajustes categoría canales y buscar[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if config.get_setting('mnu_sugeridos', default=True):
        itemlist.append(item.clone( action='channels', extra='suggested', title='Sugeridos', context=context, thumbnail=config.get_thumb('stack'),
                                    text_color='aquamarine' ))

    if config.get_setting('channels_link_main', default=True):
        itemlist.append(item.clone( action='channels', extra='all', title='Canales', context=context, thumbnail=config.get_thumb('stack'),
                                    text_color='gold' ))

    if config.get_setting('mnu_idiomas', default=True):
        context2 = []
        tit = '[COLOR %s]Información Parámetros Menús[/COLOR]' % color_infor
        context2.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

        tit = '[COLOR %s]Ajustes categoría menú y play[/COLOR]' % color_exec
        context2.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

        itemlist.append(Item( channel='groups', action='mainlist', mnu_lang='idiomas', title='Idiomas', context=context2,
                              thumbnail=config.get_thumb('idiomas'), text_color='limegreen' ))

    if config.get_setting('mnu_grupos', default=True):
        context2 = []
        tit = '[COLOR %s]Información Parámetros Menús[/COLOR]' % color_infor
        context2.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

        tit = '[COLOR %s]Ajustes categoría menú[/COLOR]' % color_exec
        context2.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

        itemlist.append(Item( channel='groups', action='mainlist', extra='groups', title='Grupos', context=context2,
                              thumbnail=config.get_thumb('bookshelf'), text_color='magenta' ))

    if not config.get_setting('mnu_simple', default=False):
       if config.get_setting('mnu_pelis', default=True):
           itemlist.append(item.clone( action='channels', extra='movies', title='Películas', context=context, thumbnail=config.get_thumb('movie'),
                                       text_color='deepskyblue' ))

       if config.get_setting('mnu_series', default=True):
           itemlist.append(item.clone( action='channels', extra='tvshows', title='Series', context=context, thumbnail=config.get_thumb('tvshow'),
                                       text_color='hotpink' ))

       if config.get_setting('channels_link_pyse', default=False):
          itemlist.append(item.clone( action='channels', extra='mixed', title='Películas y Series', context=context, no_docs = True,
                                      thumbnail=config.get_thumb('booklet'), text_color='teal' ))

       if config.get_setting('mnu_generos', default=True):
          context2 = []
          tit = '[COLOR %s]Información Parámetros Menús[/COLOR]' % color_infor
          context2.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

          tit = '[COLOR %s]Ajustes categoría menú[/COLOR]' % color_exec
          context2.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

          itemlist.append(item.clone( channel='submnuctext', action='submnu_genres', title= 'Géneros', context=context2,
                                      thumbnail=config.get_thumb('genres'), text_color='thistle' ))

       if config.get_setting('mnu_documentales', default=True):
           itemlist.append(item.clone( action='channels', extra='documentaries', title='Documentales', context=context,
                                       thumbnail=config.get_thumb('documentary'), text_color='cyan' ))

       if config.get_setting('mnu_infantiles', default=True):
           itemlist.append(item.clone( action='channels', extra='infantil', title='Infantiles', context=context, thumbnail=config.get_thumb('booklet'),
                                       text_color='lightyellow' ))

       if config.get_setting('mnu_novelas', default=True):
           itemlist.append(item.clone( action='channels', extra='tales', title='Novelas', context=context, thumbnail=config.get_thumb('booklet'),
                                       text_color='limegreen' ))

       if config.get_setting('mnu_torrents', default=True):
           context2 = []
           if config.get_setting('cliente_torrent') == 'Seleccionar' or config.get_setting('cliente_torrent') == 'Ninguno':
               tit = '[COLOR %s]Información Motores torrents[/COLOR]' % color_infor
               context2.append({'title': tit, 'channel': 'helper', 'action': 'show_help_torrents'})

           tit = '[COLOR %s][B]Motores torrents instalados[/B][/COLOR]' % color_infor
           context2.append({'title': tit, 'channel': 'helper', 'action': 'show_clients_torrent'})

           tit = '[COLOR %s]Información Parámetros Menús[/COLOR]' % color_infor
           context2.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

           tit = '[COLOR %s]Ajustes categoría canales y buscar[/COLOR]' % color_exec
           context2.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

           itemlist.append(item.clone( action='channels', extra='torrents', title='Torrents', context=context2, thumbnail=config.get_thumb('torrents'),
                                       text_color='blue' ))

       if config.get_setting('mnu_doramas', default=True):
           itemlist.append(item.clone( action='channels', extra='dorama', title='Doramas', context=context, thumbnail=config.get_thumb('computer'),
                                       text_color='firebrick' ))
       context2 = []
       if config.get_setting('adults_password'):
           tit = '[COLOR %s][B]Eliminar Pin parental[/B][/COLOR]' % color_infor
           context2.append({'title': tit, 'channel': 'actions', 'action': 'adults_password_del'})

           tit = '[COLOR %s]Refrescar caché menú[/COLOR]' % color_adver
           context2.append({'title': tit, 'channel': item.channel, 'action': '_refresh_menu'})
       else:
           tit = '[COLOR %s][B]Información parental[/B][/COLOR]' % color_infor
           context2.append({'title': tit, 'channel': 'helper', 'action': 'show_help_adults'})

       tit = '[COLOR %s]Información Parámetros Menús[/COLOR]' % color_infor
       context2.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

       tit = '[COLOR %s]Ajustes categoría canales y parental[/COLOR]' % color_exec
       context2.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

       if config.get_setting('mnu_animes', default=True):
           if not config.get_setting('descartar_anime', default=True):
               itemlist.append(item.clone( action='channels', extra='anime', title='Animes', context=context2, thumbnail=config.get_thumb('anime'),
                                           text_color='springgreen' ))

       if config.get_setting('mnu_adultos', default=True):
           if not config.get_setting('descartar_xxx', default=True):
               itemlist.append(item.clone( action='channels', extra='adults', title='Adultos', context=context2, thumbnail=config.get_thumb('adults'),
                                           text_color='orange' ))

       if config.get_setting('mnu_desactivados', default=True):
           context2 = []
           tit = '[COLOR %s]Información Parámetros Menús[/COLOR]' % color_infor
           context2.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

           tit = '[COLOR %s]Ajustes categoría canales[/COLOR]' % color_exec
           context2.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

           itemlist.append(item.clone( action='channels', extra='disableds', title='Desactivados', context=context2, thumbnail=config.get_thumb('stack'),
                                       text_color='gray' ))

       if config.get_setting('mnu_preferidos', default=True):
           context2 = []
           tit = '[COLOR %s][B]Información preferidos[/B][/COLOR]' % color_infor
           context2.append({'title': tit, 'channel': 'helper', 'action': 'show_help_tracking'})

           tit = '[COLOR %s][B]Eliminar Todos sus preferidos[/B][/COLOR]' % color_alert
           context2.append({'title': tit, 'channel': 'actions', 'action': 'manto_tracking_dbs'})

           tit = '[COLOR %s]Ajustes categoría preferidos[/COLOR]' % color_exec
           context2.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

           itemlist.append(Item( channel='tracking', action='mainlist', title='Preferidos', context=context2, thumbnail=config.get_thumb('videolibrary'),
                                           text_color='wheat' ))

       if config.get_setting('mnu_desargas', default=True):
           context2 = []
           tit = '[COLOR %s][B]Ubicación actual descargas[/B][/COLOR]' % color_infor
           context2.append({'title': tit, 'channel': 'downloads', 'action': 'show_folder_downloads'})

           tit = '[COLOR %s][B]Eliminar Todas las descargas[/B][/COLOR]' % color_alert
           context2.append({'title': tit, 'channel': 'actions', 'action': 'manto_folder_downloads'})

           tit = '[COLOR %s]Ajustes categoría descargas[/COLOR]' % color_exec
           context2.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

           itemlist.append(Item( channel='downloads', action='mainlist', title='Descargas', context=context2, thumbnail=config.get_thumb('downloads'),
                                           text_color='seagreen' ))

    try: last_ver = updater.check_addon_version()
    except: last_ver = True

    if not last_ver: last_ver = '[I][COLOR %s](desfasada)[/COLOR][/I]' % color_adver
    else: last_ver = ''

    context = []
    tit = '[COLOR %s][B]Información versión[/B][/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_version'})

    last_fix = config.get_addon_version()

    if not 'desfasada' in last_ver:
        if 'fix' in last_fix:
            tit = '[COLOR %s][B]Información Fix instalado[/B][/COLOR]' % color_infor
            context.append({'title': tit, 'channel': 'helper', 'action': 'show_last_fix'})

        tit = '[COLOR %s]Comprobar actualizaciones Fix[/COLOR]' % color_avis
        context.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates'})

        tit = '[COLOR %s]Forzar actualizaciones Fix[/COLOR]' % color_adver
        context.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates_force'})

    tit = '[COLOR %s][B]Log de su Media Center[/B][/COLOR]' % color_alert
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_log'})

    tit = '[COLOR %s][B]Test del sistema[/B][/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_test'})

    tit = '[COLOR %s][B]Test internet[/B][/COLOR]' % color_adver
    context.append({'title': tit, 'channel': 'actions', 'action': 'test_internet'})

    tit = '[COLOR green][B]Preguntas frecuentes[/B][/COLOR]'
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_faq'})

    tit = '[COLOR %s]Ajustes configuración[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    title = 'Ayuda (%s)  %s' % (config.get_addon_version(), last_ver)

    itemlist.append(Item( channel='helper', action='mainlist', title=title, context=context, thumbnail=config.get_thumb('help'), text_color='chartreuse' ))

    context = []
    tit = '[COLOR %s][B]Quitar sus Proxies memorizados[/B][/COLOR]' % color_alert
    context.append({'title': tit, 'channel': 'actions', 'action': 'manto_proxies'})

    tit = '[COLOR %s]Información Parámetros Menús[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_channels_parameters'})

    tit = '[COLOR %s]Sus Ajustes personalizados[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_sets'})

    tit = '[COLOR %s]Sus Cookies actuales[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_cook'})

    tit = '[COLOR %s][B]Eliminar sus Cookies[/B][/COLOR]' % color_alert
    context.append({'title': tit, 'channel': 'actions', 'action': 'manto_cookies'})

    tit = '[COLOR %s]Sus Advanced Settings[/COLOR]' % color_adver
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_advs'})

    tit = '[COLOR %s][B]Eliminar su Advanced Settings[/B][/COLOR]' % color_alert
    context.append({'title': tit, 'channel': 'actions', 'action': 'manto_advs'})

    tit = '[COLOR darkorange][B]Borrar su Carpeta Caché[/B][/COLOR]'
    context.append({'title': tit, 'channel': 'actions', 'action': 'manto_folder_cache'})

    tit = '[COLOR %s][B]Restablecer Parámetros internos[/B][/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'manto_params'})

    tit = '[COLOR green][B]Informacion Plataforma[/B][/COLOR]'
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_plataforma'})

    if not 'desfasada' in last_ver:
        if 'fix' in last_fix:
            tit = '[COLOR %s][B]Eliminar Fichero control Fix[/B][/COLOR]' % color_alert
            context.append({'title': tit, 'channel': 'actions', 'action': 'manto_last_fix'})

    itemlist.append(Item( channel='actions', action='open_settings', title='Configuración', context=context, folder=False,
                          thumbnail=config.get_thumb('settings'), text_color='chocolate' ))

    return itemlist


def channels(item):
    logger.info()
    itemlist = []

    thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
    thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')

    context = []
    tit = '[COLOR %s][B]Global configurar proxies[/B][/COLOR]' % color_list_proxies
    context.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

    if config.get_setting('proxysearch_excludes', default=''):
        tit = '[COLOR %s]Anular canales excluidos en Proxies[/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

    tit = '[COLOR %s]Información búsquedas[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

    tit = '[COLOR %s]Ajustes categoría buscar[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if item.extra == 'movies':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]',
                                        extra = 'movies', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='movie', title='[B]Buscar Película ...[/B]',
                              extra = 'movies', context=context, thumbnail=config.get_thumb('search'), text_color='deepskyblue' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='movie', title='[B]Búsquedas y listas en TMDB[/B]',
                                  thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='movie', title='[B]Listas en Filmaffinity[/B]',
                                  thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', extra='movies',
                                        thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Películas'
        accion = 'mainlist_pelis'
        filtros = {'categories': 'movie'}

    elif item.extra == 'tvshows':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]',
                                        extra = 'tvshows', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='tvshow', title='[B]Buscar Serie ...[/B]',
                              extra = 'tvshows', context=context, thumbnail=config.get_thumb('search'), text_color='hotpink' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='tvshow', title='[B]Búsquedas y listas en TMDB[/B]',
                                  thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='tvshow', title='[B]Listas en Filmaffinity[/B]',
                                  thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', extra='tvshows',
                                        thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Series'
        accion = 'mainlist_series'
        filtros = {'categories': 'tvshow'}

    elif item.extra == 'documentaries':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]',
                                        extra = 'documentaries', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='documentary', title='[B]Buscar Documental ...[/B]',
                              extra = 'documentaries', context=context, thumbnail=config.get_thumb('search'), text_color='cyan' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='documentary', title='[B]Listas en Filmaffinity[/B]',
                                  thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', extra='documentaries',
                                        thumbnail=config.get_thumb('heart'), text_color='pink' ))

        itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales con temática Documental[/B]', group = 'docs', text_color='magenta' ))

        item.category = 'Canales con Documentales'
        accion = 'mainlist'
        filtros = {'categories': 'documentary', 'searchable': True}

    elif item.extra == 'mixed':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]',
                                        extra = 'mixed', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='all', title='[B]Buscar Película y/o Serie ...[/B]',
                              extra = 'mixed', context=context, thumbnail=config.get_thumb('search'), text_color='yellow' ))

        if config.get_setting('search_extra_main', default=False):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en TMDB[/B]',
	                              thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='[B]Listas en Filmaffinity[/B]',
                                  thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', extra='all', no_docs = item.no_docs,
                                        thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Películas y Series (ambos contenidos)'
        accion = 'mainlist'
        filtros = {}

    elif item.extra == 'torrents':
        if config.get_setting('mnu_search_proxy_channels', default=False):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                        only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

        if config.get_setting('sub_mnu_cfg_search', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]',
                                        extra = 'torrents', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='all', title='[B][COLOR blue]Buscar Torrent[/COLOR] película y/o Serie ...[/B]',
                              extra = 'only_torrents', context=context, thumbnail=config.get_thumb('search'), text_color='yellow' ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', extra='torrents',
                                        thumbnail=config.get_thumb('heart'), text_color='pink' ))

        itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales que pueden tener enlaces Torrents[/B]', group = 'torrents', text_color='magenta' ))

        item.category = 'Canales con archivos Torrents'
        accion = 'mainlist'
        filtros = {'categories': 'torrent'}

    else:
        if item.extra == 'adults': pass
        elif item.extra == 'anime': pass
        elif item.extra == 'dorama': pass
        elif item.extra == 'infantil': pass
        elif item.extra == 'tales': pass

        elif not item.extra == 'groups':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            if config.get_setting('sub_mnu_cfg_search', default=True):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]',
                                            extra = 'all', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

            itemlist.append(Item( channel='search', action='search', search_type='all', title='[B]Buscar Película y/o Serie ...[/B]', context=context,
                                  thumbnail=config.get_thumb('search'), text_color='yellow' ))

            if config.get_setting('mnu_documentales', default=True):
                itemlist.append(Item( channel='search', action='search', search_type='documentary', title='[B]Buscar Documental ...[/B]', context=context,
	                                  thumbnail=config.get_thumb('search'), text_color='cyan' ))

            if config.get_setting('search_extra_main', default=False):
                itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en TMDB[/B]',
                                      thumbnail=thumb_tmdb, text_color=color_adver ))

                itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='[B]Listas en Filmaffinity[/B]',
                                      thumbnail=thumb_filmaffinity, text_color=color_adver ))

            if config.get_setting('sub_mnu_special', default=True):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_special', title='[B]Especiales[/B]', extra='all',
                                            thumbnail=config.get_thumb('heart'), text_color='pink' ))

        if item.extra == 'adults': item.category = 'Canales exclusivos para Adultos'
        elif item.extra == 'anime': item.category = 'Canales exclusivos de Animes'
        elif item.extra == 'dorama': item.category = 'Canales exclusivos de Doramas'
        elif item.extra == 'infantil': item.category = 'Canales exclusivos Infantiles'
        elif item.extra == 'tales': item.category = 'Canales con temática de Novelas'
        elif item.extra == 'suggested': item.category = 'Canales Sugeridos'
        elif not item.extra == 'groups': item.category = 'Todos los Canales'
        else: item.category = 'Canales con Agrupaciones (novedades, estrenos, temáticas, países, años, plataformas, etc.)'

        if item.extra == 'infantil':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            if config.get_setting('sub_mnu_cfg_search', default=True):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]',
                                            extra = 'mixed', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

            itemlist.append(Item( channel='search', action='search', search_type='all', title='[B]Buscar Película y/o Serie ...[/B]',
                                  extra = 'mixed', context=context, thumbnail=config.get_thumb('search'), text_color='yellow' ))

            if config.get_setting('search_extra_main', default=False):
                itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='[B]Búsquedas y listas en TMDB[/B]',
	                                  thumbnail=thumb_tmdb, text_color=color_adver ))

                itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='[B]Listas en Filmaffinity[/B]',
                                      thumbnail=thumb_filmaffinity, text_color=color_adver ))

            itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales con contenido Infantil[/B]',
                                        group = 'kids', text_color='magenta' ))

        if item.extra == 'tales':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            if config.get_setting('sub_mnu_cfg_search', default=True):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Personalizar búsquedas[/B]',
                                            extra = 'tvshows', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

            itemlist.append(Item( channel='search', action='search', search_type='all', title='[B]Buscar Serie ...[/B]',
                                  extra = 'tvshows', context=context, thumbnail=config.get_thumb('search'), text_color='hotpink' ))

            if config.get_setting('search_extra_main', default=False):
                itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='tvshow', title='[B]Búsquedas y listas en TMDB[/B]',
	                                  thumbnail=thumb_tmdb, text_color=color_adver ))

                itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='tvshow', title='[B]Listas en Filmaffinity[/B]',
                                      thumbnail=thumb_filmaffinity, text_color=color_adver ))

            itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales con contenido de Novelas[/B]',
                                        group = 'tales', text_color='magenta' ))

        if item.extra == 'dorama':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales con contenido Dorama[/B]',
                                        group = 'dorama', text_color='magenta' ))

        if item.extra == 'adults' or item.extra == 'anime':
            if config.get_setting('mnu_search_proxy_channels', default=False):
                itemlist.append(item.clone( channel='submnuctext', action='submnu_search', title='[B]Buscar Nuevos Proxies[/B]',
                                            only_options_proxies = True, thumbnail=config.get_thumb('flame'), text_color='red' ))

            if not config.get_setting('adults_password'):
                itemlist.append(Item( channel='helper', action='show_help_adults', title='[B]Información parental[/B]',
                                      thumbnail=config.get_thumb('help'), text_color='green' ))

                if item.extra == 'adults':
                    itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales que pueden tener vídeos para Adultos[/B]',
                                                group = 'adults', text_color='magenta' ))

                if item.extra == 'anime':
                    itemlist.append(item.clone( channel='groups', action = 'ch_groups', title = '[B]Canales con contenido Anime[/B]',
                                                group = 'anime', text_color='magenta' ))

        accion = 'mainlist'
        filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        if item.extra == 'disableds':
            if not ch['status'] == -1: continue
        else:
            if config.get_setting('mnu_desactivados', default=True):
                if ch['status'] == -1: continue

        if item.extra == 'movies':
            if ch['searchable'] == False:
                if 'adults' in ch['clusters']: continue
                elif 'anime' in ch['clusters']: continue
                elif 'dorama' in ch['clusters']: continue
                elif 'infantil' in ch['clusters']: continue
                elif 'tales' in ch['clusters']: continue

        elif item.extra == 'tvshows':
            if ch['searchable'] == False:
                if 'adults' in ch['clusters']: continue
                elif 'anime' in ch['clusters']: continue
                elif 'dorama' in ch['clusters']: continue
                elif 'infantil' in ch['clusters']: continue
                elif 'tales' in ch['clusters']: continue

        elif item.extra == 'adults':
            if ch['searchable'] == True: continue
            if not 'adults' in ch['clusters']: continue

        elif item.extra == 'anime':
            if ch['searchable'] == True: continue
            if not 'anime' in ch['clusters']: continue

        elif item.extra == 'mixed':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

            if not 'movie' in tipos: continue
            if not 'tvshow' in tipos: continue

        elif item.extra == 'torrents':
            tipos = ch['search_types']
            if 'documentary' in tipos: continue

        elif item.extra == 'suggested':
            if not 'suggested' in ch['clusters']: continue

            if not config.get_setting('mnu_documentales', default=True):
               if str(ch['search_types']) == "['documentary']": continue

            if not config.get_setting('mnu_novelas', default=True):
                if 'exclusivamente en Novelas' in ch['notes']: continue

        elif item.extra == 'infantil':
            if not 'infantil' in ch['clusters']: continue

        elif item.extra == 'tales':
            if not 'tales' in ch['clusters']: continue

        elif item.extra == 'dorama':
            if ch['searchable'] == True: continue
            if not 'dorama' in ch['clusters']: continue

        else:
           if config.get_setting('mnu_simple', default=False):
               if ch['searchable'] == False:
                   if 'adults' in ch['clusters']: continue
                   elif 'anime' in ch['clusters']: continue
                   elif 'dorama' in ch['clusters']: continue
                   elif 'infantil' in ch['clusters']: continue
                   elif 'tales' in ch['clusters']: continue
               else:
                   if not config.get_setting('mnu_documentales', default=True):
                       if str(ch['search_types']) == "['documentary']": continue

                   if not config.get_setting('mnu_novelas', default=True):
                       if 'exclusivamente en Novelas' in ch['notes']: continue

           else:
              if not config.get_setting('mnu_documentales', default=True):
                  if str(ch['search_types']) == "['documentary']": continue

              if not config.get_setting('mnu_infantiles', default=True):
                  if 'infantil' in ch['clusters']: continue

              if not config.get_setting('mnu_novelas', default=True):
                  if 'exclusivamente en Novelas' in ch['notes']: continue
                  if 'tales' in ch['clusters']: continue

              if not config.get_setting('mnu_torrents', default=True):
                  if 'enlaces Torrent exclusivamente' in ch['notes']: continue

              if not config.get_setting('mnu_doramas', default=True):
                  if ch['searchable'] == False: continue
                  if 'dorama' in ch['clusters']: continue

              if not config.get_setting('mnu_animes', default=True):
                  if ch['searchable'] == False: continue
                  if 'anime' in ch['clusters']: continue

              if not config.get_setting('mnu_adultos', default=True):
                  if ch['searchable'] == False: continue
                  if 'adults' in ch['clusters']: continue

        context = []

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

        if 'proxies' in ch['notes'].lower():
            if config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s][B]Quitar los proxies del canal[/B][/COLOR]' % color_list_proxies
                context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_proxies'})

        if ch['status'] != 1:
            tit = '[COLOR %s][B]Marcar canal como Preferido[/B][/COLOR]' % color_list_prefe
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 1})

        if ch['status'] != 0:
            if ch['status'] == 1:
                tit = '[COLOR %s][B]Des-Marcar canal como Preferido[/B][/COLOR]' % color_list_prefe
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            elif ch['status'] == -1:
                tit = '[COLOR %s][B]Des-Marcar canal como Desactivado[/B][/COLOR]' % color_list_inactive
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            else:
                tit = '[COLOR white][B]Marcar canal como Activo[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})

        if ch['status'] != -1:
            tit = '[COLOR %s][B]Marcar canal como Desactivado[/B][/COLOR]' % color_list_inactive
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': -1})

        if 'current' in ch['clusters']:
            tit = '[COLOR yellowgreen][B]Dominio vigente[/B][/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_vigente'})

            tit = '[COLOR darkorange][B]Modificar dominio Memorizado[/B][/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_memorizado'})

            tit = '[COLOR %s][B]Configurar dominio a usar[/B][/COLOR]' % color_adver
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominios'})

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] +'_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] +'_password'

            if not config.get_setting(cfg_user_channel, default='') or not config.get_setting(cfg_pass_channel, default=''):
                tit = '[COLOR green][B]Información para Registrarse[/B][/COLOR]'
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_register'})

                tit = '[COLOR teal][B]Credenciales Cuenta[/B][/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_credenciales'})
            else:
               cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] +'_login'

               presentar = True
               if 'dominios' in ch['notes'].lower():
                   cfg_dominio_channel = 'channel_' + ch['id'] + '_dominio'
                   if not config.get_setting(cfg_dominio_channel, default=''): presentar = False

               if presentar:
                   if config.get_setting(cfg_login_channel, default=False):
                       tit = '[COLOR teal][B]Cerrar sesión[/B][/COLOR]'
                       context.append({'title': tit, 'channel': item.channel, 'action': '_credenciales'})

        if 'proxies' in ch['notes'].lower():
            if not config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s]Información proxies[/COLOR]' % color_infor
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

            tit = '[COLOR %s][B]Configurar proxies a usar[/B][/COLOR]' % color_list_proxies
            context.append({'title': tit, 'channel': item.channel, 'action': '_proxies'})

            tit = '[COLOR %s]Refrescar caché menú[/COLOR]' % color_exec
            context.append({'title': tit, 'channel': item.channel, 'action': '_refresh_menu'})

        tit = '[COLOR darkorange][B]Test Web del canal[/B][/COLOR]'
        context.append({'title': tit, 'channel': item.channel, 'action': '_tests'})

        color = color_list_prefe if ch['status'] == 1 else 'white' if ch['status'] == 0 else color_list_inactive

        plot = ''
        if item.extra == 'all': plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
        plot += '[' + ', '.join([idioma_canal(lg) for lg in ch['language']]) + ']'
        if ch['notes'] != '': plot += '[CR][CR]' + ch['notes']

        titulo = ch['name']

        if ch['status'] == -1:
            titulo += '[I][COLOR %s] (desactivado)[/COLOR][/I]' % color_list_inactive
            if config.get_setting(cfg_proxies_channel, default=''): titulo += '[I][COLOR %s] (proxies)[/COLOR][/I]' % color_list_proxies
        else:
            if config.get_setting(cfg_proxies_channel, default=''):
                if ch['status'] == 1: titulo += '[I][COLOR %s] (proxies)[/COLOR][/I]' % color_list_proxies
                else: color = color_list_proxies

        if 'register' in ch['clusters']:
            cfg_user_channel = 'channel_' + ch['id'] + '_' + ch['id'] +'_username'
            cfg_pass_channel = 'channel_' + ch['id'] + '_' + ch['id'] +'_password'
            if not config.get_setting(cfg_user_channel, default='') or not config.get_setting(cfg_pass_channel, default=''):
               titulo += '[I][COLOR teal] (cuenta)[/COLOR][/I]'
            else:
               cfg_login_channel = 'channel_' + ch['id'] + '_' + ch['id'] +'_login'

               if config.get_setting(cfg_login_channel, default=False):
                   presentar = True
                   if 'dominios' in ch['notes'].lower():
                       cfg_dominio_channel = 'channel_' + ch['id'] + '_dominio'
                       if not config.get_setting(cfg_dominio_channel, default=''): presentar = False

                   if presentar: titulo += '[I][COLOR teal] (sesion)[/COLOR][/I]'

        if 'inestable' in ch['clusters']: titulo += '[I][COLOR plum] (inestable)[/COLOR][/I]'

        i =+ 1

        itemlist.append(Item( channel=ch['id'], action=accion, title=titulo, context=context, text_color=color, plot = plot,
                              thumbnail=ch['thumbnail'], category=ch['name'] ))

    if len(ch_list) == 0 or i == 0:
        if item.extra == 'disableds':
            itemlist.append(Item( channel='filters', action='channels_status', title='[B]Opción Sin canales Desactivados[/B]', text_color=color_list_inactive,
                                  des_rea=True, thumbnail=config.get_thumb('stack'), folder=False ))
        else:
            itemlist.append(Item( channel='filters', action='channels_status', title='[B]Opción Sin canales Preferidos[/B]', text_color=color_list_prefe,
                                  des_rea=False, thumbnail=config.get_thumb('stack'), folder=False ))

    return itemlist


def idioma_canal(lang):
    idiomas = { 'cast': 'Castellano', 'lat': 'Latino', 'eng': 'Inglés', 'pt': 'Portugués', 'vo': 'VO', 'vose': 'Vose', 'vos': 'Vos', 'cat': 'Català' }
    return idiomas[lang] if lang in idiomas else lang


def _marcar_canal(item):
    from modules import submnuctext
    submnuctext._marcar_canal(item)
    return True

def _refresh_menu(item):
    from modules import submnuctext
    submnuctext._refresh_menu(item)
    return True

def _quitar_proxies(item):
    from modules import submnuctext
    submnuctext._quitar_proxies(item)
    return True

def _dominio_vigente(item):
    if item.from_channel == 'hdfull':
        from modules import actions

        item.desde_el_canal = True
        actions.last_domain_hdfull(item)

    elif item.from_channel == 'dontorrents':
        from modules import actions

        actions.last_domain_dontorrents(item)

    return True

def _dominio_memorizado(item):
    if item.from_channel == 'hdfull':
        from modules import actions

        actions.manto_domain_hdfull(item)

    elif item.from_channel == 'dontorrents':
        from modules import actions

        actions.manto_domain_dontorrents(item)

    return True

def _dominios(item):
    from modules import submnuctext
    submnuctext._dominios(item)
    return True

def _credenciales(item):
    if item.from_channel == 'hdfull':
        from modules import submnuctext
        submnuctext._credenciales_hdfull(item)

    elif item.from_channel == 'playdede':
        from modules import submnuctext
        submnuctext._credenciales_playdede(item)

    return True

def _proxies(item):
    from modules import submnuctext
    submnuctext._proxies(item)
    return True

def _tests(item):
    from modules import submnuctext
    submnuctext._test_webs(item)
    return True

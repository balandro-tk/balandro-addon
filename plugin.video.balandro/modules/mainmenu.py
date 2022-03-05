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


def mainlist(item):
    logger.info()
    item.category = config.__addon_name

    itemlist = []

    if config.get_setting('developer_mode', default=False):
        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'developer.py')):
            itemlist.append(Item( channel='developer', action='mainlist', title='Gestión opción géneros',
                                  thumbnail=config.get_thumb('genres'), text_color='crimson' ))

        if os.path.exists(os.path.join(config.get_runtime_path(), 'modules', 'test.py')):
            itemlist.append(Item( channel='test', action='mainlist', title='Tests canales y servidores',
                                  thumbnail=config.get_thumb('tools'), text_color='goldenrod' ))

    if current_month == 5:
        itemlist.append(Item( channel='filmaffinitylists', action='_oscars', title='Premios Oscar ' + str(current_year), text_color='pink',
                              thumbnail=config.get_thumb('oscars'), plot = 'Las películas nominadas a los premios Oscars' ))

    elif current_month == 10:
        itemlist.append(Item( channel='filmaffinitylists', action='_emmys', title='Premios Emmy ' + str(current_year), text_color='pink',
                              thumbnail=config.get_thumb('emmys'), plot = 'Las Series nominadas a los premios Emmy' ))

    elif current_month == 11:
         itemlist.append(Item( channel='tmdblists', action='descubre', title='Halloween', text_color='pink', extra = 27, search_type = 'movie',
                               thumbnail=config.get_thumb('halloween'), plot = 'Películas del género Terror' ))

    else:
        if not config.get_setting('mnu_simple', default=False):
            if config.get_setting('sub_mnu_special', default=True):
                itemlist.append(item.clone( action='submnu_special', title='Especiales', extra='all', thumbnail=config.get_thumb('heart'), text_color='pink' ))

    context = []
    tit = '[COLOR %s]Global configurar proxies a usar[/COLOR]' % color_list_proxies
    context.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

    if config.get_setting('proxysearch_excludes', default=''):
        tit = '[COLOR %s]Anular canales excluidos en Global ...[/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

    tit = '[COLOR %s]Información búsquedas[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

    tit = '[COLOR %s]Ajustes categoría buscar[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    itemlist.append(Item( channel='search', action='mainlist', title='Buscar', context=context, thumbnail=config.get_thumb('search'), text_color='yellow' ))

    context = []
    tit = '[COLOR %s]Ajustes categoría canales[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if config.get_setting('mnu_simple', default=False):
        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( action='submnu_special', title='Especiales', extra='all', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        if config.get_setting('mnu_sugeridos', default=True):
            itemlist.append(item.clone( action='channels', extra='suggested', title='Sugeridos', context=context, thumbnail=config.get_thumb('stack'),
                                       text_color='aquamarine' ))

        if config.get_setting('channels_link_main', default=True):
            itemlist.append(item.clone( action='channels', extra='all', title='Canales', context=context, thumbnail=config.get_thumb('stack'),
                                        text_color='gold' ))

        if config.get_setting('mnu_idiomas', default=True):
            itemlist.append(Item( channel='groups', action='mainlist', mnu_lang='idiomas', title='Idiomas', thumbnail=config.get_thumb('idiomas'),
                                  text_color='limegreen' ))

        if config.get_setting('mnu_grupos', default=True):
            itemlist.append(Item( channel='groups', action='mainlist', extra='groups', title='Grupos', thumbnail=config.get_thumb('bookshelf'),
                                  text_color='magenta' ))

    else:
       if config.get_setting('mnu_sugeridos', default=True):
           itemlist.append(item.clone( action='channels', extra='suggested', title='Sugeridos', context=context, thumbnail=config.get_thumb('stack'),
                                       text_color='aquamarine' ))

       if config.get_setting('channels_link_main', default=True):
           itemlist.append(item.clone( action='channels', extra='all', title='Canales', context=context, thumbnail=config.get_thumb('stack'),
                                  text_color='gold' ))

       if config.get_setting('mnu_idiomas', default=True):
           itemlist.append(Item( channel='groups', action='mainlist', mnu_lang='idiomas', title='Idiomas', thumbnail=config.get_thumb('idiomas'),
                                  text_color='limegreen' ))

       if config.get_setting('mnu_grupos', default=True):
           itemlist.append(Item( channel='groups', action='mainlist', extra='groups', title='Grupos', thumbnail=config.get_thumb('bookshelf'),
                                  text_color='magenta' ))

       if config.get_setting('mnu_pelis', default=True):
           itemlist.append(item.clone( action='channels', extra='movies', title='Películas', thumbnail=config.get_thumb('movie'),
                                  text_color='deepskyblue' ))

       if config.get_setting('mnu_series', default=True):
           itemlist.append(item.clone( action='channels', extra='tvshows', title='Series', thumbnail=config.get_thumb('tvshow'),
                                  text_color='hotpink' ))

       if config.get_setting('channels_link_pyse', default=False):
          itemlist.append(item.clone( action='channels', extra='mixed', title='Películas y Series', context=context, thumbnail=config.get_thumb('booklet'),
                                  text_color='teal' ))

       if config.get_setting('mnu_generos', default=True):
          itemlist.append(item.clone( action='submnu_genres', title= 'Géneros', thumbnail=config.get_thumb('genres'),
                                  text_color='thistle' ))

       if config.get_setting('mnu_documentales', default=True):
           itemlist.append(item.clone( action='channels', extra='documentaries', title='Documentales', thumbnail=config.get_thumb('documentary'),
                                       text_color='cyan' ))

       if config.get_setting('mnu_torrents', default=True):
           itemlist.append(item.clone( action='channels', extra='torrents', title='Torrents', thumbnail=config.get_thumb('torrents'),
                                       text_color='blue' ))

       context = []
       if config.get_setting('adults_password'):
           tit = '[COLOR %s]Eliminar Pin parental[/COLOR]' % color_infor
           context.append({'title': tit, 'channel': 'actions', 'action': 'adults_password_del'})

           tit = '[COLOR %s]Refrescar caché menú[/COLOR]' % color_adver
           context.append({'title': tit, 'channel': item.channel, 'action': '_refresh_menu'})
       else:
           tit = '[COLOR %s]Información parental[/COLOR]' % color_infor
           context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_adults'})

       tit = '[COLOR %s]Ajustes categoría canales[/COLOR]' % color_exec
       context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

       if config.get_setting('mnu_doramas', default=True):
           itemlist.append(item.clone( action='channels', extra='dorama', title='Doramas', context=context, thumbnail=config.get_thumb('computer'),
                                       text_color='firebrick' ))

       if config.get_setting('mnu_animes', default=True):
           if not config.get_setting('descartar_anime', default=True):
               itemlist.append(item.clone( action='channels', extra='anime', title='Animes', context=context, thumbnail=config.get_thumb('anime'),
                                           text_color='springgreen' ))

       if config.get_setting('mnu_adultos', default=True):
           if not config.get_setting('descartar_xxx', default=True):
               itemlist.append(item.clone( action='channels', extra='adults', title='Adultos', context=context, thumbnail=config.get_thumb('adults'),
                                           text_color='orange' ))

       if config.get_setting('mnu_preferidos', default=True):
           context = []
           tit = '[COLOR %s]Información preferidos[/COLOR]' % color_infor
           context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_tracking'})

           tit = '[COLOR %s]Ajustes categoría preferidos[/COLOR]' % color_exec
           context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

           itemlist.append(Item( channel='tracking', action='mainlist', title='Preferidos', context=context, thumbnail=config.get_thumb('videolibrary'),
                                           text_color='wheat' ))

       if config.get_setting('mnu_desargas', default=True):
           context = []
           tit = '[COLOR %s]Ajustes categoría descargas[/COLOR]' % color_exec
           context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

           itemlist.append(Item( channel='downloads', action='mainlist', title='Descargas', context=context, thumbnail=config.get_thumb('downloads'),
                                           text_color='seagreen' ))

    context = []
    tit = '[COLOR %s]Información versión[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_version'})

    tit = '[COLOR %s]Comprobar actualizaciones Fix[/COLOR]' % color_avis
    context.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates'})

    tit = '[COLOR %s]Forzar actualizaciones Fix[/COLOR]' % color_adver
    context.append({'title': tit, 'channel': 'actions', 'action': 'check_addon_updates_force'})

    tit = '[COLOR %s]Test del sistema[/COLOR]' % color_alert
    context.append({'title': tit, 'channel': 'helper', 'action': 'show_test'})

    tit = '[COLOR %s]Ajustes configuración[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    try:
        last_ver = updater.check_addon_version()
    except: last_ver = True

    if not last_ver: last_ver = '[I][COLOR %s](desfasada)[/COLOR][/I]' % color_adver
    else: last_ver = ''

    title = 'Ayuda (%s)  %s' % (config.get_addon_version(), last_ver)

    itemlist.append(Item( channel='helper', action='mainlist', title=title, context=context, thumbnail=config.get_thumb('help'), text_color='chartreuse' ))

    itemlist.append(Item( channel='actions', action='open_settings', title='Configuración', folder=False, thumbnail=config.get_thumb('settings'),
                          text_color='chocolate' ))

    return itemlist


def channels(item):
    logger.info()
    itemlist = []

    thumb_filmaffinity = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'filmaffinity.jpg')
    thumb_tmdb = os.path.join(config.get_runtime_path(), 'resources', 'media', 'channels', 'thumb', 'tmdb.jpg')

    context = []
    tit = '[COLOR %s]Global configurar proxies a usar[/COLOR]' % color_list_proxies
    context.append({'title': tit, 'channel': 'proxysearch', 'action': 'proxysearch_all'})

    if config.get_setting('proxysearch_excludes', default=''):
        tit = '[COLOR %s]Anular canales excluidos en Global ...[/COLOR]' % color_list_proxies
        context.append({'title': tit, 'channel': 'proxysearch', 'action': 'channels_proxysearch_del'})

    tit = '[COLOR %s]Información búsquedas[/COLOR]' % color_infor
    context.append({'title': tit, 'channel': 'search', 'action': 'show_help'})

    tit = '[COLOR %s]Ajustes categoría buscar[/COLOR]' % color_exec
    context.append({'title': tit, 'channel': 'actions', 'action': 'open_settings'})

    if item.extra == 'movies':
        itemlist.append(item.clone( action='submnu_search', title='Personalizar búsquedas',
                                    extra = 'movies', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='movie', title='Buscar Película ...',
                              extra = 'movies', context=context, thumbnail=config.get_thumb('search'), text_color='deepskyblue' ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='movie', title='Búsquedas y listas en TMDB',
                                  thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='movie', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( action='submnu_special', title='Especiales', extra='movies', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Películas'
        accion = 'mainlist_pelis'
        filtros = {'categories': 'movie'}

    elif item.extra == 'tvshows':
        itemlist.append(item.clone( action='submnu_search', title='Personalizar búsquedas',
                                    extra = 'tvshows', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='tvshow', title='Buscar Serie ...',
                              extra = 'tvshows', context=context, thumbnail=config.get_thumb('search'), text_color='hotpink' ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='tvshow', title='Búsquedas y listas en TMDB',
                                  thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='tvshow', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( action='submnu_special', title='Especiales', extra='tvshows', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Series'
        accion = 'mainlist_series'
        filtros = {'categories': 'tvshow'}

    elif item.extra == 'documentaries':
        itemlist.append(item.clone( action='submnu_search', title='Personalizar búsquedas',
                                    extra = 'documentaries', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='documentary', title='Buscar Documental ...',
                              extra = 'documentaries', context=context, thumbnail=config.get_thumb('search'), text_color='cyan' ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='documentary', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( action='submnu_special', title='Especiales', extra='documentaries',
                                        thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Documentales'
        accion = 'mainlist'
        filtros = {'categories': 'documentary', 'searchable': True}

    elif item.extra == 'mixed':
        itemlist.append(item.clone( action='submnu_search', title='Personalizar búsquedas',
                                    extra = 'mixed', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='all', title='Buscar Película y/o Serie ...',
                              extra = 'mixed', context=context, thumbnail=config.get_thumb('search'), text_color='yellow' ))

        if config.get_setting('search_extra_main', default=True):
            itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='Búsquedas y listas en TMDB',
	                              thumbnail=thumb_tmdb, text_color=color_adver ))

            itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='Listas en Filmaffinity',
                                  thumbnail=thumb_filmaffinity, text_color=color_adver ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( action='submnu_special', title='Especiales', extra='all', thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con Películas y Series'
        accion = 'mainlist'
        filtros = {}

    elif item.extra == 'torrents':
        itemlist.append(item.clone( action='submnu_search', title='Personalizar búsquedas',
                                    extra = 'torrents', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

        itemlist.append(Item( channel='search', action='search', search_type='all', title='[COLOR blue]Buscar Torrent[/COLOR] película y/o Serie ...',
                              extra = 'only_torrents', context=context, thumbnail=config.get_thumb('search'), text_color='yellow' ))

        if config.get_setting('sub_mnu_special', default=True):
            itemlist.append(item.clone( action='submnu_special', title='Especiales', extra='torrents',
                                        thumbnail=config.get_thumb('heart'), text_color='pink' ))

        item.category = 'Canales con archivos Torrents'
        accion = 'mainlist'
        filtros = {'categories': 'torrent'}

    else:
        if item.extra == 'adults': pass
        elif item.extra == 'anime': pass
        elif item.extra == 'dorama': pass
        elif not item.extra == 'groups':

            itemlist.append(item.clone( action='submnu_search', title='Personalizar búsquedas',
                                    extra = 'all', thumbnail=config.get_thumb('settings'), text_color='moccasin' ))

            itemlist.append(Item( channel='search', action='search', search_type='all', title='Buscar Película y/o Serie ...', context=context,
                                  thumbnail=config.get_thumb('search'), text_color='yellow' ))

            itemlist.append(Item( channel='search', action='search', search_type='documentary', title='Buscar Documental ...', context=context,
	                              thumbnail=config.get_thumb('search'), text_color='cyan' ))

            if config.get_setting('search_extra_main', default=True):
                itemlist.append(Item( channel='tmdblists', action='mainlist', search_type='all', title='Búsquedas y listas en TMDB',
                                thumbnail=thumb_tmdb, text_color=color_adver ))

                itemlist.append(Item( channel='filmaffinitylists', action='mainlist', search_type='all', title='Listas en Filmaffinity',
                                      thumbnail=thumb_filmaffinity, text_color=color_adver ))

            if config.get_setting('sub_mnu_special', default=True):
                itemlist.append(item.clone( action='submnu_special', title='Especiales', extra='all',
                                            thumbnail=config.get_thumb('heart'), text_color='pink' ))

        if item.extra == 'adults':
            item.category = 'Canales exclusivos para Adultos'
        elif item.extra == 'anime':
            item.category = 'Canales exclusivos de Animes'
        elif item.extra == 'dorama':
            item.category = 'Canales exclusivos de Doramas'
        elif item.extra == 'suggested':
            item.category = 'Canales Sugeridos'
        elif not item.extra == 'groups':
            item.category = 'Todos los Canales'
        else:
            item.category = 'Canales con Agrupaciones'

        if item.extra == 'adults' or item.extra == 'anime':
            if not config.get_setting('adults_password'):
                itemlist.append(Item( channel='helper', action='show_help_adults', title='Información parental',
                                      thumbnail=config.get_thumb('help'), text_color='green' ))

        accion = 'mainlist'
        filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        if item.extra == 'movies':
            if ch['searchable'] == False:
                if 'adults' in ch['clusters']: continue
                elif 'anime' in ch['clusters']: continue
                elif 'dorama' in ch['clusters']: continue

        elif item.extra == 'tvshows':
            if ch['searchable'] == False:
                if 'adults' in ch['clusters']: continue
                elif 'anime' in ch['clusters']: continue
                elif 'dorama' in ch['clusters']: continue

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

        elif item.extra == 'dorama':
            if ch['searchable'] == True: continue
            if not 'dorama' in ch['clusters']: continue

        else:
           if config.get_setting('mnu_simple', default=False):
               if ch['searchable'] == False:
                   if 'adults' in ch['clusters']: continue
                   elif 'anime' in ch['clusters']: continue
                   elif 'dorama' in ch['clusters']: continue

           else:
              if not config.get_setting('mnu_doramas', default=True):
                  if 'dorama' in ch['clusters']: continue

              if not config.get_setting('mnu_animes', default=True):
                  if 'anime' in ch['clusters']: continue

              if not config.get_setting('mnu_adultos', default=True):
                  if 'adults' in ch['clusters']: continue

        context = []

        cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

        if 'proxies' in ch['notes'].lower():
            if config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s]Quitar los proxies del canal[/COLOR]' % color_list_proxies
                context.append({'title': tit, 'channel': item.channel, 'action': '_quitar_proxies'})

        if ch['status'] != 1:
            tit = '[COLOR %s]Marcar canal como Preferido[/COLOR]' % color_list_prefe
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 1})

        if ch['status'] != 0:
            if ch['status'] == 1:
                tit = '[COLOR %s]Des-Marcar canal como Preferido[/COLOR]' % color_list_prefe
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            elif ch['status'] == -1:
                tit = '[COLOR %s]Des-Marcar canal como Desactivado[/COLOR]' % color_list_inactive
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})
            else:
                tit = '[COLOR white]Marcar canal como Activo[/COLOR]'
                context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': 0})

        if ch['status'] != -1:
            tit = '[COLOR %s]Marcar canal como Desactivado[/COLOR]' % color_list_inactive
            context.append({'title': tit, 'channel': item.channel, 'action': '_marcar_canal', 'estado': -1})

        if 'dominios' in ch['notes'].lower():
            tit = '[COLOR yellowgreen]Dominio vigente[/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominio_vigente'})

            tit = '[COLOR %s]Configurar dominio a usar[/COLOR]' % color_adver
            context.append({'title': tit, 'channel': item.channel, 'action': '_dominios'})

        if 'register' in ch['clusters']:
            tit = '[COLOR green]Información para registrarse[/COLOR]'
            context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_register'})

            tit = '[COLOR teal]Credenciales Cuenta[/COLOR]'
            context.append({'title': tit, 'channel': item.channel, 'action': '_credenciales'})

        if 'proxies' in ch['notes'].lower():
            if not config.get_setting(cfg_proxies_channel, default=''):
                tit = '[COLOR %s]Información proxies[/COLOR]' % color_infor
                context.append({'title': tit, 'channel': 'helper', 'action': 'show_help_proxies'})

            tit = '[COLOR %s]Configurar proxies a usar[/COLOR]' % color_list_proxies
            context.append({'title': tit, 'channel': item.channel, 'action': '_proxies'})

            tit = '[COLOR %s]Refrescar caché menú[/COLOR]' % color_exec
            context.append({'title': tit, 'channel': item.channel, 'action': '_refresh_menu'})

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
               if not config.get_setting(cfg_login_channel, default=False): titulo += '[I][COLOR teal] (sesion)[/COLOR][/I]'

        if 'inestable' in ch['clusters']: titulo += '[I][COLOR plum] (inestable)[/COLOR][/I]'

        i =+ 1

        itemlist.append(Item( channel=ch['id'], action=accion, title=titulo, context=context, text_color=color, plot = plot,
                              thumbnail=ch['thumbnail'], category=ch['name'] ))

    if len(ch_list) == 0 or i == 0:
        itemlist.append(Item( channel='filters', action='channels_status', title='Opción Sin Canales Preferidos', text_color=color_list_prefe,
                              des_rea=False, thumbnail=config.get_thumb('stack'), folder=False ))

    return itemlist


def submnu_genres(item):
    logger.info()
    itemlist = []

    itemlist.append(Item( channel='generos', action='mainlist', title='Géneros', thumbnail=config.get_thumb('genres'), text_color='moccasin' ))

    itemlist.append(item.clone( action='', title= 'Canales que pueden necesitar proxies nuevamente:', text_color='red', folder=False ))

    itemlist.append(item.clone( channel='groups', action='ch_generos', title=' - Canales con películas', group = 'generos', extra = 'movies',
                                thumbnail=config.get_thumb('movie'), text_color='deepskyblue' ))

    itemlist.append(item.clone( channel='groups', action='ch_generos', title=' - Canales con series', group = 'generos', extra = 'tvshows',
                                thumbnail=config.get_thumb('tvshow'), text_color='hotpink' ))

    return itemlist


def submnu_search(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title= 'Búsquedas en canales con proxies:', text_color='red', folder=False ))

    itemlist.append(item.clone( channel='filters', title=' - Qué canales pueden usar proxies', action='with_proxies',
                                thumbnail=config.get_thumb('stack'), new_proxies=True, folder=False ))

    itemlist.append(item.clone( channel='proxysearch', title=' - Configurar proxies a usar [COLOR plum](en los canales que los necesiten)[/COLOR]',
                                action='proxysearch_all', thumbnail=config.get_thumb('flame') ))

    if config.get_setting('memorize_channels_proxies', default=True):
        itemlist.append(item.clone( channel='filters', title=  ' - Qué [COLOR red]canales[/COLOR] tiene con proxies memorizados', action='with_proxies',
                                    thumbnail=config.get_thumb('stack'), new_proxies=True, memo_proxies=True, test_proxies=True, folder=False ))

    itemlist.append(item.clone( channel='actions', title= ' - Quitar los proxies en los canales [COLOR red](que los tengan memorizados)[/COLOR]',
                                action = 'manto_proxies', folder=False, thumbnail=config.get_thumb('flame') ))

    itemlist.append(item.clone( channel='helper', action='show_help_proxies', title= ' - [COLOR green]Información uso de proxies[/COLOR]', folder=False ))

    if config.get_setting('proxysearch_excludes', default=''):
        itemlist.append(item.clone( channel='proxysearch', title=' - Anular los canales excluidos de Configurar proxies a usar',
                                    action='channels_proxysearch_del', thumbnail=config.get_thumb('flame'), text_color='coral', folder=False ))

    itemlist.append(item.clone( action='', title= 'Personalizacion búsquedas:', text_color='moccasin', folder=False ))

    itemlist.append(item.clone( channel='search', action='show_help_parameters', title='[COLOR chocolate] - Qué ajustes tiene configurados para las búsquedas[/COLOR]',
                                thumbnail=config.get_thumb('help'), folder=False ))

    itemlist.append(item.clone( channel='filters', action='no_actives', title=' - Qué canales no intervienen en las búsquedas (están desactivados)',
                                thumbnail=config.get_thumb('stack'), folder=False ))

    itemlist.append(item.clone( channel='filters', action='channels_status', title=' - Personalizar canales (Desactivar o Re-activar)',
                                des_rea=True, thumbnail=config.get_thumb('stack'), folder=False ))

    itemlist.append(item.clone( channel='filters', action='only_prefered', title=' - Qué canales tiene marcados como preferidos',
                                thumbnail=config.get_thumb('stack'), folder=False ))

    itemlist.append(item.clone( channel='filters', action='channels_status', title=' - Personalizar canales Preferidos (Marcar o Des-marcar)',
                                des_rea=False, thumbnail=config.get_thumb('stack'), folder=False ))

    if item.extra == 'movies':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR cyan]Excluir canales en las búsquedas de películas[/COLOR]',
                                    extra='movies', thumbnail=config.get_thumb('stack'), folder=False ))

        if channels_search_excluded_movies:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral]Anular los canales excluidos en las búsquedas de películas[/COLOR]',
                                        extra='movies', folder=False ))

    elif item.extra == 'tvshows':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR cyan]Excluir canales en las búsquedas de series[/COLOR]',
                                    extra='tvshows', thumbnail=config.get_thumb('stack'), folder=False ))

        if channels_search_excluded_tvshows:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral]Anular los canales excluidos en las búsquedas de series[/COLOR]',
                                        extra='tvshows', folder=False ))

    elif item.extra == 'documentaries':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR cyan]Excluir canales en las búsquedas de documentales[/COLOR]',
                                    extra='documentaries', thumbnail=config.get_thumb('stack'), folder=False ))

        if channels_search_excluded_documentaries:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral]Anular los canales excluidos en las búsquedas de documentales[/COLOR]',
                                        extra='documentaries', folder=False ))

    elif item.extra == 'torrents':
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR cyan]Excluir canales Torrent en las búsquedas para Películas y/o Series[/COLOR]',
                                    extra='torrents', thumbnail=config.get_thumb('stack'), folder=False ))

        if channels_search_excluded_mixed:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral]Anular los canales Torrent excluidos en las búsquedas para Películas y/o Series[/COLOR]',
                                        extra='torrents', folder=False ))

    else:
        itemlist.append(item.clone( channel='filters', action='channels_excluded', title=' - [COLOR cyan]Excluir canales en las búsquedas de Películas, Series y Documentales[/COLOR]',
                                    extra='all', thumbnail=config.get_thumb('stack'), folder=False ))

        if channels_search_excluded_all:
            itemlist.append(item.clone( channel='filters', action='channels_excluded_del', title=' - [COLOR coral]Anular los canales excluidos en las búsquedas de Películas, Series y Documentales[/COLOR]',
                                        extra='all', folder=False ))

    itemlist.append(item.clone( channel='actions', title='Ajustes categorías [COLOR yellowgreen](proxies y buscar)[/COLOR]', action = 'open_settings',
                                thumbnail=config.get_thumb('settings'), folder=False ))

    itemlist.append(item.clone( channel='search', action='show_help', title='[COLOR green]Información búsquedas[/COLOR]',
                                thumbnail=config.get_thumb('help'), folder=False ))

    return itemlist


def submnu_special(item):
    logger.info()
    itemlist = []

    if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'movies':
        itemlist.append(item.clone( title = '[COLOR deepskyblue]Películas[COLOR goldenrod] Recomendadas[/COLOR]', thumbnail=config.get_thumb('movie'), action = '' ))

        itemlist.append(Item( channel='clubcine', action='_besthistoria', title=' - Las mejores de la historia', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='clubcine', action='_bestcinespa', title=' - Las mejores del cine español', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='clubcine', action='_bestcinenegro', title=' - Las mejores del cine negro', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='clubcine', action='_bestcinedesiempre', title=' - Las mejores del cine de siempre', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='adnstream', action='_ayer_y_siempre', title=' - Las mejores del cine de ayer y siempre', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='zoowomaniacos', action='_culto', title=' - Las mejores del cine de culto', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='zoowomaniacos', action='_las1001', title=' - Las 1001 que hay que ver', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(item.clone( title='[COLOR deepskyblue]Películas[/COLOR] búsquedas a través de listas', thumbnail=config.get_thumb('movie'), action = '', text_color='pink' ))

        itemlist.append(Item( channel='tmdblists', action='listado', title= ' - En cartelera', extra='now_playing', thumbnail=config.get_thumb('movie'), search_type = 'movie' ))

        if not current_month == 5:
            itemlist.append(Item( channel='filmaffinitylists', action='_oscars', title=' - Premios Oscar', thumbnail=config.get_thumb('oscars'), search_type = 'movie' ))

        itemlist.append(Item( channel='filmaffinitylists', action='_sagas', title=' - Sagas y colecciones', thumbnail=config.get_thumb('bestsagas'), search_type = 'movie' ))

        itemlist.append(Item( channel='tmdblists', action='listado', title= ' - Más populares', extra='popular', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='tmdblists', action='listado', title= ' - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='filmaffinitylists', action='_bestmovies', title=' - Recomendadas', thumbnail=config.get_thumb('bestmovies'), search_type = 'movie' ))

        itemlist.append(Item( channel='tmdblists', action='networks', title=' - Por productora', thumbnail=config.get_thumb('movie'), search_type = 'movie' ))

        itemlist.append(Item( channel='tmdblists', action='generos', title=' - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'movie' ))

        itemlist.append(Item( channel='tmdblists', action='anios', title=' - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'movie' ))

    if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'tvshows':
        itemlist.append(item.clone( title = '[COLOR hotpink]Series[/COLOR] búsquedas a través de listas', thumbnail=config.get_thumb('tvshow'), action = '', text_color='pink' ))

        itemlist.append(Item( channel='tmdblists', action='listado', title= ' - En emisión', extra='on_the_air', thumbnail=config.get_thumb('tvshow'), search_type = 'tvshow' ))

        if not current_month == 10:
            itemlist.append(Item( channel='filmaffinitylists', action='_emmys', title=' - Premios Emmy', thumbnail=config.get_thumb('emmys'),
                                  origen='mnu_esp', search_type = 'tvshow' ))

        itemlist.append(Item( channel='tmdblists', action='listado', title= ' - Más populares', extra='popular', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

        itemlist.append(Item( channel='tmdblists', action='listado', title= ' - Más valoradas', extra='top_rated', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

        itemlist.append(Item( channel='filmaffinitylists', action='_besttvshows', title=' - Recomendadas', thumbnail=config.get_thumb('besttvshows'), search_type = 'tvshow' ))

        itemlist.append(Item( channel='tmdblists', action='generos', title=' - Por género', thumbnail=config.get_thumb('listgenres'), search_type = 'tvshow' ))

        itemlist.append(Item( channel='tmdblists', action='anios', title=' - Por año', thumbnail=config.get_thumb('listyears'), search_type = 'tvshow' ))

    if item.extra == 'all' or item.extra == 'mixed' or item.extra == 'documentaries':
        itemlist.append(item.clone( title = '[COLOR cyan]Documentales[/COLOR] búsquedas a través de listas', thumbnail=config.get_thumb('documentary'), action = '', text_color='pink' ))

        itemlist.append(Item( channel='filmaffinitylists', action='_bestdocumentaries', title=' - Los Mejores', thumbnail=config.get_thumb('bestdocumentaries'), search_type = 'all' ))

    itemlist.append(item.clone( title = '[COLOR yellow]Películas y Series[/COLOR] búsquedas a través de listas', thumbnail=config.get_thumb('heart'), action = '', text_color='pink' ))

    itemlist.append(Item( channel='filmaffinitylists', action='plataformas', title=' - Películas y series por plataforma', thumbnail=config.get_thumb('heart'), search_type = 'all' ))

    itemlist.append(Item( channel='filmaffinitylists', action='_genres', title=' - Películas y series por género', thumbnail=config.get_thumb('listgenres'), search_type = 'all' ))

    itemlist.append(Item( channel='filmaffinitylists', action='_years', title=' - Películas y series por año', thumbnail=config.get_thumb('listyears'), search_type = 'all' ))

    itemlist.append(Item( channel='filmaffinitylists', action='_themes', title=' - Películas y series por tema', thumbnail=config.get_thumb('listthemes'), search_type = 'all' ))

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

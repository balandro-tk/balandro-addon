# -*- coding: utf-8 -*-

from platformcode import config, logger
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


def mainlist(item):
    logger.info()
    itemlist = []

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

    itemlist.append(item.clone( action='submnu_search', title= 'Personalizar búsquedas',
                                thumbnail=config.get_thumb('settings'), text_color='moccasin', extra = 'all' ))

    if not item.mnu_lang:
        itemlist.append(Item( channel='search', action='mainlist', title='Buscar', context=context, thumbnail=config.get_thumb('search'), text_color='yellow' ))

        item.category = 'Agrupaciones de Canales'

        itemlist.append(item.clone( title = 'Novedades:', thumbnail=config.get_thumb('heart'), action = '', text_color='yellowgreen' ))

        if config.get_setting('mnu_pelis', default=True):
            itemlist.append(item.clone( title = ' - Canales de [COLOR deepskyblue]Películas[/COLOR] con Estrenos y/ó Novedades',
                                        thumbnail=config.get_thumb('movie'), action = 'ch_groups', group = 'news', extra = 'movies', ))

        if config.get_setting('mnu_series', default=True):
            itemlist.append(item.clone( title = ' - Canales de [COLOR hotpink]Series[/COLOR] con Episodios Nuevos y/ó Últimos',
                                        thumbnail=config.get_thumb('tvshow'), action = 'ch_groups', group = 'lasts', extra = 'tvshows' ))

        itemlist.append(item.clone( title = 'Películas, Series y/ó Documentales:', action = '', thumbnail=config.get_thumb('booklet'), text_color='pink' ))
        itemlist.append(item.clone( title = ' - Canales con temática Clásica', action = 'ch_groups', group = 'classic', extra = 'all' ))
        itemlist.append(item.clone( title = ' - Canales con temática Infantil', action = 'ch_groups', group = 'kids', extra = 'all' ))

        if config.get_setting('mnu_torrents', default=True):
            itemlist.append(item.clone( title = ' - Canales que pueden contener enlaces Torrents', thumbnail=config.get_thumb('torrents'),
                                        action = 'ch_groups', group = 'torrents', extra = 'torrents' ))

        itemlist.append(item.clone( title = ' - Canales con Rankings (Más vistas, Más valoradas, etc.)', action = 'ch_groups', group = 'rankings', extra = 'all' ))

        if config.get_setting('mnu_idiomas', default=True):
            itemlist.append(item.clone( title = ' - Canales con Vídeos en Versión Original y/ó Subtitulada', action = 'ch_groups', group = 'vos', extra = 'all' ))

        itemlist.append(item.clone( title = ' - Canales con Vídeos en 3D', action = 'ch_groups', group = '3d', extra = 'all' ))

        if config.get_setting('mnu_pelis', default=True):
            itemlist.append(item.clone( title = 'Películas:', action = '', thumbnail=config.get_thumb('movie'), text_color='deepskyblue' ))

            if config.get_setting('mnu_generos', default=True):
                 itemlist.append(item.clone( title = ' - Canales con Géneros', action = 'ch_groups', group = 'genres', extra = 'movies' ))

            itemlist.append(item.clone( title = ' - Canales con Idiomas', action = 'ch_groups', group = 'languages', extra = 'movies' ))
            itemlist.append(item.clone( title = ' - Canales con Años', action = 'ch_groups', group = 'years', extra = 'movies' ))
            itemlist.append(item.clone( title = ' - Canales con Épocas', action = 'ch_groups', group = 'epochs', extra = 'movies' ))
            itemlist.append(item.clone( title = ' - Canales con Calidades', action = 'ch_groups', group = 'qualityes', extra = 'movies' ))

        if config.get_setting('mnu_series', default=True):
            itemlist.append(item.clone( title = 'Series:', action = '', thumbnail=config.get_thumb('tvshow'), text_color='hotpink' ))

            if config.get_setting('mnu_generos', default=True):
                itemlist.append(item.clone( title = ' - Canales con Géneros', action = 'ch_groups', group = 'genres', extra = 'tvshows' ))

            itemlist.append(item.clone( title = ' - Canales con Novelas', action = 'ch_groups', group = 'tales', extra = 'tvshows' ))

        presentar = True
        if not config.get_setting('mnu_pelis', default=True): presentar = False
        if not config.get_setting('mnu_series', default=True): presentar = False

        if presentar:
            itemlist.append(item.clone( title = 'Películas ó Series:', action = '', thumbnail=config.get_thumb('booklet'), text_color='salmon' ))
            itemlist.append(item.clone( title = ' - Canales con Países', action = 'ch_groups', group = 'countries', extra = 'movies' ))

        if config.get_setting('mnu_documentales', default=True):
            itemlist.append(item.clone( title = 'Documentales:', action = '', thumbnail=config.get_thumb('documentary'), text_color='cyan' ))
            itemlist.append(item.clone( title = ' - Canales con temática [COLOR cyan]Documental[/COLOR]', action = 'ch_groups', group = 'docs' ))

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

        presentar = True
        if config.get_setting('mnu_simple', default=False): presentar = False

        if presentar:
            if config.get_setting('mnu_doramas', default=True):
                itemlist.append(item.clone( title = 'Doramas:', action = '', thumbnail=config.get_thumb('computer'), text_color='firebrick' ))
                itemlist.append(item.clone( title = ' - Canales con contenido [COLOR firebrick]Dorama[/COLOR]', action = 'ch_groups', group = 'dorama', context=context ))

        presentar = True
        descartar_xxx = config.get_setting('descartar_xxx', default=False)

        if config.get_setting('mnu_simple', default=False): presentar = False
        else:
           if descartar_xxx:
               if descartar_anime: presentar = False

        if presentar:
            if not config.get_setting('descartar_anime', default=True):
                itemlist.append(item.clone( title = 'Animes:', action = '', thumbnail=config.get_thumb('anime'), text_color='springgreen' ))
                itemlist.append(item.clone( title = ' - Canales con contenido [COLOR springgreen]Anime[/COLOR]', action = 'ch_groups', group = 'anime', context=context ))

            if not descartar_xxx:
                itemlist.append(item.clone( title = 'Adultos (+18):', action = '', thumbnail=config.get_thumb('adults'), text_color='orange' ))
                itemlist.append(item.clone( title = ' - Canales que pueden contener temática para [COLOR orange]Adultos[/COLOR]', action = 'ch_groups', group = 'adults', context=context ))

        itemlist.append(item.clone( title = 'Diversos:', action = '', thumbnail=config.get_thumb('crossroads'), text_color='fuchsia' ))
        itemlist.append(item.clone( title = ' - Canales con Categorias', action = 'ch_groups', group = 'categories', extra = 'mixed' ))
        itemlist.append(item.clone( title = ' - Canales con Intérpretes', action = 'ch_groups', group = 'stars', extra = 'mixed' ))
        itemlist.append(item.clone( title = ' - Canales con Directores/as', action = 'ch_groups', group = 'directors', extra = 'mixed' ))
        itemlist.append(item.clone( title = ' - Canales con Productoras, Plataformas, y/ó Estudios', action = 'ch_groups', group = 'producers', extra = 'mixed' ))
        itemlist.append(item.clone( title = ' - Canales con Listas, Sagas, Colecciones, y/ó Otros', action = 'ch_groups', group = 'lists', extra = 'mixed' ))

    presentar = False
    if item.mnu_lang: presentar = True
    else:
       if config.get_setting('mnu_idiomas', default=True): presentar = True

    if presentar:
        itemlist.append(item.clone( title = 'Audios:', action = '', thumbnail=config.get_thumb('idiomas'), text_color='violet' ))
        itemlist.append(item.clone( title = ' - Canales con Audio Multiple', action = 'ch_groups', group = 'all', extra = 'mixed' ))
        itemlist.append(item.clone( title = ' - Canales con Audio solo en Castellano', action = 'ch_groups', group = 'cast', extra = 'mixed' ))
        itemlist.append(item.clone( title = ' - Canales con Audio solo en Latino', action = 'ch_groups', group = 'lat', extra = 'mixed' ))
        itemlist.append(item.clone( title = ' - Canales con Audio solo en Vose', action = 'ch_groups', group = 'vose', extra = 'mixed' ))
        itemlist.append(item.clone( title = ' - Canales con Audio solo en VO', action = 'ch_groups', group = 'vo', extra = 'mixed' ))

    return itemlist


def ch_groups(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)
    descartar_anime = config.get_setting('descartar_anime', default=False)

    accion = 'mainlist'

    search_type = ''
    if item.group == 'news': accion = 'mainlist_pelis'
    elif item.group == 'lasts': accion = 'mainlist_series'

    elif item.group == 'genres' or item.group == 'generos':
         if item.extra == 'movies': search_type = 'movie'
         else: search_type = 'tvshow'

    elif item.group == 'languages':
         accion = 'idiomas'
         search_type = 'movie'
    elif item.group == 'years':
         accion = 'anios'
         search_type = 'movie'
    elif item.group == 'epochs':
         search_type = 'movie'
    elif item.group == 'countries':
         accion = 'paises'
         search_type = 'movie'
    elif item.group == 'qualityes':
         accion = 'calidades'
         search_type = 'movie'

    elif item.group == 'categories': accion = 'categorias'

    canales = []
    filtros = {}

    channels_list_status = config.get_setting('channels_list_status', default=0)
    if channels_list_status > 0:
        filtros['status'] = 0 if channels_list_status == 1 else 1

    ch_list = channeltools.get_channels_list(filtros=filtros)

    i = 0

    for ch in ch_list:
        try:
           agrupaciones = ch['clusters']
        except:
           continue

        if item.group == 'genres' or item.group == 'generos':
            if not 'géneros' in ch['notes']: continue

            if item.group == 'generos':
                if not 'proxies' in ch['notes'].lower(): continue

            if item.extra == 'movies':
                if not 'movie' in ch['categories']: continue
            elif item.extra == 'tvshows':
                if not 'tvshow' in ch['categories']: continue

            search_types = ch['search_types']

            accion = 'generos'

            if item.group == 'generos': accion = 'mainlist'
            elif 'all' in search_types:
               if search_type == 'tvshow':
                   if not 'Géneros' in ch['notes']: continue
               elif not 'géneros' in ch['notes']: accion = 'mainlist'

        elif item.group == 'cast':
            audios = ch['language']
            if not item.group in audios: continue

            if 'lat' in audios: continue
            elif 'vose' in audios: continue
            elif 'vo' in audios: continue
        elif item.group == 'lat':
            audios = ch['language']
            if not item.group in audios: continue

            if 'cast' in audios: continue
            elif 'vose' in audios: continue
            elif 'vo' in audios: continue
        elif item.group == 'vose':
            audios = ch['language']
            if not item.group in audios: continue

            if 'cast' in audios: continue
            elif 'lat' in audios: continue
            elif 'vo' in audios: continue
        elif item.group == 'vo':
            audios = ch['language']
            if not item.group in audios: continue

            if 'cast' in audios: continue
            elif 'lat' in audios: continue
            elif 'vose' in audios: continue

            if ch['searchable'] == False: # adultos
               if descartar_xxx: continue
        elif item.group == 'all':
            audios = ch['language']
            if len(audios) == 1: continue

        else:
           if not item.group in agrupaciones: continue

        if ch['searchable'] == False: # adultos
            if descartar_xxx:
                if 'adults' in agrupaciones:
                    if item.group == 'news': continue
                    elif item.group == 'rankings': continue
                    elif item.group == 'categories': continue
                    elif item.group == 'stars': continue
                    elif item.group == 'vose': continue
                    elif item.group == 'vo': continue
            elif descartar_anime:
                if 'anime' in agrupaciones:
                   if item.group == 'anime': continue
                   elif item.group == 'vose': continue
                   elif item.group == 'vo': continue

            if not config.get_setting('mnu_doramas', default=True):
                if 'dorama' in ch['clusters']: continue

            if not config.get_setting('mnu_animes', default=True):
                if 'anime' in agrupaciones: continue

            if not config.get_setting('mnu_adultos', default=True):
                if 'adults' in agrupaciones: continue

        action = accion
        if item.group == 'anime':
            if 'anime' in ch['notes'].lower(): action = 'mainlist_anime'
            else:
                 if ch['name'].startswith('Series'): action = 'mainlist_series'
                 else:
                     if ch['name'] == 'Tekilaz': action = 'mainlist_series'
                     else: action = 'mainlist_pelis'

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
        plot += '[' + ', '.join([config.get_localized_category(ct) for ct in ch['categories']]) + '][CR]'
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
                              thumbnail=ch['thumbnail'], category=ch['name'], search_type = search_type, sort = 'C' ))

        if ch['status'] == -1: continue

        canales.append(ch['id'])

    if len(itemlist) == 0 or i == 0:
        itemlist.append(Item( channel='filters', action='channels_status', title='Opción Sin Canales Preferidos', text_color=color_list_prefe,
                              des_rea=False, thumbnail=config.get_thumb('stack'), sort = 'C', folder=False ))

    if itemlist:
        buscar_only_group = True

        if item.group == 'adults': buscar_only_group = False

        if buscar_only_group:
            if len(itemlist) > 1:
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

                itemlist.append(item.clone( action='submnu_search', title= 'Personalizar búsquedas',
                                            extra = item.extra, thumbnail=config.get_thumb('settings'),  sort = 'A', text_color='moccasin' ))

                itemlist.append(Item( channel='search', action='search', search_type='all', title='Buscar solo en los canales de este grupo ...',
                                      context=context, only_channels_group = canales, group = item.group,
                                      thumbnail=config.get_thumb('search'), sort = 'B', text_color='yellowgreen' ))

    return sorted(itemlist, key=lambda it: it.sort)


def submnu_search(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone( action='', title='Búsquedas en canales con proxies:', text_color='red', folder=False ))

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
            itemlist.append(item.clone( channel='filters', action = 'channels_excluded_del', title=' - [COLOR coral]Anular los canales excluidos en las búsquedas de documentales[/COLOR]',
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


def ch_generos(item):
    return ch_groups(item)


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

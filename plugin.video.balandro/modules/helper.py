# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    PY3 = True

    import xbmcvfs
    translatePath = xbmcvfs.translatePath
else:
    PY3 = False

    translatePath = xbmc.translatePath

import os, time, xbmcaddon
import xbmc, xbmcgui, platform

from platformcode import config, logger, platformtools, updater
from core import filetools
from core.item import Item

from modules import filters


ADDON_REPO_ADDONS = 'https://balandro-tk.github.io/balandro/'
ADDON_UPDATES_JSON = 'https://raw.githubusercontent.com/balandro-tk/addon_updates/main/updates.json'

color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


_foro = "[COLOR plum][B][I] mimediacenter.info/foro/viewforum.php?f=44 [/I][/B][/COLOR]"
_source = "[COLOR coral][B][I] balandro-tk.github.io/balandro/ [/I][/B][/COLOR]"
_telegram = "[COLOR lightblue][B][I] t.me/balandro_asesor [/I][/B][/COLOR]"

_team = "[COLOR hotpink][B][I] t.me/Balandro_team [/I][/B][/COLOR]"


def mainlist(item):
    logger.info()
    itemlist = []

    descartar_xxx = config.get_setting('descartar_xxx', default=False)
    descartar_anime = config.get_setting('descartar_anime', default=False)

    itemlist.append(item.clone( action='', title= '[B]CONTACTO:[/B]', text_color='limegreen', folder=False, thumbnail=config.get_thumb('pencil') ))

    itemlist.append(item.clone( action='', title= ' - Foro ' + _foro + ' Instalaciones, Novedades, Sugerencias, etc.', thumbnail=config.get_thumb('foro'), folder=False ))
    itemlist.append(item.clone( action='', title= ' - Fuente ' + _source + ' Repositorio, Add-On, etc.', thumbnail=config.get_thumb('repo'), folder=False ))
    itemlist.append(item.clone( action='', title= ' - Telegram ' + _telegram + ' Asesoramiento, Dudas, Consultas, etc.', thumbnail=config.get_thumb('telegram'), folder=False ))

    itemlist.append(item.clone( action='', title= '[B]USO:[/B]', text_color='darkorange', folder=False, thumbnail=config.get_thumb('addon') ))

    itemlist.append(item.clone( action='show_not_contemplated', title= ' - ¿ Qué NO está contemplado en Balandro ?', thumbnail=config.get_thumb('roadblock') ))
    itemlist.append(item.clone( action='show_help_faq', title= ' - Preguntas Frecuentes' ))
    itemlist.append(item.clone( action='show_help_tips', title= ' - Trucos y Consejos' ))
    itemlist.append(item.clone( action='show_help_use', title= ' - Ejemplos de Uso' ))
    itemlist.append(item.clone( action='show_help_settings', title= ' - Apuntes sobre ciertos Parámetros de la configuración', thumbnail=config.get_thumb('pencil') ))
    itemlist.append(item.clone( action='show_server_report', title= ' - Como Reportar posible Fallo en la Reproducción de Servidores', thumbnail=config.get_thumb('telegram') ))
    itemlist.append(item.clone( action='show_help_notice', title= '[B] - Comunicado Oficial de Balandro[/B]', thumbnail=config.get_thumb('megaphone'), text_color='firebrick' ))

    itemlist.append(item.clone( action='', title= '[B]MENÚS:[/B]', text_color='chartreuse', folder=False, thumbnail=config.get_thumb('addon') ))

    itemlist.append(item.clone( action='show_menu_parameters', title= ' - [COLOR green][B]Información[/B][/COLOR] sobre sus [COLOR chocolate][B]Parámetros[/B][/COLOR] Actuales para los Menús', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title= '[B]CANALES:[/B]', text_color='gold', folder=False, thumbnail=config.get_thumb('stack') ))

    if config.get_setting('developer_mode', default=False):
        itemlist.append(item.clone( action='show_channels_list', title= ' - Todos los Canales', tipo = 'all', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='show_channels_parameters', title=' - Qué [COLOR chocolate][B]Ajustes[/B][/COLOR] tiene configurados para Mostrar los Canales', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='show_channels_list', title= ' - Qué canales están Disponibles', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= ' - Qué canales están Sugeridos', suggesteds = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B] - Canales Personalización:[/B]', text_color='goldenrod', folder=False, thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='channels_status', title= '    - Personalizar canales Preferidos (Marcar ó Des-marcar)', des_rea = False, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_status', title= '    - Personalizar canales (Desactivar ó Re-activar)', des_rea = True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_prefered', title= '    - Qué canales tiene marcados como Preferidos', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_no_actives', title= '    - Qué canales tiene marcados como Desactivados', thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B] - Canales con Cuentas y/ó Dominios:[/B]', text_color='goldenrod', folder=False, thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_help_register', title= '    - [COLOR green][B]Información[/B][/COLOR] webs que requieren Registrarse (Cuenta)', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales requieren Cuenta', cta_register = True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales tienen varios Dominios', var_domains = True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - En qué canales puede comprobarse el último dominio Vigente', last_domain = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='', title= '[B] - Canales Situación:[/B]', text_color='goldenrod', folder=False, thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='channels_with_proxies', title= '    - Qué canales pueden necesitar Proxies', new_proxies=True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales están Inestables', no_stable = True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales están Temporalmente inactivos', temp_no_active = True, thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales son Privados', tipo = 'all', privates = True, thumbnail=config.get_thumb('stack') ))

    if not PY3:
        itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales son Incompatibiles con su MediaCenter',
                                    mismatched = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( action='show_channels_list', title= '    - Qué canales están Inactivos', no_active = True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR gold][B]Canales y Cuentas[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    presentar = True
    if config.get_setting('mnu_simple', default=False): presentar = False
    else:
       if descartar_xxx:
           if descartar_anime: presentar = False

    if presentar:
        itemlist.append(item.clone( action='', title= '[B]PARENTAL:[/B]', text_color='orange', folder=False, thumbnail=config.get_thumb('roadblock') ))

        if not descartar_xxx:
            itemlist.append(item.clone( action='show_help_adults', title= ' - [COLOR green][B]Información[/B][/COLOR] Control parental (+18)', thumbnail=config.get_thumb('settings') ))

        if not descartar_anime:
            itemlist.append(item.clone( action='', title= '[B] - Canales con Animes:[/B]', text_color='orange', folder=False, thumbnail=config.get_thumb('anime') ))

            itemlist.append(item.clone( action='channels_only_animes', title= '   - Qué canales pueden tener contenido de Animes', thumbnail=config.get_thumb('anime') ))
            itemlist.append(item.clone( action='channels_exclusively_animes', title= '   - Qué canales tienen contenido Exclusivamente de Animes', thumbnail=config.get_thumb('anime') ))

        if not descartar_xxx:
            itemlist.append(item.clone( action='', title= '[B] - Canales con vídeos para Adultos:[/B]', text_color='orange', folder=False, thumbnail=config.get_thumb('adults') ))

            itemlist.append(item.clone( action='channels_only_adults', title= '   - Qué canales pueden tener contenido para Adultos', thumbnail=config.get_thumb('adults') ))
            itemlist.append(item.clone( action='channels_exclusively_adults', title= '   - Qué canales tienen contenido Exclusivamente para Adultos', thumbnail=config.get_thumb('adults') ))

        itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR orange][B]Parental[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title='[B]PLAY (Servidores):[/B]', folder=False, text_color='fuchsia', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='show_help_recaptcha', title= ' - ¿ Qué significa Requiere verificación [COLOR red][B]reCAPTCHA[/B][/COLOR]?', thumbnail=config.get_thumb('roadblock') ))

    itemlist.append(item.clone( action='show_help_mega', title= ' - [COLOR green][B]Información[/B][/COLOR] servidor [COLOR goldenrod][B]Mega[/B][/COLOR]',
                                thumbnail=config.get_thumb('mega') ))

    itemlist.append(item.clone( action='show_help_uptobox', title= ' - [COLOR green][B]Información[/B][/COLOR] servidor [COLOR goldenrod][B]Uptobox[/B][/COLOR]',
                                thumbnail=config.get_thumb('uptobox') ))

    if config.get_setting('developer_mode', default=False):
        itemlist.append(item.clone( action='show_servers_list', title= ' - Todos los Servidores', tipo = 'all', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='show_servers_list', title= ' - Qué servidores están Disponibles', tipo = 'activos', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( action='', title= '[B] - Servidores Situación:[/B]', folder=False, text_color='orchid', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_servers_list', title= '    - Qué servidores tienen Vías Alternativas', tipo = 'alternativos', thumbnail=config.get_thumb('bolt') ))
    itemlist.append(item.clone( action='show_servers_list', title= '    - Qué servidores se detectan pero No están Soportados', tipo = 'sinsoporte', thumbnail=config.get_thumb('roadblock') ))
    itemlist.append(item.clone( action='show_servers_list', title= '    - Qué servidores están Inactivos', tipo = 'inactivos', thumbnail=config.get_thumb('bolt') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR fuchsia][B]Play[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title= '[B]PROXIES:[/B]', folder=False, text_color='red', thumbnail=config.get_thumb('flame') ))

    itemlist.append(item.clone( action='show_help_proxies', title= ' - [COLOR green][B]Información[/B][/COLOR] Uso de proxies', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_yourlist', title= ' - [COLOR green][B]Información[/B][/COLOR] de su Fichero Lista de proxies', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_help_providers', title= ' - [COLOR green][B]Información[/B][/COLOR] Proveedores de proxies', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_yourlist', title= ' - Visualizar su fichero [COLOR plum][B]Lista-proxies.txt[/B][/COLOR]', thumbnail=config.get_thumb('computer') ))

    itemlist.append(item.clone( action='channels_with_proxies', title= ' - Qué canales pueden usar Proxies',
                                new_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    if config.get_setting('memorize_channels_proxies', default=True):
        itemlist.append(item.clone( action='channels_with_proxies_memorized', title= ' - Qué [COLOR red]canales[/COLOR] tiene con proxies Memorizados',
                                    new_proxies=True, memo_proxies=True, test_proxies=True, thumbnail=config.get_thumb('stack') ))

    itemlist.append(item.clone( channel='actions', action = 'manto_proxies', title= ' - Quitar los proxies en los canales [COLOR red](que los tengan Memorizados)[/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'global_proxies', title = ' - Configurar proxies a usar [COLOR plum](en los canales que los necesiten)[/COLOR]', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR red][B]Proxies[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title= '[B]TORRENTS:[/B]', folder=False, text_color='blue', thumbnail=config.get_thumb('torrents') ))

    itemlist.append(item.clone( action='show_help_torrents', title= ' - ¿ Dónde obtener los Clientes/Motores para torrents (Add-Ons) ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( action='show_clients_torrent', title= ' - Clientes/Motores externos torrent soportados', thumbnail=config.get_thumb('cloud') ))
    itemlist.append(item.clone( action='channels_only_torrents', title= ' - Qué canales pueden contener archivos Torrent', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_exclusively_torrents', title= ' - Qué canales tienen enlaces Torrent Exclusivamente', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR blue][B]Torrents[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title='[B]BUSCAR:[/B]', folder=False, text_color='yellow', thumbnail=config.get_thumb('magnifyingglass') ))

    itemlist.append(item.clone( channel='search', action='show_help', title = ' - [COLOR green][B]Información[/B][/COLOR] sobre Búsquedas' ))
    itemlist.append(item.clone( channel='tmdblists', action='show_help', title= ' - [COLOR green][B]Información[/B][/COLOR] Búsquedas y Listas en TMDB' ))
    itemlist.append(item.clone( channel='search', action='show_help_parameters', title=' - Qué [COLOR chocolate][B]Ajustes[/B][/COLOR] tiene configurados para las búsquedas', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='channels_no_searchables', title= ' - Qué canales Nunca intervendrán en las búsquedas', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( action='channels_no_actives', title= ' - Qué canales no intervienen en las búsquedas (Desactivados)', thumbnail=config.get_thumb('stack') ))
    itemlist.append(item.clone( channel='actions', action = 'global_proxies', title = ' - Configurar Proxies a usar [COLOR plum](en los canales que los necesiten)[/COLOR]', thumbnail=config.get_thumb('settings') ))

    txt_exc = ''

    if config.get_setting('search_excludes_movies', default=''): txt_exc += '[COLOR deepskyblue][B]Películas[/B][/COLOR] '
    if config.get_setting('search_excludes_tvshows', default=''): txt_exc += '[COLOR hotpink][B]Series[/B][/COLOR] '
    if config.get_setting('search_excludes_documentaries', default=''): txt_exc += '[COLOR cyan][B]Documentales[/B][/COLOR] '
    if config.get_setting('search_excludes_torrents', default=''): txt_exc += '[COLOR blue][B]Torrents[/B][/COLOR] '
    if config.get_setting('search_excludes_mixed', default=''): txt_exc += '[COLOR yellow][B]Películas y/ó Series[/B][/COLOR] '
    if config.get_setting('search_excludes_all', default=''): txt_exc += '[COLOR green][B]Todos[/B][/COLOR] '

    if txt_exc:
        txt_exc.strip()
        txt_exc = '[COLOR chocolate][B] hay en [/B][/COLOR]' + txt_exc

    itemlist.append(item.clone( channel='filters', action = 'mainlist', title = ' - Excluir canales en las búsquedas' + txt_exc,
                                thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR yellow][B]Buscar[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title='[B]PREFERIDOS:[/B]', folder=False, text_color='tomato', thumbnail=config.get_thumb('videolibrary') ))

    itemlist.append(item.clone( action='show_help_tracking', title= ' - [COLOR green][B]Información[/B][/COLOR] ¿ Cómo funciona ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( action='show_help_tracking_update', title= ' - Búsqueda automática de Nuevos Episodios', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR tomato][B]Preferidos[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title='[B]DESCARGAS:[/B]', folder=False, text_color='green', thumbnail=config.get_thumb('download') ))

    itemlist.append(item.clone( channel='actions', action='show_ubicacion', title= ' - ¿ Donde se ubican las descargas ?', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR green][B]Descargas[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title='[B]ACTUALIZAR (FIXES):[/B]', folder=False, text_color='cyan', thumbnail=config.get_thumb('addon') ))

    itemlist.append(item.clone( action='show_help_fixes', title= ' - ¿ Qué son los Fix ?' ))
    itemlist.append(item.clone( action='show_last_fix', title= ' - [COLOR green][B]Información[/B][/COLOR] último Fix instalado', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( channel='actions', action = 'check_addon_updates', title= ' - Comprobar últimas actualizaciones tipo Fix', thumbnail=config.get_thumb('download') ))
    itemlist.append(item.clone( channel='actions', action = 'check_addon_updates_force', title= ' - Forzar Todas las actualizaciones tipo Fix', thumbnail=config.get_thumb('download') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR cyan][B]Actualizar[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title= '[B]MEDIA CENTER:[/B]', folder=False, text_color='pink', thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='show_log', title= ' - Visualizar el fichero LOG de su Media Center', thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( action='copy_log', title= ' - Obtener una Copia del fichero LOG de su Media Center', thumbnail=config.get_thumb('folder') ))
    itemlist.append(item.clone( action='show_advs', title= ' - Visualizar su fichero Advanced Settings de su Media Center', thumbnail=config.get_thumb('quote') ))
    itemlist.append(item.clone( action='show_plataforma', title= ' - [COLOR green][B]Información[/B][/COLOR] Plataforma', thumbnail=config.get_thumb('computer') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] configuración (categoría [COLOR pink][B]Sistema[/B][/COLOR])', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title= '[B]SISTEMA:[/B]', folder=False, text_color='teal', thumbnail=config.get_thumb('tools') ))
    itemlist.append(item.clone( action='show_test', title= ' - Test Status del sistema', thumbnail=config.get_thumb('addon') ))
    itemlist.append(item.clone( channel='actions', title= ' - Comprobar el estado de su Internet', action = 'test_internet', thumbnail=config.get_thumb('crossroads') ))
    itemlist.append(item.clone( action='show_sets', title= ' - Visualizar sus [COLOR chocolate][B]Ajustes[/B][/COLOR] Personalizados de la configuración', thumbnail=config.get_thumb('settings') ))
    itemlist.append(item.clone( action='show_cook', title= ' - Visualizar su fichero de cookies', thumbnail=config.get_thumb('folder') ))
    itemlist.append(item.clone( channel='actions', action = 'open_settings', title= ' - [COLOR chocolate][B]Ajustes[/B][/COLOR] Configuración', thumbnail=config.get_thumb('settings') ))

    itemlist.append(item.clone( action='', title='[B]VERSION:[/B]', folder=False, text_color='violet', thumbnail=config.get_thumb('addon') ))
    itemlist.append(item.clone( action='show_version', title= ' - [COLOR green][B]Información[/B][/COLOR] Versión', thumbnail=config.get_thumb('news') ))
    itemlist.append(item.clone( action='show_changelog', title= ' - Historial de Versiones', thumbnail=config.get_thumb('news') ))

    itemlist.append(item.clone( action='', title='[B]DESARROLLO:[/B]', folder=False, text_color='firebrick', thumbnail=config.get_thumb('team') ))
    itemlist.append(item.clone( action='', title= ' - Team ' + _team + ' Unirse al Equipo de Desarrollo', folder=False, thumbnail=config.get_thumb('foro') ))
    itemlist.append(item.clone( action='show_dev_notes', title= ' - Notas para Developers (desarrolladores)', thumbnail=config.get_thumb('tools') ))

    if config.get_setting('developer_mode', default=False):
        itemlist.append(item.clone( channel='submnuctext', action='submnu_developer', title = ' - [B]Acceso a Desarrollo[/B]', thumbnail=config.get_thumb('team'), text_color='firebrick' ))

    itemlist.append(item.clone( action='', title='[B]LEGALIDAD:[/B]', folder=False, text_color='crimson', thumbnail=config.get_thumb('addon') ))
    itemlist.append(item.clone( action='show_license', title= ' - Licencia (Gnu Gpl v3)', thumbnail=config.get_thumb('megaphone') ))
    itemlist.append(item.clone( action='show_legalidad', title= ' - Cuestiones Legales', thumbnail=config.get_thumb('megaphone') ))

    return itemlist


def channels_only_animes(item):
    logger.info()

    filters.only_animes(item)

def channels_exclusively_animes(item):
    logger.info()

    item.exclusively_animes = True

    filters.only_animes(item)

def channels_only_adults(item):
    logger.info()

    filters.only_adults(item)

def channels_exclusively_adults(item):
    logger.info()

    item.exclusively_adults = True

    filters.only_adults(item)

def show_channels_list(item):
    logger.info()

    filters.show_channels_list(item)

def channels_status(item):
    logger.info()

    filters.channels_status(item)

def channels_des_rea(item):
    logger.info()

    item.des_rea = True

    filters.channels_status(item)

def channels_with_proxies(item):
    logger.info()

    filters.with_proxies(item)

def channels_with_proxies_memorized(item):
    logger.info()

    # por si venimos de config
    if config.get_setting('memorize_channels_proxies', default=True):
        item.memo_proxies = True

        filters.with_proxies(item)

def channels_no_actives(item):
    logger.info()

    filters.no_actives(item)

def channels_no_searchables(item):
    logger.info()

    item.no_searchables = True

    filters.no_actives(item)

def channels_prefered(item):
    logger.info()

    filters.only_prefered(item)

def channels_suggesteds(item):
    logger.info()

    item.suggesteds = True

    filters.show_channels_list(item)

def channels_inestables(item):
    logger.info()

    item.no_stable = True

    filters.show_channels_list(item)

def channels_only_torrents(item):
    logger.info()

    filters.only_torrents(item)

def channels_exclusively_torrents(item):
    logger.info()

    item.exclusively_torrents = True

    filters.only_torrents(item)

def show_clients_torrent(item):
    logger.info()

    if not item.title: item.title = 'soportados'

    filters.show_clients_torrent(item)

def show_servers_list(item):
    logger.info()

    # por si venimos de config
    if not item.tipo: item.tipo = 'activos'

    filters.show_servers_list(item)


def show_help_register(item):
    logger.info()

    txt = '*) Determinadas webs obligan a registrarse para permitir su acceso.'

    txt += '[CR][CR]'
    txt += ' Es importante usar [B][COLOR gold]cuentas secundarias[/COLOR][/B] para registrarse, nunca useis las vuestras personales.'

    txt += '[CR][CR]'
    txt += '*) Para ello desde otro equipo debeis accecder a la web en cuestión y registraros (darse de alta)'

    txt += '[CR][CR]'
    txt += ' Si desconoceis el dominio actual de esa web, mediante un navegador localizar su [B][COLOR gold]twitter[/COLOR][/B]'

    txt += '[CR][CR]'
    txt += ' Por ejemplo [B][COLOR gold]HdFull[/COLOR][/B] twitter oficial ó [B][COLOR gold]PlayDede[/COLOR][/B] twitter oficial'

    txt += '[CR][CR]'
    txt += '*) Imprescindible tomar buena nota de vuestro [B][COLOR gold]Usuario y Contraseña[/COLOR][/B] para cada web.'

    txt += '[CR][CR]'
    txt += '*) Una vez tengais vuestros datos, podeis informarlos en la configuración, ó bien se os solicitará al acceder a ese canal determinado.'

    txt += '[CR][CR]'
    txt += '*) Mientras mantengais las sesiones abiertas via navegador en estos dominios, no tendreis q volver a informar vuestras credenciales.'

    txt += '[CR][CR]'
    txt += '*) [B][COLOR gold]Atención[/COLOR][/B]: las [COLOR chartreuse]Sesiones Abiertas[/COLOR] en vuestro Media Center [B][COLOR yellow]No son In Eternum[/COLOR][/B], por ello es conveniente, que procedaís a [COLOR chartreuse]Cerrar vuestra Sesión[/COLOR] cada cierto tiempo, porque podría provocar que no se presentaran resultados.'

    platformtools.dialog_textviewer('Información dominios que requieren Registrarse', txt)


def show_help_mega(item):
    logger.info()

    txt = '*) Si su Media Center es una versión anterior a [COLOR gold][B]19.x[/COLOR][/B] y opera bajo el sistema operativo [COLOR gold][B]Windows[/COLOR][/B], en determinadas ocasiones, puede fallar la Reproducción.'

    platformtools.dialog_textviewer('Información servidor Mega', txt)


def show_help_uptobox(item):
    logger.info()

    txt = '*) Determinados servidores obligan a registrarse para permitir su acceso.'

    txt += '[CR][CR]'
    txt += ' Es importante usar [B][COLOR gold]cuentas secundarias[/COLOR][/B] para registrarse, nunca useis las vuestras personales.'

    txt += '[CR][CR]'
    txt += '*) Para ello desde otro equipo debeis accecder a la web en cuestión y registraros (darse de alta)'

    txt += '[CR][CR]'
    txt += ' Si desconoceis el dominio actual de ese servidor, mediante un navegador localizar su [B][COLOR gold]twitter[/COLOR][/B]'

    txt += '[CR][CR]'
    txt += ' Por ejemplo [B][COLOR gold]Uptobox[/COLOR][/B] twitter oficial'

    txt += '[CR][CR]'
    txt += '*) Imprescindible tomar buena nota de vuestro [B][COLOR gold]Usuario y Contraseña[/COLOR][/B] para ese servidor.'

    txt += '[CR][CR]'
    txt += '*) Una vez tengais vuestros datos, se os solicitará al acceder a ese servidor determinado.'

    txt += '[CR][CR]'
    txt += '*) Acceder desde otro equipo via navegador a [B][COLOR gold]uptobox.com/pin[/COLOR][/B], solo se gestionan las cuentas [B][COLOR gold]Free[/COLOR][/B]'

    txt += '[CR][CR]'
    txt += '*) En el caso de no estar registrados proceder a ello (darse de alta)'

    txt += '[CR][CR]'
    txt += ' Iniciar la sesión con vuestras credenciales'
    txt += ' e introducir el [B][COLOR gold]PIN[/COLOR][/B] que se os mostró en la ventana al intentar reproducir, para tener vinculada vuestra cuenta.'

    txt += '[CR][CR]'
    txt += '*) Mientras mantengais las sesiones abiertas via navegador en ese servidor, no tendreis q volver a informar vuestras credenciales.'

    txt += '[CR][CR]'
    txt += '*) Hay servidores que limitan el [B][COLOR gold]tiempo máximo de visionado diario[/COLOR][/B] (aprox. 150 minutos).'

    platformtools.dialog_textviewer('Información servidor Uptobox', txt)


def show_server_report(item):
    logger.info()

    txt = '*) Estos Reportes debereís informarlos en nuestro grupo de Telegram' + _telegram

    txt += '[CR][CR]'
    txt += '*) [B][COLOR gold]Antes de reportarlo como un posible error, rogamos accedaís a través de un navegador web, a ese canal en concreto y procedaís a comprobar si esa pelicula/serie/episodio reproduce a través del servidor en cuestión[/COLOR][/B]'

    txt += '[CR][CR]'
    txt += '*) [B][COLOR yellow]Si el resultado de esta operativa ha resultado satisfactoria, indicarnos toda esa información para proceder a su verficación/subsanación[/COLOR][/B]'

    txt += '[CR][CR]'
    txt += '*) Debeís comprender que este trabajo ha de ser compartido entre vosotros y nosotros, porqué si la carga solo recayera sobre nosotros sería imposible abordarlo por saturación/falta de tiempo'

    txt += '[CR][CR]'
    txt += '*) Muchas gracias, por vuestro tiempo y comprensión al respecto'

    platformtools.dialog_textviewer('Como Reportar posible Fallo en la Reproducción de servidores', txt)


def show_help_settings(item):
    logger.info()

    txt = '*) Las opciones para los [COLOR gold]listados de canales[/COLOR] se usan si marcas canales como preferidos ó desactivados.'
    txt += ' Esto lo puedes hacer desde el menú contextual en los listados de canales.'

    txt += '[CR][CR]'
    txt += '*) En "Búsquedas" el parámetro "[COLOR gold]Resultados previsualizados por canal[/COLOR]" sirve para limitar el número de coincidencias que se muestran en la pantalla de búsqueda global.'
    txt += ' Es para que no salga un listado demasiado largo ya que algunos canales son más sensibles que otros y pueden devolver bastantes resultados.'
    txt += ' Pero de todas maneras se puede acceder al listado de todos los resultados de cada canal concreto.'
    txt += ' Dispones de más parámetros personalizables en la configuración "Buscar".'

    txt += '[CR][CR]'
    txt += '*) En "Reproducción" se puede activar Autoplay para no tener que seleccionar un servidor para reproducir.'
    txt += ' Si hay algún canal para el que quieras desactivar el autoplay puedes indicarlo en la configuración "Play".'

    txt += '[CR][CR]'
    txt += '*) En "Reproducción" los parámetros para ordenar/filtrar los enlaces [COLOR gold]por idioma[/COLOR] permiten indicar nuestras preferencias de idiomas.'
    txt += ' Entre Español, Latino y Versión Original elije el orden que prefieres, ó descarta alguno de ellos si no te interesa.'
    txt += ' Todo ello puedes personalizarlo en la configuración "Play".'

    txt += '[CR][CR]'
    txt += '*) En "Reproducción" los parámetros para ordenar los enlaces [COLOR gold]por calidad[/COLOR] permiten mostrar antes los de más calidad en lugar de mostrarlos según el orden que tienen en la web.'
    txt += ' Algunos canales tienen valores fiables de calidad pero otros no, depende de cada web.'
    txt += ' Todo ello puedes personalizarlo en la configuración "Play".'

    txt += '[CR][CR]'
    txt += '*) En "Reproducción" los parámetros para ordenar/filtrar los enlaces [COLOR gold]por servidores[/COLOR] permiten hacer algunos ajustes en función de los servers.'
    txt += ' Si no quieres que te salgan enlaces de ciertos servidores, escríbelos en "descartados" (ej: torrent,mega).'
    txt += ' Y si quieres priorizar algunos servidores escríbelos en "preferidos" (ej: torrent, mega), ó al revés en "última opción" (ej: torrent, mega).'
    txt += ' Para modificar estas opciones necesitas saber qué servidores te funcionan mejor y peor, en caso de duda no hace falta que lo modifiques.'
    txt += ' Todo ello puedes personalizarlo en la configuración "Play".'

    txt += '[CR][CR]'
    txt += '*) Una opción que puede provocar una demora en los tiempos de respuesta es en configuración "TMDB" si se activa "[COLOR gold]buscar información extendida[/COLOR]".'
    txt += ' Esto provoca que los listados de películas y series de todos los canales tarden más en mostrarse ya que se hace una segunda llamada a TMDB para intentar recuperar más datos.'

    txt += '[CR][CR]'
    txt += '*) En "TMDB" se pueden desactivar las "[COLOR gold]llamadas a TMDB en los listados[/COLOR]".'
    txt += ' Esto provoca que los listados de películas y series de todos los canales tarden menos en mostrarse pero en la mayoría de casos no tendrán información como la sinopsis y las carátulas serán de baja calidad.'
    txt += ' Puede ser útil desactivarlo temporalmente en casos dónde alguna película/serie no se identifica correctamente en tmdb y se quieran ver los datos originales de la web.'

    txt += '[CR][CR]'
    txt += '*) Exiten más parámetros en la [COLOR gold]Configuracion[/COLOR] de Balandro,  para tener personalizada su ejecución.'
    txt += ' Divididos por categorías [COLOR gold]Menú, Canales, Parental, Cuentas, Play, Proxies, Torrents, Buscar, etc.[/COLOR].'

    platformtools.dialog_textviewer('Notas sobre algunos parámetros de la configuración', txt)


def show_help_tips(item):
    logger.info()

    txt = '*) Es importante usar el [B][COLOR gold]menú contextual[/COLOR][/B] para acceder a acciones que se pueden realizar sobre los elementos de los listados.'
    txt += ' Si dispones de un teclado puedes acceder a él pulsando la tecla C, en dispositivos táctiles manteniendo pulsado un elemento, y en mandos de tv-box manteniendo pulsado el botón de selección.'
    txt += ' Si usas un mando de TV es recomendable configurar una de sus teclas con "ContextMenu".'

    txt += '[CR][CR]'
    txt += '*) En los listados de canales puedes usar el menú contextual para marcarlos como Desactivado/Activo/Preferido.'
    txt += ' De esta manera podrás tener tus [COLOR gold]canales preferidos[/COLOR] al inicio y quitar ó mover al final los que no te interesen.'
    txt += ' Los canales desactivados son accesibles pero no forman parte de las búsquedas.'

    txt += '[CR][CR]'
    txt += '*) Si en algún canal encuentras una película/serie que te interesa pero fallan sus enlaces, accede al menú contextual y selecciona'
    txt += ' "[COLOR gold]buscar en otros canales[/COLOR]" para ver si está disponible en algún otro canal.'

    txt += '[CR][CR]'
    txt += '*) Desde cualquier pantalla desplázate hacia el lateral izquierdo para desplegar algunas [COLOR gold]opciones standard de su Media Center[/COLOR].'
    txt += ' Allí tienes siempre un acceso directo a la Configuración del addon y también puedes cambiar el tipo de vista que se aplica a los listados.'
    txt += ' Entre Lista, Cartel, Mays., Muro de información, Lista amplia, Muro, Fanart, escoge como prefieres ver la información.'

    txt += '[CR][CR]'
    txt += '*) Algunos canales de series tienen un listado de [COLOR gold]últimos episodios[/COLOR]. En función de las características de las webs, los enlaces llevan'
    txt += ' a ver el capítulo ó a listar las temporadas de la serie. Cuando es posible, desde el enlace se ve el episodio y desde el menú contextual'
    txt += ' se puede acceder a la temporada concreta ó la lista de temporadas.'

    txt += '[CR][CR]'
    txt += '*) Para seguir series es recomendable usar la opción [COLOR gold]Preferidos[/COLOR]. Busca la serie que te interese en cualquiera de los canales y desde el menú contextual guárdala.'
    txt += ' Luego ves a "Preferidos" dónde podrás gestionar lo necesario para la serie. Además puedes usar "Buscar en otros canales" y desde el listado de resultados con el menú'
    txt += ' contextual también los puedes guardar y se añadirán a los enlaces que ya tenías. De esta manera tendrás alternativas en diferentes enlaces por si algún día falla alguno ó desaparece.'

    platformtools.dialog_textviewer('Trucos y consejos varios', txt)


def show_help_use(item):
    logger.info()

    txt = '[COLOR gold][B]Uso modo CASUAL:[/B][/COLOR][CR]'
    txt += 'Accede por ejemplo a Películas ó Series desde el menú principal, entra en alguno de los canales y navega por sus diferentes opciones hasta encontrar una película que te interese.'
    txt += ' Al entrar en la película se mostrará un diálogo con diferentes opciones de vídeos encontrados.'
    txt += ' Prueba con el primero y si el enlace es válido empezará a reproducirse. Sino, prueba con alguno de los otros enlaces disponibles.'
    txt += ' Si ninguno funcionara, desde el enlace de la película accede al menú contextual y selecciona "Buscar en otros canales".'

    txt += '[CR][CR][COLOR gold][B]Uso modo DIRECTO:[/B][/COLOR][CR]'
    txt += 'Si quieres ver una película/serie concreta, accede a "Buscar" desde el menú principal y escribe el título en el buscador.'
    txt += ' Te saldrá una lista con las coincidencias en todos los canales disponibles.'

    txt += '[CR][CR][COLOR gold][B]Uso modo PLANIFICADOR:[/B][/COLOR][CR]'
    txt += 'Navega por los diferentes canales y ves apuntando las películas/series que te puedan interesar.'
    txt += ' Para ello accede al menú contextual desde cualquier película/serie y selecciona "Guardar enlace".'
    txt += ' Cuando quieras ver una película/serie, accede a "Preferidos" desde el menú principal dónde estará todo lo guardado.'

    txt += '[CR][CR][COLOR gold][B]Uso modo ASEGURADOR:[/B][/COLOR][CR]'
    txt += 'Descarga algunas películas para tener listas para ver sin depender de la saturación de la red/servidores en momentos puntuales.'
    txt += ' Desde cualquier película/episodio, tanto en los canales como en "Preferidos", accede al menú contextual y "Descargar vídeo".'
    txt += ' Selecciona alguno de los enlaces igual que cuando se quiere reproducir y empezará la descarga.'
    txt += ' Para ver lo descargado, accede a "Descargas" desde el menú principal.'

    txt += '[CR][CR][COLOR gold][B]Uso modo COLECCIONISTA:[/B][/COLOR][CR]'
    txt += 'Desde "Preferidos" accede a "Gestionar listas", dónde puedes crear diferentes listas para organizarte las películas y series que te interesen.'
    txt += ' Por ejemplo puedes tener listas para distintos usuarios de Balandro (Padres, Esposa, Hijos, etc.) ó de diferentes temáticas, ó para guardar lo que ya hayas visto, ó para pasar tus recomendaciones a algún amigo, etc.'

    platformtools.dialog_textviewer('Ejemplos de uso de Balandro', txt)


def show_help_faq(item):
    logger.info()

    txt = '[COLOR gold][B]¿ De dónde viene Balandro ?[/B][/COLOR][CR]'
    txt += 'Balandro es desde el año [COLOR cyan][B]2018[/B][/COLOR] un addon derivado de [COLOR gold]Pelisalacarta y Alfa[/COLOR], optimizado a nivel interno de código y a nivel funcional para el usuario.'
    txt += ' Puede ser útil en dispositivos poco potentes como las Raspberry Pi u otros TvBox y para usuarios que no se quieran complicaciones.'
    txt += ' Al ser un addon de tipo navegador, tiene el nombre de un velero ya que Balandro era una embarcación ligera y maniobrable, muy apreciada por los piratas.'

    txt += '[CR][CR][COLOR gold][B]¿ Qué características tiene Balandro ?[/B][/COLOR][CR]'
    txt += 'Principalmente permite acceder a los contenidos de webs con vídeos de películas y series para reproducirlos y/o guardarlos, y'
    txt += ' dispone de unos Preferidos propios dónde poder apuntar todas las Películas y Series que interesen al usuario.'
    txt += ' Se pueden configurar múltiples opciones, por ejemplo la preferencia de idioma, la reproducción automática, los colores para los listados, los servidores preferidos, excluir canales en las búsquedas, etc.'

    txt += '[CR][CR][COLOR gold][B]¿ Cómo funciona el Autoplay ?[/B][/COLOR][CR]'
    txt += 'Se puede activar la función de reproducción automática desde la configuración del addon.'
    txt += ' Si se activa, al ver una película ó episodio se intenta reproducir el primero de los enlaces que funcione, sin mostrarse el diálogo de selección de servidor.'
    txt += ' Los enlaces se intentan secuencialmente en el mismo orden que se vería en el diálogo, por lo que es importante haber establecido las preferencias de idioma, servidores y calidades.'

    txt += '[CR][CR][COLOR gold][B]¿ En qué orden se muestran los enlaces de servidores ?[/B][/COLOR][CR]'
    txt += 'El orden inicial es por la fecha de los enlaces, para tener al principio los últimos actualizados ya que es más probable que sigan vigentes, aunque en los canales que no lo informan es según el orden que devuelve la web.'
    txt += ' Desde la configuración se puede activar el ordenar por calidades, pero su utilidad va a depender de lo que muestre cada canal y la fiabilidad que tenga.'
    txt += ' A partir de aquí, si hay preferencias de servidores en la configuración, se cambia el orden para mostrar al principio los servidores preferentes y al final los de última opción.'
    txt += ' Y finalmente se agrupan en función de las preferencias de idiomas del usuario.'

    txt += '[CR][CR][COLOR cyan][B]¿ Funcionan los enlaces Torrent ?[/B][/COLOR][CR]'
    txt += 'El addon está preparado para tratarlos usando un Motor/Cliente de torrents externo, tipo [COLOR gold]Elementum, etc.[/COLOR]'
    txt += ' Estos Motores/Clientes externos (addons) torrents no están incluidos en Balandro y deben Instalarse por separado.'
    txt += ' Además, debe indicarse Obligatoriamente en la configuración de Balandro cual va a ser su Motor/Cliente habitual de torrents.'

    txt += '[CR][CR]Si algun otro addon tiene activado [COLOR gold]"Borrar caché de kodi en el inicio"[/COLOR], se elimina una carpeta temporal que [COLOR gold]Elementum[/COLOR] necesita'
    txt += ' [COLOR gold].../.kodi/temp/elementum/[/COLOR], en consecuencia puede fallar la descarga/reproducción del torrent.'
    txt += ' Cuando a [COLOR gold]Elementum[/COLOR] se le pasa un enlace .torrent lo intenta descargar en esa carpeta, pero no podrá hacerlo si esta carpeta se ha eliminado.'
    txt += ' Si esto sucede, en el Log de su Media Center se observa el mensaje [COLOR gold]"Error adding torrent: &os.PathError"[/COLOR].'
    txt += ' Este error no se produce si el enlace es de tipo [COLOR gold]magnet:?[/COLOR], por lo tanto, pueden haber enlaces en Balandro que funcionen y otros que No.'

    txt += '[CR][CR][COLOR cyan][B]Este problema se resuelve:[/B][/COLOR] si se accede a la Configuración de [COLOR gold]Elementum[/COLOR] y se guarda nuevamente, se regenera su carpeta de caché y funcionará correctamente la descarga/reproducción del torrent.'
    txt += ' Pero si se mantiene activado el borrado por ejemplo en Indigo, al reiniciar su Media Center Kodi dejará de funcionar de nuevo.'

    txt += '[CR][CR][COLOR chartreuse][B]¿ Porqué la opción Buscar entra em modo bucle (vuelve a solicitar el texto a localizar) ?[/B][/COLOR][CR]'
    txt += 'Addons de limpieza que pueden afectar al funcionamiento de Balandro, [COLOR gold]LimpiaTuKodi, Indigo y similares.[/COLOR]'

    txt += '[CR][CR]Cuando desde estos addons se ejecuta la función [COLOR gold]"Limpiar Cache y Rom"[/COLOR],'
    txt += ' se elimina la carpeta interna de la caché de su Media Center Kodi [COLOR gold].../.kodi/temp/archive_cache/[/COLOR]'
    txt += ' y ello provoca que este no pueda cachear. Al no poder usar esta caché, puede influir en el rendimiento en general de todos los addons,'
    txt += ' pero dónde resulta una molestia dentro de Balandro (y demás addons) es al buscar, ya que después de hacer una búsqueda y entrar en alguno de los resultados,'
    txt += ' al volver atrás, vuelve a solicitar de nuevo la introducción de texto, cuando debería volver a mostrar la lista de resultados previa.'

    txt += '[CR][CR][COLOR chartreuse][B]Este problema se resuelve:[/B][/COLOR] Re-iniciando su Media center Kodi, ya que Kodi vuelve a generar la carpeta de caché al iniciarse.'
    txt += ' Cualquier addon que en lugar de eliminar el contenido del caché para limpiar, elimine la propia carpeta provocará este mismo efecto.'

    txt += '[CR][CR][COLOR blue][B]¿ Como evitar la Ventana "Lista de Reproduccion Abortada" aunque el enlace NO reproduzca ?[/B][/COLOR][CR]'
    txt += 'Es necesario incorporar en su Media Center, las instrucciones que a continuación se detallan en el archivo [COLOR gold]"advancedsettings.xml"[/COLOR], si no existiera dicho fichero deberá crear uno Nuevo con ese Contenido.'
    txt += ' la ruta donde debe estar ubicado este arhivo es [COLOR gold].../.kodi/userdata/[/COLOR]'

    txt += '[CR][CR][COLOR blue][B]Este problema se resuelve:[/B][/COLOR] Con las siguientes Instrucciones.[CR]'

    if PY3: txt += '[COLOR darkorange][B]Pueden NO funcionar correctamente en su Media Center.[/B][/COLOR][CR]'

    txt += '<!-- Balandro -->[CR]'
    txt += '[COLOR yellow][B]<advancedsettings  version="1.0">[/B][/COLOR][CR]'
    txt += '[COLOR yellow][B]   <playlistretries>-1</playlistretries>[/B][/COLOR][CR]'
    txt += '[COLOR yellow][B]   <playlisttimeout>-1</playlisttimeout>[/B][/COLOR][CR]'
    txt += '[COLOR yellow][B]</advancedsettings>[/B][/COLOR]'

    platformtools.dialog_textviewer('Preguntas Frecuentes', txt)


def show_help_notice(item):
    logger.info()

    txt = '[COLOR gold][B]COMUNICADO BALANDRO 9/5/2022 20:00[/B][/COLOR][CR][CR]'

    txt += '[COLOR yellow][B][I]Son ya más de 4 años desde la aparición pública de nuestro Addon[/COLOR][COLOR cyan] (2018)[/I][/B][/COLOR][CR][CR]'

    txt += 'Desde [COLOR gold]Enero/2021[/COLOR] hemos solicitado incorporaciones al desarrollo del Addon [COLOR gold](equipo Balandro Team)[/COLOR] por distintas vías, y todos nuestros intentos han sido infructuosos hasta el momento[CR]'

    txt += '[CR][COLOR darkorange]Motivos:[/COLOR][CR]'
    txt += ' - Desconocen la Programación[CR]'
    txt += ' - Desconocen el lenguaje Python[CR]'
    txt += ' - No disponen de Tiempo para ello[CR]'
    txt += ' - No están Interesados[CR]'
    txt += ' - Solo se comprometen a intervenciones Puntuales[CR]'

    txt += '[CR][COLOR darkorange]Situación:[/COLOR][CR]'
    txt += '  [COLOR chartreuse][B]El Addon se seguirá manteniendo[/B][/COLOR], pero nos va a ser del todo imposible, acomenter el mantenimiento del mismo como ha sido hasta ahora, a no ser que realmente vengan [COLOR gold]Nuevas Incorporaciones a Balandro Team[/COLOR] con un compromiso y complicidad total[CR]'

    txt += '[CR]  El principal miembro de [COLOR gold]Balandro Team[/COLOR] y responsable del mantenimiento, ya ha superado una edad sexagenaria, y se agotó de este cometido[CR]'

    txt += '[CR]  Tan solo vamos a efectuar los [COLOR chartreuse][B]Mínimos cambios en Canales y Servidores[/B][/COLOR], que no sufran una alteración radical de estructura, y no abordaremos jamás, ni [COLOR chartreuse][B]Nuevos Canales/Servidores[/B][/COLOR], ni [COLOR chartreuse][B]Mejoras[/B][/COLOR], reservandonos el derecho incluso de [COLOR chartreuse][B]Desactivar[/B][/COLOR] lo que nos de un quebradero de cabeza[CR]'

    txt += '[CR][COLOR darkorange]Conclusión:[/COLOR][CR]'
    txt += '  Somos conscientes, que con el paso del tiempo, el Addon sufra una degradación y deje de cumplir vuestras expectativas sobre el, pero tambien debeís tener presente, que nosotros así mismo tenemos nuestras vidas y existe más vida fuera del Media Center Kodi[CR]'

    txt += '[CR]Saludos, Balandro Team[CR]'

    platformtools.dialog_textviewer('Comunicado Oficial de Balandro', txt)


def show_not_contemplated(item):
    logger.info()

    txt ='[CR][CR][COLOR red][B]¿ Qué temas no están Implementados dentro de Balandro ?[/B][/COLOR][CR]'

    txt += ' - Las Versiones anteriores a [COLOR darkorange][B]K17.x[/B][/COLOR] en su Media Center.[CR]'

    txt += ' - Ejecución de Balandro bajo [COLOR gold]Builds, Wizards ó Widgets[/COLOR] no se pueden garantizar resultados satisfactorios[CR]'
    txt += ' - Intervención del fichero [COLOR gold]AdvancedSettings[/COLOR] con sentencias relativas a la memoria de su Media Center[CR]'
    txt += ' - Integración con la [COLOR gold]Videoteca[/COLOR] de su Media Center[CR]'
    txt += ' - Motor Torrent [COLOR gold]Horus / AceStream[/COLOR][CR]'
    txt += ' - Integración con cuentas [COLOR gold]Alldebrid[/COLOR][CR]'
    txt += ' - Descargar [COLOR gold]Todos[/COLOR] los Capítulos de una Temporada alunísono[CR]'
    txt += ' - Acceder a [COLOR gold]Una Página Concreta[/COLOR] en los listados de las opciones de los canales[CR]'
    txt += ' - Incluir el [COLOR gold]Rating[/COLOR] en los listados de las opciones de los canales[CR]'

    platformtools.dialog_textviewer('¿ Qué NO está contemplado en Balandro ?', txt)


def show_help_tracking(item):
    logger.info()

    txt = '[COLOR gold]¿ Cómo se guardan las películas ó series ?[/COLOR][CR]'
    txt += 'Desde cualquiera de los canales dónde se listen películas ó series, accede al menú contextual y selecciona "Guardar película/serie".'
    txt += ' En el caso de películas es casi instantáneo, y para series puede demorarse unos segundos si tiene muchas temporadas/episodios.'
    txt += ' Para ver y gestionar todo lo que tengas, accede a "Preferidos" desde el menú principal del addon.'
    txt += ' También puedes guardar una temporada ó episodios concretos.'

    txt += '[CR][CR][COLOR gold]¿ Qué pasa si una película/serie no está correctamente identificada ?[/COLOR][CR]'
    txt += 'Esto puede suceder cuando la película/serie no está bien escrita en la web de la que procede ó si hay varias películas con el mismo título.'
    txt += ' Si no se detecta te saldrá un diálogo para seleccionar entre varias opciones ó para cambiar el texto de búsqueda.'
    txt += ' Desde las opciones de configuración puedes activar que se muestre siempre el diálogo de confirmación, para evitar que se detecte incorrectamente.'

    txt += '[CR][CR][COLOR gold]¿ Y si no se puede identificar la película/serie ?[/COLOR][CR]'
    txt += 'Es necesario poder identificar cualquier película/serie en TMDB, sino no se puede guardar.'
    txt += ' Si no existe en [COLOR gold]themoviedb.org[/COLOR] ó tiene datos incompletos puedes completar allí la información ya que es un proyecto comunitario y agradecerán tu aportación.'

    txt += '[CR][CR][COLOR gold]¿ Se puede guardar la misma película/serie desde canales diferentes ?[/COLOR][CR]'
    txt += 'Sí, al guardar se apuntan en la base de datos interna los datos propios de la película, serie, temporada ó episodio, y también el enlace al canal de dónde se ha guardado.'
    txt += ' De esta manera puedes tener diferentes alternativas por si algún canal fallara ó no tuviera enlaces válidos.'
    txt += ' Si tienes enlaces de varios canales, al reproducir podrás escoger en cual intentarlo.'

    txt += '[CR][CR][COLOR gold]¿ Se guardan las marcas de películas/episodios ya vistos ?[/COLOR][CR]'
    txt += 'Sí, su Media Center gestiona automáticamente las marcas de visto/no visto.'
    txt += ' Estas marcas están en la base de datos de su Media Center pero no en las propias de Balandro.'

    txt += '[CR][CR][COLOR gold]¿ Qué pasa si un enlace guardado deja de funcionar ?[/COLOR][CR]'
    txt += 'A veces las webs desaparecen ó cambian de estructura y/o de enlaces, y eso provoca que en Preferidos dejen de ser válidos.'
    txt += ' Al acceder a un enlace que da error, se muestra un diálogo para escoger si se quiere "Buscar en otros canales" ó "Volver a buscar en el mismo canal".'
    txt += ' Si la web ha dejado de funcionar deberás buscar en otros canales, pero si ha sufrido cambios puedes volver a buscar en ella.'

    txt += '[CR][CR][COLOR gold]¿ Se puede compartir una lista de Preferidos ?[/COLOR][CR]'
    txt += 'De momento puedes hacerlo manualmente. En la carpeta userdata del addon, dentro de "tracking_dbs" están los ficheros [COLOR gold].sqlite[/COLOR] de cada lista que tengas creada.'
    txt += ' Puedes copiar estos ficheros y llevarlos a otros dispositivos.'

    txt += '[CR][CR][COLOR gold]¿ Cómo invertir el orden de los episodios ?[/COLOR][CR]'
    txt += 'Por defecto los episodios dentro de una temporada se muestran en orden ascendente, del primero al último.'
    txt += ' Si prefieres que sea al revés, desde el menú contextual de una temporada selecciona "Invertir el orden de los episodios" y'
    txt += ' tu preferencia quedará guardada para esa temporada.'

    txt += '[CR][CR][COLOR gold]¿ Hay alguna límitación en los episodios a guardar por cada temporada ?[/COLOR][CR]'
    txt += 'Si, no se almacenarán más de [COLOR red]50 episodios por temporada [/COLOR], si fuera necesario, debe gestionar esa serie y/o temporada'
    txt += ' a través de los [COLOR gold]"favoritos/videoteca genérica"[/COLOR] de su Media Center.'

    txt += '[CR][CR][COLOR gold]¿ Cómo integrar los Preferidos en la Videoteca de su Media Center? ?[/COLOR][CR]'
    txt += 'Una alternativa es añadir los Preferidos de Balandro a los "favoritos/videoteca genérica" de su Media center.'
    txt += ' ó bien, añadir el contenido de Preferidos de Balandro a la "Videoteca genérica" de su Media center, con el addon externo "ADD TO LIB"'

    platformtools.dialog_textviewer('Preferidos y su Funcionamiento', txt)


def show_help_tracking_update(item):
    logger.info()

    txt = '[COLOR gold]¿ Qué es el servicio de búsqueda de nuevos episodios ?[/COLOR][CR]'
    txt += 'El servicio es un proceso de Balandro que se ejecuta al iniciarse su Media Center, y se encarga de comprobar cuando hay que buscar actualizaciones.'
    txt += ' En la configuración dentro de "Actualizar" puedes indicar cada cuanto tiempo deben hacerse las comprobaciones.'
    txt += ' Por defecto es dos veces al día, cada 12 horas, pero puedes cambiarlo.'
    txt += ' Si lo tienes desactivado, puedes ejecutar manualmente la misma búsqueda desde el menú contextual de "Series" dentro de "Preferidos".'

    txt += '[CR][CR][COLOR gold]¿ Cómo se activa la búsqueda de nuevos episodios para series ?[/COLOR][CR]'
    txt += 'Desde el listado de series dentro de "Preferidos" accede a "Gestionar serie" desde el menú contextual.'
    txt += ' Al seleccionar "Programar búsqueda automática de nuevos episodios" podrás definir el seguimiento que quieres darle a la serie'
    txt += ' e indicar cada cuanto tiempo hay que hacer la comprobación de si hay nuevos episodios.'

    txt += '[CR][CR][COLOR gold]¿ Cómo se combina el servicio con las series ?[/COLOR][CR]'
    txt += 'Cada vez que se ejecuta el servicio (1, 2, 3 ó 4 veces por día) se buscan las series que tienen activada la búsqueda automática.'
    txt += ' Por cada serie según su propia periodicidad se ejecuta ó no la búsqueda.'
    txt += ' Esto permite por ejemplo tener series que sólo requieren una actualización por semana, y otras dónde conviene comprobar cada día.'

    txt += '[CR][CR][COLOR gold]¿ Porqué la búsqueda de nuevos episodios está desactivada por defecto ?[/COLOR][CR]'
    txt += 'Es preferible ser prudente con las actualizaciones para no saturar más las webs de dónde se obtiene la información.'
    txt += ' Por esta razón al guardar series por defecto no tienen activada la comprobación de nuevos episodios y hay que indicarlo explícitamente si se quiere.'
    txt += ' Si por ejemplo sigues una serie ya terminada seguramente no necesitarás buscar nuevos episodios, en cambio si sigues una serie de un show diario sí te interesará.'

    txt += '[CR][CR][COLOR gold]¿ Dónde se ven los nuevos episodios encontrados ?[/COLOR][CR]'
    txt += 'En "Preferidos" estarán dentro de sus series respectivas, pero también se puede ver un listado de los últimos episodios añadidos'
    txt += ' por fecha de emisión ó de actualización en los canales.'

    platformtools.dialog_textviewer('Búsqueda automática de nuevos episodios', txt)


def show_help_proxies(item):
    logger.info()

    txt = '[COLOR gold]¿ Porqué en algunos canales hay una opción para configurar proxies ?[/COLOR][CR]'
    txt += 'Ciertos canales sufren bloqueos por parte de algunos países/operadoras que no permiten acceder a su contenido.'
    txt += ' Mediante el uso de proxies se puede evitar esa restricción.'

    txt += '[CR][CR][COLOR gold]¿ En qué canales hay que usar los proxies ?[/COLOR][CR]'
    txt += 'Depende de la conexión de cada usuario (el país dónde se conecta, con qué operadora, qué dns tiene configurados, si usa ó no vpn, ...).'
    txt += ' Lo más aconsejable es probar primero si funcionan sin necesidad de proxies ya que es lo más cómodo y rápido.'
    txt += ' Aunque un canal tenga la opción de proxies no es obligatorio usarlos, hacerlo solamente si es necesario.'

    txt += '[CR][CR][COLOR gold]¿ Se pueden descartar los canales que requieren proxies ?[/COLOR][CR]'
    txt += 'Sí, desde la opción dentro de buscar [COLOR gold]Excluir canales en las búsquedas[/COLOR].'
    txt += 'También, desde el listado de canales de películas y/o series, en el menú contextual se pueden desactivar los canales deseados.'
    txt += ' De esta manera quedarán descartados para las búsquedas globales, se evitarán sus mensajes relacionados con los proxies'
    txt += ' y se acelerará la búsqueda.'

    txt += '[CR][CR][COLOR gold]¿ Cómo se usa la configuración de proxies ?[/COLOR][CR]'
    txt += 'Por defecto en la configuración de Balandro esta activada la opción "Buscar proxies automaticamente" ello efectua un barrido de búsqueda de acuerdo con el proveedor informado.'
    txt += '[CR][CR]'
    txt += 'En la configuración de "Proxies" se pueden personalizar (Dejar de buscar si se hallaron suficientes válidos, Proveedor de proxies habitual, Limitar la cantidad de válidos a memorizar,'
    txt += ' las solicitudes de Anonimidad, País, etc.)'
    txt += '[CR][CR]'
    txt += 'Una vez finalizado el proceso de búsqueda presentará la consola de resultados con varias opciones.'
    txt += '[CR][CR]'
    txt += 'La 1ra opción [COLOR gold]Modificar manualmente[/COLOR] sirve por si se quieren escribir los proxies a usar.'
    txt += ' La 2da opción [COLOR gold]Buscar nuevos proxies[/COLOR] sirve para realizar una búsqueda de proxies que pueden servir para el canal. Los tres más rápidos entre los válidos se guardarán en la configuración del canal.'
    txt += ' La 3ra opción [COLOR gold]Parámetros para buscar[/COLOR] sirve para configurar ciertas opciones para la búsqueda de proxies. Normalmente las opciones por defecto son suficientes pero si fallan se puede probar cambiando algún parámetro (la web de dónde se obtienen, el tipo de proxy, ...).'

    txt += '[CR][CR][COLOR gold]¿ Se ralentizan los canales si se utilizan proxies ?[/COLOR][CR]'
    txt += 'Sí, acceder a las webs de los canales a través de proxies ralentiza considerablemente lo que tardan en responder.'
    txt += ' Aún así, [COLOR yellow]hay proxies más rápidos que otros, ó más estables, ó menos saturados, ó más duraderos, gratuítos ó de pago, etc.[/COLOR]'

    txt += '[CR][CR][COLOR gold]¿ Porqué muchos proxies dejan de funcionar ?[/COLOR][CR]'
    txt += 'Los proxies que se pueden encontrar en la búsqueda [COLOR yellow]son todos gratuítos pero tienen ciertas limitaciones y no siempre están activos.[/COLOR]'
    txt += ' Para cada canal se guardan los proxies a utilizar, pero es posible que algunos días cuando entres tengas que volver a hacer una búsqueda de proxies porque han dejado de funcionar.'

    platformtools.dialog_textviewer('Utilización de proxies', txt)


def show_channels_parameters(item):
    txt = ''

    if config.get_setting('mnu_simple', default=False):
        txt += 'Opera con el Menú [B][COLOR crimson]SIMPLIFICADO[/COLOR][/B]'
        txt += '[CR][CR]'

    channels_list_status = config.get_setting('channels_list_status', default=0)

    if channels_list_status == 0:
        txt += 'Se Muestran [B][COLOR goldenrod]TODOS LOS CANALES[/COLOR][/B]'
    elif channels_list_status == 1:
        txt += 'Se Muestran Solo los canales [B][COLOR goldenrod]PREFERIDOS Y ACTIVOS[/COLOR][/B]'
    else:
        txt += 'Solo se Muestran los canales [B][COLOR goldenrod]PREFERIDOS[/COLOR][/B]'
 
    if config.get_setting('channels_list_order', default=True):
        txt +='[CR][CR]Se Presentan los canales [B][COLOR gold]Preferidos[/COLOR][/B] al principio de las Listas'

    txt += '[CR][CR]'

    txt_disableds = _menu_parameters()

    if txt_disableds:
        txt += 'PERSONALIZACIÓN MENÚS:[CR]'
        txt += txt_disableds

    txt_specials = _menu_specials()

    if txt_specials:
        txt += 'PERSONALIZACIÓN MENÚS Y SUB-MENÚS:[CR]'
        txt += txt_specials

    platformtools.dialog_textviewer('Información Parámetros Actuales para Mostrar los Canales en las Listas', txt)


def _menu_parameters():
    txt_disableds = ''

    if not config.get_setting('mnu_sugeridos', default=True):
        txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú[B][COLOR aquamarine]Sugeridos[/COLOR][/B][CR][CR]'

    if not config.get_setting('channels_link_main', default=True):
        txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR gold]Canales[/COLOR][/B][CR][CR]'

    if not config.get_setting('mnu_idiomas', default=True):
        txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR limegreen]Idiomas[/COLOR][/B][CR][CR]'

    if not config.get_setting('mnu_grupos', default=True):
        txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR magenta]Grupos[/COLOR][/B][CR][CR]'

    if config.get_setting('mnu_simple', default=False):
        txt_disableds += ' - [B][COLOR crimson]Menú Simplificado:[/B][/COLOR][CR]'

        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR wheat]Preferidos[/COLOR][/B][CR]'
        txt_disableds += '     Además no se mostrará en los Menús Contextuales la opción [COLOR darkorange][B]Guardar en Preferidos[/B][/COLOR][CR][CR]'

        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR seagreen]Descargas[/COLOR][/B][CR]'
        txt_disableds += '     Además no se mostrará en los Menús Contextuales la opción [COLOR darkorange][B]Descargar Vídeo[/B][/COLOR][CR][CR]'

        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR deepskyblue]Películas[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR hotpink]Series[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR teal]Películas y Series[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR thistle]Géneros[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR cyan]Documentales[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR lightyellow]Infantiles[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR limegreen]Novelas[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR blue]Torrents[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR firebrick]Doramas[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR springgreen]Animes[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR orange]Adultos[/COLOR][/B][CR]'
        txt_disableds += '   - No se presentará jamás la opción de [B][COLOR gray]Desactivados[/COLOR][/B][CR]'

    else:
        if not config.get_setting('mnu_pelis', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR deepskyblue]Películas[/COLOR][/B][CR][CR]'

        if not config.get_setting('mnu_series', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR hotpink]Series[/COLOR][/B][CR][CR]'

        if config.get_setting('channels_link_pyse', default=False):
            txt_disableds += ' - Tiene [COLOR yellow]Habilitada[/COLOR] la opción del Menú [B][COLOR teal]Películas y Series[/COLOR][/B][CR][CR]'

        if not config.get_setting('mnu_generos', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR thistle]Géneros[/COLOR][/B][CR][CR]'

        if not config.get_setting('mnu_documentales', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR cyan]Documentales[/COLOR][/B][CR]'

            txt_disableds += '   Además no se mostrarán en el resto de Menús los canales que sean [COLOR cyan]Exclusivos de Documentales[/COLOR][CR][CR]'

        if not config.get_setting('mnu_infantiles', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR lightyellow]Infantiles[/COLOR][/B][CR]'

            txt_disableds += '   Además no se mostrarán en el resto de Menús los canales que sean [COLOR lightyellow]Exclusivos de Infantiles[/COLOR][CR][CR]'

        if not config.get_setting('mnu_novelas', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR limegreen]Novelas[/COLOR][/B][CR]'

            txt_disableds += '   Además no se mostrarán en el resto de Menús los canales que sean [COLOR limegreen]Exclusivos de Novelas[/COLOR][CR][CR]'

        if not config.get_setting('mnu_torrents', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR blue]Torrents[/COLOR][/B][CR]'

            txt_disableds += '   Además no se mostrarán en el resto de Menús los canales que sean [COLOR blue]Exclusivos de Torrents[/COLOR][CR][CR]'

        if not config.get_setting('mnu_doramas', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR firebrick]Doramas[/COLOR][/B][CR]'

            txt_disableds += '   Además no se mostrarán en el resto de Menús los canales que sean [COLOR firebrick]Exclusivos de Doramas[/COLOR][CR][CR]'

        if not config.get_setting('mnu_animes', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR springgreen]Animes[/COLOR][/B][CR]'

            txt_disableds += '   Además no se mostrarán en el resto de Menús los canales que sean [COLOR springgreen]Exclusivos de Animes[/COLOR][CR][CR]'

        if not config.get_setting('mnu_adultos', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR orange]Adultos[/COLOR][/B][CR]'

            txt_disableds += '   Además no se mostrarán en el resto de Menús los canales que sean [COLOR orange]Exclusivos para Adultos[/COLOR][CR][CR]'

        if config.get_setting('mnu_desactivados', default=False):
            txt_disableds += ' - Tiene [COLOR yellow]Habilitada[/COLOR] la opción del Menú [B][COLOR gray]Desactivados[/COLOR][/B][CR]'

            txt_disableds += '   Además no se mostrarán en el resto de Menús los canales que esten [COLOR gray]Desactivados[/COLOR][CR][CR]'

        if not config.get_setting('mnu_preferidos', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR wheat]Preferidos[/COLOR][/B][CR][CR]'

            txt_disableds += '   Además no se mostrará en los Menús Contextuales la opción [COLOR darkorange][B]Guardar en Preferidos[/B][/COLOR][CR][CR]'

        if not config.get_setting('mnu_desargas', default=True):
            txt_disableds += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú [B][COLOR seagreen]Descargas[/COLOR][/B][CR][CR]'

            txt_disableds += '   Además no se mostrará en los Menús Contextuales la opción [COLOR darkorange][B]Descargar Vídeo[/B][/COLOR][CR][CR]'

    return txt_disableds


def _menu_specials():
    txt_specials = ''

    if config.get_setting('mnu_search_proxy_channels', default=False):
        txt_specials += ' - Tiene [COLOR yellow]Habilitada[/COLOR] la opción del Menú y Sub-Menús [B][COLOR red]Buscar Nuevos Proxies[/COLOR][/B][CR][CR]'

    if config.get_setting('search_extra_proxies', default=True):
        txt_specials += ' - Tiene [COLOR yellow]Habilitada[/COLOR] la opción del Menú y Sub-Menús [B][COLOR red]Búsquedas en Canales con Proxies[/COLOR][/B][CR][CR]'

    if not config.get_setting('sub_mnu_special', default=True):
        txt_specials += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú y Sub-Menús [B][COLOR pink]Especiales[/COLOR][/B][CR][CR]'

    if config.get_setting('search_extra_main', default=False):
        txt_specials += ' - Tiene [COLOR yellow]Habilitada[/COLOR] la opción del Menú y Sub-Menús [B][COLOR violet]Búsquedas Especiales (Listas TMDB, etc.)[/COLOR][/B][CR][CR]'

    if not config.get_setting('sub_mnu_cfg_search', default=True):
        txt_specials += ' - Tiene [COLOR yellow]Des-habilitada[/COLOR] la opción del Menú y Sub-Menús [B][COLOR moccasin]Personalizar Búsquedas[/COLOR][/B][CR][CR]'

    return txt_specials


def show_menu_parameters(item):
    txt = ''

    if config.get_setting('mnu_simple', default=True):
        txt += 'Opera con el Menú [B][COLOR crimson]SIMPLIFICADO[/COLOR][/B]'
        txt += '[CR][CR]'

    txt_disableds = _menu_parameters()

    if txt_disableds:
        txt += 'PERSONALIZACIÓN MENÚS:[CR]'
        txt += txt_disableds

    txt_specials = _menu_specials()

    if txt_specials:
        txt += 'PERSONALIZACIÓN MENÚS Y SUB-MENÚS:[CR]'
        txt += txt_specials

    platformtools.dialog_textviewer('Información Parámetros Actuales para los Menús', txt)


def show_help_providers(item):
    logger.info()

    txt = ''

    providers_preferred = config.get_setting('providers_preferred', default='')
    if providers_preferred:
        txt = '[COLOR violet]Proveedores preferidos:[/COLOR][CR]'

        txt += '    [COLOR pink]' + str(providers_preferred) + '[/COLOR]'
        txt += '[CR][CR]'

    txt += '[COLOR aquamarine]Proveedores habituales:[/COLOR][CR]'

    txt += ' - [COLOR yellow]clarketm[/COLOR][CR]'
    txt += ' - [COLOR yellow]dailyproxylists.com[/COLOR][CR]'
    txt += ' - [COLOR yellow]free-proxy-list[/COLOR][CR]'
    txt += ' - [COLOR yellow]google-proxy.net[/COLOR][CR]'
    txt += ' - [COLOR yellow]hidemy.name[/COLOR][CR]'
    txt += ' - [COLOR yellow]httptunnel.ge[/COLOR][CR]'
    txt += ' - [COLOR yellow]ip-adress.com[/COLOR][CR]'
    txt += ' - [COLOR yellow]proxy-list.download[/COLOR][CR]'
    txt += ' - [COLOR yellow]proxydb.net[/COLOR][CR]'
    txt += ' - [COLOR yellow]proxynova.com[/COLOR][CR]'
    txt += ' - [COLOR yellow]proxyscrape.com[/COLOR][CR]'
    txt += ' - [COLOR yellow]proxyservers.pro[/COLOR][CR]'
    txt += ' - [COLOR yellow]proxysource.org[/COLOR][CR]'
    txt += ' - [COLOR yellow]silverproxy.xyz[/COLOR][CR]'
    txt += ' - [COLOR yellow]spys.me[/COLOR][CR]'
    txt += ' - [COLOR yellow]spys.one[/COLOR][CR]'
    txt += ' - [COLOR yellow]sslproxies.org[/COLOR][CR]'
    txt += ' - [COLOR yellow]us-proxy.org[/COLOR][CR]'

    txt += '[CR][COLOR cyan]Lista ampliada de proveedores:[/COLOR][CR]'

    txt += ' - [COLOR gold]coderduck[/COLOR][CR]'
    txt += ' - [COLOR gold]echolink[/COLOR][CR]'
    txt += ' - [COLOR gold]free-proxy-list.anon[/COLOR][CR]'
    txt += ' - [COLOR gold]free-proxy-list.com[/COLOR][CR]'
    txt += ' - [COLOR gold]free-proxy-list.uk[/COLOR][CR]'
    txt += ' - [COLOR gold]opsxcq[/COLOR][CR]'
    txt += ' - [COLOR gold]proxy-daily[/COLOR][CR]'
    txt += ' - [COLOR gold]proxyhub[/COLOR][CR]'
    txt += ' - [COLOR gold]proxyranker[/COLOR][CR]'
    txt += ' - [COLOR gold]xroxy[/COLOR][CR]'
    txt += ' - [COLOR gold]socks[/COLOR][CR]'
    txt += ' - [COLOR gold]squidproxyserver[/COLOR][CR]'

    platformtools.dialog_textviewer('Proveedores de proxies', txt)


def show_help_fixes(item):
    logger.info()

    txt = '[CR] Son correcciones del Addon:[CR]'

    txt += ' - [COLOR yellow]Por bugs (errores)[/COLOR][CR]'

    txt += ' - [COLOR yellow]Por cambios menores (nuevos dominios, estructuras, etc.)[/COLOR][CR]'

    txt += '[CR] Y que no tienen la embergadura suficiente como para confeccionar y publicar una nueva versión.[CR]'

    txt += '[CR][COLOR gold] Los Fixes siempre se actualizan automáticamente al iniciar sesión en su Media Center.[/COLOR]'

    platformtools.dialog_textviewer('Información ¿ Qué son los fixes ?', txt)


def show_help_recaptcha(item):
    logger.info()

    txt = '[CR]Son avisos de porqué no se puede reproducir ese enlace en cuestion.[CR]'

    txt += '[CR] Para reproducir ese enlace el servidor exige resolver que no eres un [COLOR gold]Boot[/COLOR], para ello'

    txt += '[CR] presenta un proceso para [COLOR yellow]seleccionar imágenes[/COLOR] (bicicletas, barcos, semáforos, etc.)'

    txt += '[CR][CR]Dada su dificultad [COLOR gold]NO[/COLOR] está contemplado en el Addon esta situación.'

    platformtools.dialog_textviewer('Información ¿ Qué significa Requiere verificación [COLOR red]reCAPTCHA[/COLOR] ?', txt)


def show_version(item):
    logger.info()

    txt = ''

    try:
       with open(os.path.join(config.get_runtime_path(), 'version.txt'), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(config.get_runtime_path(), 'version.txt'), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Información versión', txt)

def show_changelog(item):
    logger.info()

    txt = ''

    try:
       with open(os.path.join(config.get_runtime_path(), 'changelog.txt'), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(config.get_runtime_path(), 'changelog.txt'), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Historial de versiones', txt)

def show_dev_notes(item):
    logger.info()

    txt = ''

    try:
       with open(os.path.join(config.get_runtime_path(), 'dev-notes.txt'), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(config.get_runtime_path(), 'dev-notes.txt'), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Notas para developers', txt)

def show_todo_log(item):
    logger.info()

    path = os.path.join(config.get_data_path(), item.todo)

    existe = filetools.exists(path)

    if not existe:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún No hay el fichero Log[/COLOR][/B]' % color_alert)
        return

    txt = ''

    try:
        with open(path, 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(path, encoding="utf8").read()
        except: pass

    if txt:
        platformtools.dialog_textviewer('Fichero Log ' + item.todo, txt)
    else:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Información[/COLOR][/B]' % color_alert)

def show_log(item):
    logger.info()

    loglevel = config.get_setting('debug', 0)
    if not loglevel >= 2:
        if not platformtools.dialog_yesno(config.__addon_name, 'El nivel actual de información del fichero LOG de su Media Center NO esta configurado al máximo. ¿ Desea no obstante visualizarlo ?'): 
            return

    path = translatePath(os.path.join('special://logpath/', ''))

    file_log = 'kodi.log'

    file = path + file_log

    existe = filetools.exists(file)

    if existe == False:
        files = filetools.listdir(path)
        for file_log in files:
            if file_log.endswith('.log') == True:
                file = path + file_log
                existe = filetools.exists(file)
                break

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se localiza su fichero Log[/COLOR][/B]' % color_alert)
        return

    size = filetools.getsize(file)
    if size > 999999: platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Cargando fichero log[/COLOR][/B]' % color_infor)

    txt = ''

    try:
        with open(os.path.join(path, file_log), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(path, file_log), encoding="utf8").read()
        except: pass

    if config.get_setting('developer_mode', default=False):
        txt = txt.replace('Balandro.', '[COLOR yellow][B]Balandro[/B][/COLOR].')
        txt = txt.replace('Balandro ', '[COLOR yellow][B]Balandro[/B][/COLOR] ')
        txt = txt.replace('balandro.', '[COLOR yellow][B]Balandro[/B][/COLOR].')
        txt = txt.replace('balandro ', '[COLOR yellow][B]Balandro[/B][/COLOR] ')

    if txt: platformtools.dialog_textviewer('Fichero LOG de su Media Center', txt)


def copy_log(item):
    logger.info()

    loglevel = config.get_setting('debug', 0)
    if not loglevel >= 2:
        if not platformtools.dialog_yesno(config.__addon_name, 'El nivel actual de información del fichero LOG de su Media Center NO esta configurado al máximo. [B][COLOR %s]¿ Desea no obstante obtener una Copia ?[/B][/COLOR]' % color_infor):
            return

    path = translatePath(os.path.join('special://logpath/', ''))

    file_log = 'kodi.log'

    file = path + file_log

    existe = filetools.exists(file)

    if existe == False:
        files = filetools.listdir(path)
        for file_log in files:
            if file_log.endswith('.log') == True:
                file = path + file_log
                existe = filetools.exists(file)
                break

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se localiza su fichero Log[/COLOR][/B]' % color_alert)
        return

    destino_path = xbmcgui.Dialog().browseSingle(3, 'Seleccionar carpeta dónde copiar', 'files', '', False, False, '')
    if not destino_path: return

    origen = os.path.join(path, file_log)
    destino = filetools.join(destino_path, file_log)
    if not filetools.copy(origen, destino, silent=False):
        platformtools.dialog_ok(config.__addon_name, 'Error, no se ha podido copiar el fichero Log!', origen, destino)
        return

    platformtools.dialog_notification('Fichero Log copiado', file_log)

    time.sleep(0.5)

    loglevel = config.get_setting('debug', 0)
    if not loglevel == 0:
        if not platformtools.dialog_yesno(config.__addon_name, 'La configuración actual del nivel de información del fichero LOG de su Media Center REDUCE el rendimiento de su equipo. [B][COLOR %s]¿ Desea mantener ese Nivel de información ?[/B][/COLOR]' % color_avis):
            config.set_setting('debug', '0')

def show_advs(item):
    logger.info()

    path = translatePath(os.path.join('special://home/userdata', ''))

    file_advs = 'advancedsettings.xml'

    file = path + file_advs

    existe = filetools.exists(file)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero Advancedsettings[/COLOR][/B]' % color_infor)
        return

    txt = ''

    try:
       with open(os.path.join(path, file_advs), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(path, file_advs), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Su fichero Advancedsettings de su Media Center', txt)


def show_yourlist(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'Lista-proxies.txt')

    existe = filetools.exists(path)

    if not existe:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún No hay el fichero de Lista de Proxies[/COLOR][/B]' % color_alert)
        return

    txt = ''

    try:
        with open(path, 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(path, encoding="utf8").read()
        except: pass

    if txt:
        platformtools.dialog_textviewer('Fichero Lista de Proxies', txt)
    else:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin Información[/COLOR][/B]' % color_alert)


def show_help_adults(item):
    logger.info()

    txt = '*) Las webs podrian, en algún caso, publicar Vídeos con contenido [COLOR gold]No Apto[/COLOR] para menores.'
    txt += ' Balandro cuenta con un apartado en su configuración exclusivo para el [COLOR gold]Control Parental[/COLOR].'
    txt += ' (por defecto este apartado está [COLOR gold]Habilitado[/COLOR]).'

    txt += '[CR][CR]'
    txt += '*) Pero no se puede garantizar que todo el material de este tipo se filtre correctamente en determinadas ocasiones.'

    platformtools.dialog_textviewer('Control Parental', txt)


def show_help_torrents(item):
    logger.info()

    txt = '*) A través de un navegador web localize e instale al menos uno de los add-ons de la lista que más se adapte a'
    txt += '  sus necesidades y que sea a su vez compatible con su Media Center.'

    txt += '[CR][CR]'
    txt += '*) Add-Ons:[CR]'
    txt += '    - plugin.video.elementum[CR]'
    txt += '    - plugin.video.torrest[CR]'
    txt += '    - plugin.video.torrenter[CR]'
    txt += '    - plugin.video.torrentin[CR]'
    txt += '    - plugin.video.quasar[CR]'
    txt += '    - plugin.video.pulsar[CR]'
    txt += '    - plugin.video.stream[CR]'
    txt += '    - plugin.video.xbmctorrent'

    txt += '[CR][CR]'
    txt += '*) A modo de ejemplo para [COLOR gold]Elementum[/COLOR] puede acceder a su web oficial en [COLOR gold]elementum.surge.sh[/COLOR]'

    txt += '[CR][CR]'
    txt += '*) Existen múltiples sitios webs en donde puede localizar estos add-ons, entre estos sitios le recomendamos'
    txt += '   acceda a este [COLOR gold]fuentekodileia.github.io[/COLOR]'

    platformtools.dialog_textviewer('¿ Dónde obtener los add-ons para torrents ?', txt)


def show_legalidad(item):
    logger.info()

    txt = '[COLOR yellow]*)[B] Balandro [COLOR moccasin][B] es Totalmente [I] GRATUITO [/I], si Pagó por este Add-On le [I] ENGAÑARON, [/I][/B][/COLOR]'
    txt += '[COLOR lightblue][B] y tiene como objeto, permitir visualizar Películas, Series, Documentales, etc... [/B][/COLOR]'
    txt += '[COLOR lightblue][B] Todo a través de Internet y directamente desde su Sistema Media Center.[/B][/COLOR]'

    txt += '[CR][CR][COLOR orchid][B] Este Add-On es tan solo un mero Ejercicio de Aprendizaje del Lenguaje de Programación Python y se distribuye sin Ningún Contenido Multimedia adjunto al mismo.[/B][/COLOR]'
    txt += '[COLOR lightgrey][B][I] En consecuencia solo Las Webs son plenamente Responsables de los Contenidos que Publiquen [/I][/B][/COLOR]'

    txt += '[CR][CR][COLOR tan][B] Úselo de acuerdo con su Criterio y bajo su Responsabilidad,[/B][/COLOR]'
    txt += '[COLOR tan][B] sus Creadores quedarán Totalmente Eximidos de toda Repercusión Legal, si se Re-Distribuye solo ó con acceso a Contenidos Protegidos por los Derechos de Autor, sin el Permiso Explícito de estos mismos.[/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR chocolate][B][I] Si este tipo de contenido está Prohibido en su País, solamente Usted será el Responsable de su uso.[/I][/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR mediumaquamarine][B] Este Add-On es un proyecto sin ánimo de Lucro y con Fines Educativos, por lo tanto está Prohibida su Venta en solitario ó como parte de Software Integrado en cualquier dispositivo, es exclusivamente para un uso Docente y Personal.[/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR chartreuse][B] Vesiones de este Add-On desde el año 2018.[/B][/COLOR]'

    txt += '[CR][CR]*)[COLOR red][B][I] Queda totalmente Prohibida su Re-Distribución, sin la Autorización Fehaciente de sus Creadores.[/I][/B][/COLOR]'

    platformtools.dialog_textviewer('Cuestiones Legales', txt)


def show_license(item):
    logger.info()

    txt = ''
    try:
       with open(os.path.join(config.get_runtime_path(), 'LICENSE'), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(config.get_runtime_path(), 'LICENSE'), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Licencia (Gnu Gpl v3)', txt)


def show_test(item):
    from core import httptools, channeltools, scrapertools

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Cargando información sistema[/B][/COLOR]' % color_infor)

    your_ip = ''

    try:
       import re
       data = httptools.downloadpage('http://httpbin.org/ip').data
       data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
       your_ip = scrapertools.find_single_match(str(data), '.*?"origin".*?"(.*?)"')
    except:
       pass

    if not your_ip:
        try: your_ip = httptools.downloadpage('http://ipinfo.io/ip').data
        except: pass

    if not your_ip:
        try: your_ip = httptools.downloadpage('http://www.icanhazip.com/').data
        except: pass

    if not your_ip:
	    platformtools.dialog_ok(config.__addon_name, '[COLOR red]Parece que NO hay conexión con internet.[/COLOR]', 'Compruebelo realizando cualquier Búsqueda, desde un Navegador Web ')

    hay_repo = False
    if xbmc.getCondVisibility('System.HasAddon("%s")' % 'repository.balandro'): hay_repo = True

    access_repo = False
    tex_access_repo = ''
    if hay_repo:
        try:
           data = httptools.downloadpage(ADDON_REPO_ADDONS).data
           if data: access_repo = True
        except: tex_access_repo = '[COLOR lightblue][B]No se pudo comprobar[/B][/COLOR]'

    ult_ver = ''

    access_last_ver = False

    if hay_repo:
        if access_repo:
            try: ult_ver = updater.check_addon_version()
            except: pass

            if ult_ver: access_last_ver = True

    access_fixes = False
    tex_access_fixes = ''
    if hay_repo:
        if access_repo:
            try:
               data = httptools.downloadpage(ADDON_UPDATES_JSON).data
               if data:
                   access_fixes = True
                   if 'addon_version' not in data or 'fix_version' not in data: access_fixes = None
            except: tex_access_fixes = '[COLOR lightblue][B]No se pudo comprobar[/B][/COLOR]'

    txt = '[CR][CR][COLOR fuchsia]BALANDRO[/COLOR][CR]'

    if not your_ip: your_ip = '[COLOR red][B] Sin Conexión [/B][/COLOR]'

    txt += ' - [COLOR gold]Conexión internet:[/COLOR]  %s ' % your_ip
    txt += '[CR][CR]'

    tex_repo = ' Instalado'
    if hay_repo == False: tex_repo = '[I][B][COLOR %s] No instalado, No recibirá más versiones [/COLOR][/B][/I]' % color_adver

    txt += ' - [COLOR gold]Repositorio:[/COLOR]  %s ' % tex_repo
    txt += '[CR][CR]'
    tex_access_repo = ' Accesible'
    if access_repo == False:
        if tex_access_repo == '': tex_access_repo = '[COLOR red][B] Sin conexión, No accesible [/B][/COLOR]'

    txt += ' - [COLOR gold]Conexión con repositorio:[/COLOR]  %s ' % tex_access_repo
    txt += '[CR][CR]'

    if access_last_ver: tex_access_last_ver = ' Versión correcta '
    else:
        if not ult_ver:
            if not access_repo: tex_access_last_ver = '[I][B][COLOR %s] No accesible [/COLOR][/B][/I]' % color_adver
            else: tex_access_last_ver = '[I][B][COLOR %s] Accesible desde Repositorio [/COLOR][/B][/I]' % color_adver
        else: tex_access_last_ver = '[I][B][COLOR %s] (desfasada)[/COLOR][/B][/I]' % color_adver

    txt += ' - [COLOR gold]Última versión:[/COLOR]  %s ' % tex_access_last_ver
    txt += '[CR][CR]'

    if not tex_access_fixes:
        tex_access_fixes = ' Accesibles'
        if access_fixes == None: tex_access_fixes = '[COLOR yellow] Sin actualizaciones tipo Fix pendientes [/COLOR]'
        elif access_fixes == False: tex_access_fixes = '[I][B][COLOR %s] Fixes sobre última versión, No accesibles [/COLOR][/B][/I]' % color_adver

    txt += ' - [COLOR gold]Fixes sobre última versión:[/COLOR]  %s ' % tex_access_fixes
    txt += '[CR][CR]'

    txt += ' - [COLOR gold]Versión instalada:[/COLOR]  [COLOR yellow][B]%s[/B][/COLOR]' % config.get_addon_version()
    if not ult_ver:
        if not access_repo: txt = txt + '[I][COLOR %s] (Sin repositorio)[/COLOR][/I]' % color_adver
        else: txt = txt + '[I][COLOR %s] (desfasada)[/COLOR][/I]' % color_adver

    txt += '[CR][CR]'

    folder_down = config.get_setting('downloadpath', default='')
    if not folder_down == '':
        txt += ' - [COLOR gold]Carpeta descargas:[/COLOR]  [COLOR moccasin]%s[/COLOR]' % folder_down
        txt += '[CR][CR]'

    tex_dom = ''

    hdfull_dominio = config.get_setting('channel_hdfull_dominio', default='')
    if hdfull_dominio: tex_dom = tex_dom + hdfull_dominio

    dontorrents_dominio = config.get_setting('channel_dontorrents_dominio', default='')
    if dontorrents_dominio:
       if tex_dom: tex_dom = tex_dom + '  ' + dontorrents_dominio
       else: tex_dom = dontorrents_dominio

    if tex_dom:
        txt += ' - [COLOR gold]Dominios:[/COLOR]  [COLOR springgreen]%s[/COLOR]' % str(tex_dom).replace('https://', '').replace('/', '')
        txt += '[CR][CR]'

    filtros = {'searchable': True}
    opciones = []

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if ch_list:
       txt_ch = ''

       for ch in ch_list:
           cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'

           if not config.get_setting(cfg_proxies_channel, default=''): continue

           txt_ch += '[COLOR red]%s[/COLOR]  ' % ch['name']

       if not txt_ch: txt_ch = 'No hay canales con proxies' 
       txt += ' - [COLOR gold]Proxies:[/COLOR]  %s' % str(txt_ch)

    txt_exc = ''

    if config.get_setting('search_excludes_movies', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR deepskyblue][B]Películas[/B][/COLOR] ' + config.get_setting('search_excludes_movies') + '[CR]'
    if config.get_setting('search_excludes_tvshows', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR hotpink][B]Series[/B][/COLOR] ' + config.get_setting('search_excludes_tvshows') + '[CR]'
    if config.get_setting('search_excludes_documentaries', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR cyan][B]Documentales[/B][/COLOR] ' + config.get_setting('search_excludes_documentaries') + '[CR]'
    if config.get_setting('search_excludes_torrents', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR blue][B]Torrents[/B][/COLOR] ' + config.get_setting('search_excludes_torrents') + '[CR]'
    if config.get_setting('search_excludes_mixed', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR yellow][B]Películas y/ó Series[/B][/COLOR] ' + config.get_setting('search_excludes_mixed') + '[CR]'
    if config.get_setting('search_excludes_all', default=''):
        txt_exc += ' - [COLOR gold]Excluir Buscar:[/COLOR] [COLOR green][B]Todos[/B][/COLOR] ' + config.get_setting('search_excludes_all') + '[CR]'

    if txt_exc:
       txt += '[CR][CR]'
       txt += txt_exc
	
    cliente_torrent = config.get_setting('cliente_torrent', default='Ninguno')
    if cliente_torrent == 'Ninguno': tex_tor = '[COLOR moccasin]Ninguno[/COLOR]'
    elif cliente_torrent == 'Seleccionar':  tex_tor = 'Seleccionar'
    else:
      tex_tor = cliente_torrent
      cliente_torrent = 'plugin.video.' + cliente_torrent.lower()
      if xbmc.getCondVisibility('System.HasAddon("%s")' % cliente_torrent): tex_tor += '  Instalado'
      else: tex_tor += '  [COLOR red][B]No instalado[/B][/COLOR]'

    if not txt_exc: txt += '[CR]'

    txt += '[CR] - [COLOR gold]Cliente/Motor torrent:[/COLOR]  %s' % tex_tor

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.youtube")'): tex_yt = '  Instalado'
    else: tex_yt = '  [COLOR red][B]No instalado[/B][/COLOR]'

    txt += '[CR][CR] - [COLOR gold]YouTube addon:[/COLOR]  %s' % tex_yt

    if xbmc.getCondVisibility('System.HasAddon("script.module.resolveurl")'): tex_yt = '  Instalado'
    else: tex_yt = '  [COLOR red][B]No instalado[/B][/COLOR]'

    txt += '[CR][CR] - [COLOR gold]ResolveUrl script:[/COLOR]  %s' % tex_yt

    loglevel = config.get_setting('debug', 0)
    if loglevel == 0: tex_niv = 'Solo Errores'
    elif loglevel == 1: tex_niv = 'Errores e Información'
    else: tex_niv = 'Máxima Información'

    txt += '[CR][CR] - [COLOR gold]Log:[/COLOR]  %s' % tex_niv

    plataforma = get_plataforma('')

    txt += plataforma

    if not ult_ver:
        if not access_repo:
            platformtools.dialog_ok(config.__addon_name, 'Versión instalada sin repositorio[COLOR coral][B] ' + config.get_addon_version() + '[/B][/COLOR]', '[COLOR yellow][B] Instale la última Versión del Repositorio [/COLOR][/B]')
        else:
            platformtools.dialog_ok(config.__addon_name, 'Versión instalada desfasada[COLOR coral][B] ' + config.get_addon_version() + '[/B][/COLOR]', '[COLOR yellow][B] Instale la última Versión disponible del Add-On[/COLOR][/B]')

    platformtools.dialog_textviewer('Test status sistema', txt)


def show_plataforma(item):
    logger.info()

    plataforma = get_plataforma('')

    txt = plataforma

    platformtools.dialog_textviewer('Información sobre su Plataforma', txt)


def get_plataforma(txt):
    logger.info()

    txt += '[CR][CR][COLOR fuchsia]PLATAFORMA[/COLOR][CR]'

    txt += ' - [COLOR gold]Media center:[/COLOR]  [COLOR coral]%s[/COLOR]' % str(xbmc.getInfoLabel('System.BuildVersion'))
    txt += '[CR][CR]'

    plataforma = platform.uname()

    txt += ' - [COLOR gold]Sistema:[/COLOR]  %s-%s-%s' % (str(plataforma[0]), str(plataforma[2]), str(plataforma[3]))
    txt += '[CR][CR]'

    txt += ' - [COLOR gold]Python:[/COLOR]  %s.%s.%s' % (str(sys.version_info[0]), str(sys.version_info[1]), str(sys.version_info[2]))
    txt += '[CR][CR]'

    return txt


def show_last_fix(item):
    logger.info()

    path = os.path.join(config.get_runtime_path(), 'last_fix.json')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero Fix[/COLOR][/B]' % color_infor)
        return

    txt = ''

    try:
       with open(path, 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(path, encoding="utf8").read()
        except: pass

    if txt:
       txt = txt.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(',', '').replace('"', '').replace("'", '').strip()
       platformtools.dialog_textviewer('Información del último Fix instalado', txt)


def show_sets(item):
    logger.info()

    file_sets = os.path.join(config.get_data_path(), "settings.xml")

    existe = filetools.exists(file_sets)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No existe settings.xml[/COLOR][/B]' % color_alert)
        return

    txt = ''
    try:
       with open(os.path.join(file_sets), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(file_sets), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Su fichero de Ajustes personalizados', txt)

def show_cook(item):
    logger.info()

    file_cook = os.path.join(config.get_data_path(), "cookies.dat")

    existe = filetools.exists(file_cook)

    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No existe cookies.dat[/COLOR][/B]' % color_adver)
        return

    txt = ''

    try:
       with open(os.path.join(file_cook), 'r') as f: txt=f.read(); f.close()
    except:
        try: txt = open(os.path.join(file_cook), encoding="utf8").read()
        except: pass

    if txt: platformtools.dialog_textviewer('Su fichero de Cookies', txt)

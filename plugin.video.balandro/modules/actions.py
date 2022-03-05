# -*- coding: utf-8 -*-

import os, re
import xbmcgui, xbmc

from platformcode import config, logger, platformtools
from core import filetools

from core.item import Item


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis  = config.get_setting('notification_avis_color', default='yellow')
color_exec  = config.get_setting('notification_exec_color', default='cyan')


def open_settings(item):
    logger.info()

    config.__settings__.openSettings()

    platformtools.itemlist_refresh()


def _marcar_canales(item):
    cfg_cchannel_status = 'channel_' + item.canal + '_status'
    status = config.get_setting(cfg_cchannel_status, default='')

    if status:
        ant_tipo = 'Activo'
        if status == 1: ant_tipo = 'Preferido'
        if status == -1: ant_tipo = 'Desactivado'

    new_tipo = 'Activo'
    if item.estado == 1: new_tipo = 'Preferido'
    if item.estado == -1: new_tipo = 'Desactivado'

    if status:
        if ant_tipo == new_tipo:
            el_canal = ('Sin cambio en [B][COLOR %s] %s [COLOR %s] ' + item.canal.capitalize() + '[/COLOR][/B]') % (color_exec, new_tipo, color_infor)
            platformtools.dialog_notification(config.__addon_name, el_canal)
            return

        if not platformtools.dialog_yesno(config.__addon_name + ' - ' + item.canal.capitalize(), '[COLOR red]¿ Confirma cambiar la personalización del canal ?[/COLOR]', 'de:  [COLOR cyan]' + ant_tipo + '[/COLOR]', 'a:    [COLOR yellow]' + new_tipo + '[/COLOR]'): 
            return

    config.set_setting('status', item.estado, item.canal)
	
    el_canal = ('Cambiado a [B][COLOR %s] %s [COLOR %s] ' + item.canal.capitalize() + '[/COLOR][/B]') % (color_exec, new_tipo, color_avis)
    platformtools.dialog_notification(config.__addon_name, el_canal)


def comprobar_nuevos_episodios(item):
    logger.info()

    la_notif = ('[B][COLOR %s]') % color_infor
    la_notif += ('Comprobando existencia nuevos episodios[/B][/COLOR]')
    platformtools.dialog_notification(config.__addon_name, la_notif, time=2000, sound=False)

    from core import trackingtools
    trackingtools.check_and_scrap_new_episodes()


def check_addon_updates(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando actualizaciones[/B][/COLOR]' % color_infor)

    from platformcode import updater
    updater.check_addon_updates(verbose=True)

    platformtools.itemlist_refresh()


def check_addon_updates_force(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Forzando actualizaciones[/B][/COLOR]' % color_avis)

    from platformcode import updater
    updater.check_addon_updates(verbose=True, force=True)

    platformtools.itemlist_refresh()


def drop_db_cache(item):
    logger.info()

    if platformtools.dialog_yesno('Borrar Caché Tmdb', '[COLOR red]¿ Eliminar Todos los registros de la caché de Tmdb ?[/COLOR]'): 
        from core import tmdb
        if tmdb.drop_bd():
            platformtools.dialog_notification(config.__addon_name, 'Caché Tmdb borrada', time=2000, sound=False)


def clean_db_cache(item):
    logger.info()

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Inspeccionado la Caché de Tmdb[/B][/COLOR]' % color_infor)

    import sqlite3, time

    fecha_caducidad = time.time() - (31 * 24 * 60 * 60)

    fname = filetools.join(config.get_data_path(), "tmdb.sqlite")
    conn = sqlite3.connect(fname)
    c = conn.cursor()

    c.execute('SELECT COUNT() FROM tmdb_cache')
    numregs = c.fetchone()[0]

    c.execute('SELECT COUNT() FROM tmdb_cache WHERE added < ?', (fecha_caducidad,))
    numregs_expired = c.fetchone()[0]

    txt = 'El caché de Tmdb ocupa [COLOR gold]%s[/COLOR]' % config.format_bytes(filetools.getsize(fname))
    txt += ' y contiene [COLOR gold]%s[/COLOR] registros.' % numregs
    txt += ' ¿ Borrar los [COLOR blue]%s[/COLOR] registros que tienen más de un mes de antiguedad de Tmdb ?' % numregs_expired

    if platformtools.dialog_yesno('Limpiar la caché de Tmdb', txt): 
        c.execute('DELETE FROM tmdb_cache WHERE added < ?', (fecha_caducidad,))
        conn.commit()
        conn.execute('VACUUM')
        platformtools.dialog_notification(config.__addon_name, 'Limpiada Caché Tmdb', time=2000, sound=False)

    conn.close()


def more_info(item):
    logger.info()

    # Si  menú contextual, recuperar parámetros action y channel
    if item.from_action: item.__dict__['action'] = item.__dict__.pop('from_action')
    if item.from_channel: item.__dict__['channel'] = item.__dict__.pop('from_channel')

    from core import tmdb

    tmdb.set_infoLabels_item(item)

    xlistitem = xbmcgui.ListItem()
    platformtools.set_infolabels(xlistitem, item, True)

    ret = xbmcgui.Dialog().info(xlistitem)


def search_trailers(item):
    logger.info()

    from core.tmdb import Tmdb

    tipo = 'movie' if item.contentType == 'movie' else 'tv'
    nombre = item.contentTitle if item.contentType == 'movie' else item.contentSerieName
    if item.infoLabels['tmdb_id']:
        tmdb_search = Tmdb(id_Tmdb=item.infoLabels['tmdb_id'], tipo=tipo, idioma_busqueda='es')
    else:
        anyo = item.infoLabels['year'] if item.infoLabels['year'] else '-'
        tmdb_search = Tmdb(texto_buscado=nombre, tipo=tipo, year=anyo, idioma_busqueda='es')

    opciones = []
    resultados = tmdb_search.get_videos()
    for res in resultados:
        it = xbmcgui.ListItem(res['name'], '[%sp] (%s)' % (res['size'], res['language']))
        if item.thumbnail: it.setArt({ 'thumb': item.thumbnail })
        opciones.append(it)

    if len(resultados) == 0:
        notification_d_ok = config.get_setting('notification_d_ok', default=True)
        if notification_d_ok:
            platformtools.dialog_ok(nombre, 'No se encuentra ningún tráiler en TMDB')
        else:
            platformtools.dialog_notification(nombre, '[B][COLOR %s]Sin tráiler en TMDB[/COLOR][/B]' % color_alert)
    else:
        while not xbmc.Monitor().abortRequested():
            ret = xbmcgui.Dialog().select('Tráilers para %s' % nombre, opciones, useDetails=True)
            if ret == -1: break

            platformtools.dialog_notification(resultados[ret]['name'], 'Cargando tráiler ...', time=3000, sound=False)

            from core import servertools

            if 'youtube' in resultados[ret]['url']:
                video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing('youtube', resultados[ret]['url'])
            else:
                video_urls = []
                logger.info("check-resultados: %s" % resultados[ret])

            if len(video_urls) > 0:
                xbmc.Player().play(video_urls[0][1])
                xbmc.sleep(1000)
                while not xbmc.Monitor().abortRequested() and xbmc.Player().isPlaying():
                    xbmc.sleep(1000)
            else:
                la_notif = ('[B][COLOR %s]') % color_alert
                la_notif += ('No se pudo reproducir el tráiler[/B][/COLOR]')

                platformtools.dialog_notification(resultados[ret]['name'], la_notif, time=3000, sound=False)

            if len(resultados) == 1: break


def global_proxies(item):
    logger.info()

    from modules import proxysearch

    proxysearch.proxysearch_all(item)


def manto_proxies(item):
    logger.info()

    from core import channeltools

    filtros = {'searchable': True}

    ch_list = channeltools.get_channels_list(filtros=filtros)

    if not ch_list:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Sin canales de este tipo[/B][/COLOR]' % color_adver)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma Eliminar los Proxies memorizados en Todos los canales que los tengan?[/COLOR]'):
       for ch in ch_list:
           if not 'proxies' in ch['notes'].lower():
               continue

           # por NAME anteriores a 2.0
           cfg_proxies_channel = 'channel_' + ch['name'] + '_proxies'

           if config.get_setting(cfg_proxies_channel, default=''):
               config.set_setting(cfg_proxies_channel, '')

               cfg_proxytools_max_channel = 'channel_' + ch['name'] + '_proxytools_max'
               if config.get_setting(cfg_proxytools_max_channel, default=''): config.set_setting(cfg_proxytools_max_channel, '')

               cfg_proxytools_provider = 'channel_' + ch['name'] + '_proxytools_provider'
               if config.get_setting(cfg_proxytools_provider, default=''): config.set_setting(cfg_proxytools_provider, '')

           # por ID
           cfg_proxies_channel = 'channel_' + ch['id'] + '_proxies'
           cfg_proxytools_max_channel = 'channel_' + ch['id'] + '_proxytools_max'
           cfg_proxytools_provider = 'channel_' + ch['id'] + '_proxytools_provider'

           if not config.get_setting(cfg_proxies_channel, default=''):
               if not config.get_setting(cfg_proxytools_max_channel, default=''):
                   if not config.get_setting(cfg_proxytools_provider, default=''):
                       continue

           if config.get_setting(cfg_proxies_channel, default=''): config.set_setting(cfg_proxies_channel, '')
           if config.get_setting(cfg_proxytools_max_channel, default=''): config.set_setting(cfg_proxytools_max_channel, '')
           if config.get_setting(cfg_proxytools_provider, default=''): config.set_setting(cfg_proxytools_provider, '')

       config.set_setting('channels_proxies_memorized', '')

       platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Proxies eliminados[/B][/COLOR]' % color_infor)


def last_domain_hdfull(item):
    logger.info()

    from core import httptools, scrapertools, jsontools

    platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Comprobando dominio[/B][/COLOR]' % color_exec)

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

    try:
       data = httptools.downloadpage('https://hdfullcdn.cc/login').data
       last_domain = scrapertools.find_single_match(data, 'location.replace.*?"(.*?)"')
       if last_domain:
           last_domain = last_domain.replace('login', '')
           if not last_domain.endswith('/'):
               last_domain = last_domain + '/'
    except:
      last_domain = ''

    if not last_domain:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No se pudo comprobar[/B][/COLOR]' % color_alert)
        return

    domain = config.get_setting('dominio', 'hdfull', default='')

    if domain == last_domain:
        platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR yellow]El último dominio vigente es correcto.', '[COLOR cyan][B]' + last_domain + '[/B][/COLOR]')
        return

    if platformtools.dialog_yesno(config.__addon_name + ' - HdFull', '¿ [COLOR red] Último dominio memorizado incorrecto. [/COLOR] Desea cambiarlo  ?','Memorizado:  [COLOR yellow][B]' + domain + '[/B][/COLOR]', 'Vigente:           [COLOR cyan][B]' + last_domain + '[/B][/COLOR]'): 
        config.set_setting('dominio', last_domain, 'hdfull')

        if not item.desde_el_canal:
            if not item.from_action == 'mainlist':
                platformtools.dialog_ok(config.__addon_name + ' - HdFull', '[COLOR yellow]Ultimo dominio vigente memorizado, pero aún NO guardado.', '[COLOR cyan][B]Recuerde, que para que el cambio surta efecto deberá abandonar la configuración/ajustes de Balandro a través de su correspondiente botón --> OK[/B][/COLOR]')

def del_datos_hdfull(item):
    logger.info()

    username = config.get_setting('hdfull_username', 'hdfull', default='')
    password = config.get_setting('hdfull_password', 'hdfull', default='')

    if not username or not password:
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma eliminar sus credenciales de HdFull ?[/COLOR]'):
        config.set_setting('channel_hdfull_hdfull_login', False)
        config.set_setting('channel_hdfull_hdfull_password', '')
        config.set_setting('channel_hdfull_hdfull_username', '')


def del_datos_playdede(item):
    logger.info()

    username = config.get_setting('playdede_username', 'playdede', default='')
    password = config.get_setting('playdede_password', 'playdede', default='')

    if not username or not password:
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma eliminar sus credenciales de PlayDede ?[/COLOR]'):
        config.set_setting('channel_playdede_playdede_login', False)
        config.set_setting('channel_playdede_playdede_password', '')
        config.set_setting('channel_playdede_playdede_username', '')


def manto_params(item):
    logger.info()

    if platformtools.dialog_yesno(config.__addon_name, "Se quitarán: 'Logins' en canales, 'Dominios' seleccionados en los canales, 'Canales Excluidos' en búsquedas, 'Canales Excluidos' en buscar proxies global, y se Inicializarán otros 'Parámetros'.", '[COLOR yellow]¿ Confirma Restablecer a sus valores por defecto los Parámetros Internos del addon ?[/COLOR]'):
        config.set_setting('adults_password', '')

        config.set_setting('channel_documaniatv_rua', '')

        config.set_setting('channel_hdfull_dominio', '')
        config.set_setting('channel_hdfull_hdfull_login', False)
        config.set_setting('channel_hdfull_hdfull_password', '')
        config.set_setting('channel_hdfull_hdfull_username', '')

        config.set_setting('channel_playdede_playdede_login', False)
        config.set_setting('channel_playdede_playdede_password', '')
        config.set_setting('channel_playdede_playdede_username', '')

        config.set_setting('channels_proxies_memorized', '')

        config.set_setting('search_excludes_movies', '')
        config.set_setting('search_excludes_tvshows', '')
        config.set_setting('search_excludes_documentaries', '')
        config.set_setting('search_excludes_mixed', '')
        config.set_setting('search_excludes_all', '')

        config.set_setting('proxysearch_excludes', '')

        # ~ config.set_setting('downloadpath', '')  No funciona

        config.set_setting('chrome_last_version', '98.0.4758.80')

        config.set_setting('debug', '0')

        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Parámetros restablecidos[/B][/COLOR]' % color_infor)

def manto_cookies(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'cookies.dat')

    existe = filetools.exists(path)
    if existe == False:
         platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]No hay fichero de Cookies[/COLOR][/B]' % color_alert)
         return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma Eliminar el fichero de Cookies ?[/COLOR]'):
        filetools.remove(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Fichero Cookies eliminado[/B][/COLOR]' % color_infor)

def manto_folder_cache(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'cache')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no hay Carpeta Caché[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma Eliminar Toda la carpeta Caché ?[/COLOR]'):
        filetools.rmdirtree(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Carpeta Caché eliminada[/B][/COLOR]' % color_infor)

def manto_tracking_dbs(item):
    logger.info()

    path = os.path.join(config.get_data_path(), 'tracking_dbs')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Preferidos[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma Eliminar Todo el contenido de sus Preferidos ?[/COLOR]'):
        filetools.rmdirtree(path)
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Contenido Preferidos eliminado[/B][/COLOR]' % color_infor)

def manto_folder_downloads(item):
    logger.info()

    downloadpath = config.get_setting('downloadpath', default='')

    if downloadpath:
        path = downloadpath
    else:
        path = os.path.join(config.get_data_path(), 'downloads')

    existe = filetools.exists(path)
    if existe == False:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Descargas[/COLOR][/B]' % color_exec)
        return

    if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ Confirma Eliminar el contenido de Todas sus Descargas ?[/COLOR]'):
        filetools.rmdirtree(path)

        # por si varió el path y quedaron descargas huerfanas en el path default
        if downloadpath:
           try:
              path = os.path.join(config.get_data_path(), 'downloads')
              filetools.rmdirtree(path)
           except:
              pass

        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Contenido Descargas eliminado[/B][/COLOR]' % color_infor)

def manto_folder_addon(item):
    logger.info()

    path = config.get_data_path()

    existe = filetools.exists(path)
    if not existe == False:
        if platformtools.dialog_yesno(config.__addon_name, '[COLOR red]¿ ATENCION: Confirma Eliminar Todos los Datos del Addon ?[/COLOR]'):
            # ~  deja solo settings.xml lo tiene bloqueado el sistema
            filetools.rmdirtree(path)
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Datos del Addon eliminados[/B][/COLOR]' % color_adver)

def adults_password(item):
    logger.info()

    if not config.get_setting('adults_password'):
        password = platformtools.dialog_numeric(0, 'Pin (4 dígitos)')
        if not password: return

        if len(password) != 4:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin obligatorio 4 dígitos[/B][/COLOR]' % color_alert)
            return
        
        if str(password) == '0000':
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin NO admitido[/COLOR][/B]' % color_avis)
            return

        confirmpassword = platformtools.dialog_numeric(0, 'Confirme el Pin')
        if not confirmpassword: return

        if password == confirmpassword:
            platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin establecido[/B][/COLOR]' % color_infor)
            config.set_setting('adults_password', password)
            return password
    else:
        password = platformtools.dialog_numeric(0, '[B][COLOR %s]Indique Pin parental[/COLOR][/B]' % color_adver)
        try:
            if int(password) == int(config.get_setting('adults_password')):
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin correcto[/COLOR][/B]' % color_avis)
                return True
            else:
                platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin incorrecto[/COLOR][/B]' % color_exec)
                return False
        except:
            return False

def adults_password_del(item):
    logger.info()

    if not config.get_setting('adults_password'):
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Aún no tiene Pin parental[/COLOR][/B]' % color_exec)
        return

    password = platformtools.dialog_numeric(0, '[B][COLOR %s]Indique Pin parental[/COLOR][/B]' % color_adver)

    try:
       if int(password) == int(config.get_setting('adults_password')):
           txt = 'Si es afirmativa su repuesta a la pregunta formulada, deberá salir y volver a acceder a esta configuración y si lo desea establecer un nuevo Pin parental.'
           if platformtools.dialog_yesno(config.__addon_name, txt, '[B][COLOR %s]¿ Desea eliminar el Pin parental memorizado ?[/COLOR][/B]' % color_adver):
               config.set_setting('adults_password', '')
               platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin anulado[/COLOR][/B]' % color_exec)
       else:
           platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Pin incorrecto[/COLOR][/B]' % color_exec)
           return
    except:
       return


def show_ubicacion(item):
    logger.info()

    downloadpath = config.get_setting('downloadpath', default='')

    if downloadpath:
        path = downloadpath
    else:
        path = os.path.join(config.get_data_path(), 'downloads')

    platformtools.dialog_textviewer('Ubicación de las Descargas', path)


def test_internet(item):
    platformtools.dialog_notification(config.__addon_name, 'Comprobando [B][COLOR %s]Internet[/COLOR][/B]' % color_avis)

    from core import httptools, scrapertools

    your_ip = ''

    try:
       data = httptools.downloadpage('http://httpbin.org/ip').data
       data = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', data)
       your_ip = scrapertools.find_single_match(str(data), '.*?"origin".*?"(.*?)"')
    except:
       pass

    if not your_ip:
        try:
           your_ip = httptools.downloadpage('http://ipinfo.io/ip').data
        except:
           pass

    if not your_ip:
        try:
           your_ip = httptools.downloadpage('http://www.icanhazip.com/').data
        except:
           pass

    if your_ip:
        your_info = ''
		
        try:
           your_info = httptools.downloadpage('https://ipinfo.io/json').data
        except:
           pass

        if your_info:
            your_info = your_info.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(',', '').replace('"', '').replace("'", '')
            platformtools.dialog_textviewer('Información de su Internet', your_info)
        else:
            platformtools.dialog_ok(config.__addon_name, '[COLOR yellow][B]Hay conexión con internet.[/B][/COLOR]', your_ip)
        return

    platformtools.dialog_ok(config.__addon_name, '[COLOR red][B]Parece que NO hay conexión con internet.[/B][/COLOR]', 'Compruebelo realizando cualquier Búsqueda, desde un Navegador Web ')
    return

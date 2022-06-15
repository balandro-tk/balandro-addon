# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3: PY3 = True
else: PY3 = False


import os, re, time

from platformcode import config, logger, platformtools
from core import httptools, scrapertools, filetools, jsontools


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis  = config.get_setting('notification_avis_color', default='yellow')
color_exec  = config.get_setting('notification_exec_color', default='cyan')

channels_unsatisfactory = config.get_setting('developer_test_channels', default='')
servers_unsatisfactory = config.get_setting('developer_test_servers', default='')


channels_poe = [
        ['gdrive', 'https://drive.google.com/drive/']
        ]

servers_poe = [
        ['directo'],
        ['gamovideo'],
        ['m3u8hls'],
        ['torrent']
        ]


def test_channel(channel_name):
    logger.info()

    channel_id = channel_name.lower()

    channel_json = channel_id + '.json'
    filename_json = os.path.join(config.get_runtime_path(), 'channels', channel_json)

    try:
       data = filetools.read(filename_json)
       params = jsontools.load(data)
    except:
       el_canal = ('Falta [B][COLOR %s]' + channel_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
       return

    if params['active'] == False:
        el_canal = ('[B][COLOR %s]' + channel_name) % color_avis
        if not 'temporary' in str(params['clusters']):
            platformtools.dialog_notification(config.__addon_name, el_canal + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
            return

    if config.get_setting('developer_mode', default=False):
        txt = '[COLOR moccasin][B]Internet:[/COLOR]  [COLOR yellow]Status Developer Mode[/B][/COLOR][CR][CR]'
    else:
        txt = test_internet()

    txt += '[COLOR moccasin][B]Balandro:[/B][/COLOR] ' + config.get_addon_version() + '[CR][CR]'

    txt += '[COLOR moccasin][B]Parámetros:[/B][/COLOR][CR]'
    txt += 'id: ' + str(params['id']) + '[CR]'
    txt += 'active: ' + str(params['active']) + '[CR]'
    txt += 'searchable: ' + str(params['searchable']) + '[CR]'

    search_types = str(params['search_types'])
    search_types = search_types.replace('[', '').replace(']', '').replace("'", '').strip()
    txt += 'search_types: ' + str(search_types) + '[CR]'

    categories = str(params['categories'])
    categories = categories.replace('[', '').replace(']', '').replace("'", '').strip()
    txt += 'categories: ' + str(categories) + '[CR]'

    language = str(params['language'])
    language = language.replace('[', '').replace(']', '').replace("'", '').strip()
    txt += 'language: ' + str(language) + '[CR]'

    clusters = str(params['clusters'])
    clusters = clusters.replace('[', '').replace(']', '').replace("'", '').strip()

    if 'suggested' in clusters: clusters = clusters.replace('suggested,', '').strip()
    if 'inestable' in clusters: clusters = clusters.replace('inestable,', '').strip()
    if 'temporary' in clusters: clusters = clusters.replace('temporary,', '').strip()
    if 'mismatched' in clusters: clusters = clusters.replace('mismatched,', '').strip()
    if 'clons' in clusters: clusters = clusters.replace('clons,', '').strip()
    if 'register' in clusters: clusters = clusters.replace('register,', '').strip()
    if 'current' in clusters: clusters = clusters.replace('current,', '').strip()
    if 'torrents' in clusters: clusters = clusters.replace('torrents,', '').strip()

    if str(params['clusters']) == "['dorama']": clusters = clusters.replace('dorama', '').strip()
    if str(params['clusters']) == "['anime']": clusters = clusters.replace('anime', '').strip()

    if 'adults' in clusters: clusters = clusters.replace('adults,', '').strip()
    if str(params['clusters']) == "['adults']": clusters = clusters.replace('adults', '').strip()

    if clusters: txt += 'clusters: ' + str(clusters) + '[CR]'

    notes = str(params['notes'])

    if '+18' in notes:
        notes = notes.replace(' +18', '').strip()

    if 'Canal con enlaces Torrent exclusivamente.' in notes:
        notes = notes.replace('Canal con enlaces Torrent exclusivamente.', '').strip()

    if 'Canal con enlaces Streaming y Torrent.' in notes:
        notes = notes.replace('Canal con enlaces Streaming y Torrent.', '').strip()

    if 'Dispone de varios posibles dominios.' in notes:
        notes = notes.replace('Dispone de varios posibles dominios.', '').strip()

    if 'Puede requerir el uso de proxies' in  notes:
        notes = scrapertools.find_single_match(str(notes), '(.*?)Puede requerir el uso de proxies').strip()

    txt += 'notes: ' + str(notes)

    txt_diag = ''

    if 'temporary' in str(params['clusters']):
        txt_diag  += 'estado: ' + '[COLOR plum][B]Temporalmente Inactivo[/B][/COLOR]'

    if 'inestable' in str(params['clusters']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'estado: ' + '[COLOR plum][B]Inestable[/B][/COLOR]'

    if 'mismatched' in str(params['clusters']):
        if not PY3:
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'result: ' + '[COLOR violet][B]Posible MediaCenter Incompatibile (Sin Resultados) si versión anterior a 19.x[/B][/COLOR]'

    if 'clons' in str(params['clusters']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'clones: ' + '[COLOR lightyellow][B]Varios Clones[/B][/COLOR]'

    if 'suggested' in str(params['clusters']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'canal: ' + '[COLOR aquamarine][B]Sugerido[/B][/COLOR]'

    cfg_status_channel = 'channel_' + channel_id + '_status'

    if str(config.get_setting(cfg_status_channel)) == '1':
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'marcado: ' + '[COLOR aqua][B]Preferido[/B][/COLOR]'
    elif str(config.get_setting(cfg_status_channel)) == '-1':
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'marcado: ' + '[COLOR aqua][B]Desactivado[/B][/COLOR]'

    if not params['searchable']:
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'buscar: ' + '[COLOR yellow][B]No Interviene[/B][/COLOR]'
    else:
        if str(params['search_types']) == "['documentary']":
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'buscar: ' + '[COLOR yellow][B]Solo Documental[/B][/COLOR]'

    if '+18' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'adultos: ' + '[COLOR orange][B]+18[/B][/COLOR]'

    if 'Web dedicada exclusivamente al anime' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR springgreen][B]Solo Animes[/B][/COLOR]'

    if 'Web dedicada exclusivamente al dorama' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR firebrick][B]Solo Doramas[/B][/COLOR]'

    if 'Web dedicada exclusivamente en Novelas' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR limegreen][B]Solo Novelas[/B][/COLOR]'

    if not str(params['clusters']) == "['adults']":
        if 'adults' in str(params['clusters']):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'contenido: ' + '[COLOR orange][B]Puede tener enlaces para Adultos[/B][/COLOR]'

    if str(params['search_types']) == "['documentary']":
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR cyan][B]Solo Documentales[/B][/COLOR]'

    if 'Canal con enlaces Torrent exclusivamente' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'contenido: ' + '[COLOR blue][B]Solo Torrents[/B][/COLOR]'

    if 'Canal con enlaces Streaming y Torrent' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'enlaces: ' + '[COLOR thistle][B]Streaming y Torrent[/B][/COLOR]'

    if 'register' in str(params['clusters']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'cuenta: ' + '[COLOR green][B]Requiere registrarse[/B][/COLOR]'

    if 'dominios' in str(params['notes']):
        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'dominios: ' + '[COLOR lightyellow][B]Varios disponibles[/B][/COLOR]'

    if 'current' in str(params['clusters']):
        cfg_dominio_channel = 'channel_' + channel_id + '_dominio'
        if config.get_setting(cfg_dominio_channel, default=''):
            if txt_diag: txt_diag += '[CR]'
            txt_diag  += 'memorizado: ' + '[COLOR darkorange][B]' + config.get_setting(cfg_dominio_channel) + '[/B][/COLOR]'

        if txt_diag: txt_diag += '[CR]'
        txt_diag  += 'vigente: ' + '[COLOR darkorange][B]Puede comprobarse el último dominio[/B][/COLOR]'

    if 'Puede requerir el uso de proxies' in params['notes']:
        if txt_diag: txt_diag += '[CR]'
        txt_diag += 'bloqueo: ' + '[COLOR red][B]Puede requerir el uso de proxies en función del país/operadora desde el que se accede[/B][/COLOR]'

    if config.get_setting('search_excludes_movies', default=''):
        if "'" + channel_id + "'" in str(config.get_setting('search_excludes_movies')):
            if txt_diag: txt_diag += '[CR]'
            txt_diag += 'excluido: Buscar en [COLOR deepskyblue][B]Películas[/B][/COLOR]'
    if config.get_setting('search_excludes_tvshows', default=''):
        if "'" + channel_id + "'" in str(config.get_setting('search_excludes_tvshows')):
            if txt_diag: txt_diag += '[CR]'
            txt_diag += 'excluido: Buscar en [COLOR hotpink][B]Series[/B][/COLOR]'
    if config.get_setting('search_excludes_documentaries', default=''):
        if "'" + channel_id + "'" in str(config.get_setting('search_excludes_documentaries')):
            if txt_diag: txt_diag += '[CR]'
            txt_diag += 'excluido: Buscar en [COLOR cyan][B]Documentales[/B][/COLOR]'
    if config.get_setting('search_excludes_torrents', default=''):
        if "'" + channel_id + "'" in str(config.get_setting('search_excludes_torrents')):
            if txt_diag: txt_diag += '[CR]'
            txt_diag += 'excluido: Buscar en [COLOR blue][B]Torrents[/B][/COLOR]'
    if config.get_setting('search_excludes_mixed', default=''):
        if "'" + channel_id + "'" in str(config.get_setting('search_excludes_mixed')):
            if txt_diag: txt_diag += '[CR]'
            txt_diag += 'excluido: Buscar en [COLOR yellow][B]Películas y/ó Series[/B][/COLOR]'
    if config.get_setting('search_excludes_all', default=''):
        if "'" + channel_id + "'" in str(config.get_setting('search_excludes_all')):
            if txt_diag: txt_diag += '[CR]'
            txt_diag += 'excluido: Buscar en [COLOR green][B]Todos[/B][/COLOR]'

    if txt_diag:
        txt += '[CR][CR][COLOR moccasin][B]Diagnosis:[/B][/COLOR][CR]'
        txt += txt_diag

    if 'mismatched' in str(params['clusters']):
        from modules import helper

        txt_plat =  helper.get_plataforma('')

        if '(17.' in txt_plat or '(18.' in txt_plat:
            txt_plat = txt_plat.replace('[CR][CR]', '[CR]')
            txt += '[CR][CR]' + txt_plat

    channel_py = channel_id + '.py'
    filename_py = os.path.join(config.get_runtime_path(), 'channels', channel_py)

    dominio = config.get_setting('dominio', channel_id, default='')

    host = ''

    channel_poe = "'" + channel_id + "'"
    esta_en_poe = False

    if channel_poe in str(channels_poe):
        for x in channels_poe:
            if x[0] == channel_id:
               esta_en_poe = True
               channel_poe = x[0]
               host = x[1]
               break

    if not esta_en_poe:
       channel_poe = ''

       if dominio: host = dominio
       else:
          try:
             data = filetools.read(filename_py)
          except:
             el_canal = ('Falta [B][COLOR %s]' + channel_py) % color_alert
             platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
             return

          part_py = 'def mainlist'
          if 'CLONES ' in data or 'clones ' in data: part_py = 'clones '
          elif 'CLASS' in data or 'class ' in data: part_py = 'class '

          elif 'documaniatv_rua' in data: part_py = 'documaniatv_rua'

          elif 'def login' in data: part_py = 'def login'
          elif 'def configurar_proxies' in data: part_py = 'def configurar_proxies'
          elif 'def do_downloadpage' in data: part_py = 'def do_downloadpage'

          bloc = scrapertools.find_single_match(data.lower(), '(.*?)' + part_py)
          bloc = re.sub(r'\n|\r|\t|\s{2}|&nbsp;', '', bloc)

          host = scrapertools.find_single_match(bloc, '.*?host.*?"(.*?)"')
          if not host: host = scrapertools.find_single_match(bloc, ".*?host.*?'(.*?)'")

    host = host.strip()

    if not host:
        if dominio: host = dominio

    if not host or not '//' in host:
        el_canal = ('Falta Dominio/Host/Clon/Metodo en [B][COLOR %s]' + channel_py) % color_alert
        platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
        return

    txt = info_channel(channel_name, channel_poe, host, dominio, txt)

    avisado = False

    if channel_id in str(channels_poe): pass
    else:
       if not 'code: [COLOR springgreen][B]200' in txt:
           platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + channel_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Canal NO ha resultado Satisfactorio.[/I][/B][/COLOR]', '[COLOR yellow][B]Por favor, compruebe la información del Test del Canal.[/B][/COLOR]')
           avisado = True

    if channels_unsatisfactory == 'unsatisfactory':
        if not avisado: return

    platformtools.dialog_textviewer(channel_name.capitalize(), txt)


def info_channel(channel_name, channel_poe, host, dominio, txt):
    el_canal = ('Accediendo [B][COLOR %s]' + channel_name) % color_avis
    platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')

    channel_id = channel_name.lower()

    if dominio: txt_dominio = 'dominio'
    else: txt_dominio = ''

    response, txt = acces_channel(channel_name, host, txt_dominio, txt, follow_redirects=False)

    if channel_id == channel_poe: return txt

    if response.sucess == False:
        if not '<urlopen error timed out>' in txt:
            if not 'Host error' in txt:
                if not 'Cloudflare' in txt:
                   if not 'Invisible Captcha' in txt:
                       if not 'Parece estar Bloqueado' in txt:
                           if not '<urlopen error' in txt:
                               if not 'timed out' in txt:
                                   platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B][COLOR cyan] Redirect[/COLOR]')

                                   response, txt = acces_channel(channel_name, host, '', txt, follow_redirects=True)

    if not dominio:
        dominio = config.get_setting('dominio', channel_id, default='')
        if dominio: response, txt = acces_channel(channel_name, dominio, 'dominio', txt, follow_redirects=False)

    return txt


def acces_channel(channel_name, host, dominio, txt, follow_redirects=None):
    el_canal = ('Testeando [B][COLOR %s]' + channel_name) % color_infor
    platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')

    channel_id = channel_name.lower()

    proxies = ''
    text_with_proxies = ''

    cfg_proxies_channel = 'channel_' + channel_id + '_proxies'
    if not config.get_setting(cfg_proxies_channel, default=''):
        response = httptools.downloadpage(host, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)
    else:
        proxies = config.get_setting(cfg_proxies_channel, default='')

        if proxies:
            proxies = proxies.replace(' ', '')

            if ';' in proxies:  proxies = proxies.replace(',', ';').split(';')
            else: proxies = proxies.split(',')

            platformtools.dialog_notification(config.__addon_name + '[COLOR red][B] con proxies[/B][/COLOR]', el_canal + '[/COLOR][/B]')

            if len(proxies) > 1:
                platformtools.dialog_notification(el_canal + '[/COLOR][/B]', '[COLOR orangered]Test con [B]' + str(len(proxies)) + '[/B] proxies ...[/COLOR]')
                time.sleep(1)

        response = httptools.downloadpage_proxy(channel_id, host, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)
        text_with_proxies = '[COLOR red] con proxies [/COLOR]'

    if proxies:
        if follow_redirects == False:
            txt += '[CR][CR]'
            txt += '[COLOR moccasin][B]Proxies: [/B][/COLOR][CR]'

            proxies = str(proxies)
            proxies = proxies.replace('[', '').replace(']', '').replace("'", '').strip()
            txt += 'actuales: ' + str(proxies)

            cfg_provider_channel = 'channel_' + channel_id + '_proxytools_provider'

            if config.get_setting(cfg_provider_channel): txt += '[CR]provider: ' + config.get_setting(cfg_provider_channel)
    else:
        if 'requerir el uso de proxies' in txt:
            txt += '[CR][CR]'
            txt += '[COLOR moccasin][B]Proxies: [/B][/COLOR][CR]'
            txt += 'actuales: [COLOR cyan][B]Sin proxies[/B][/COLOR]'
	
    if dominio: dominio = '[COLOR coral]' + dominio + '[/COLOR]'

    if follow_redirects == False:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso: ' + dominio + ' ' + text_with_proxies + '[/B][/COLOR][CR]'
    else:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Redirect: ' + dominio + ' ' + text_with_proxies + '[/B][/COLOR][CR]'

    txt += 'host: [COLOR pink][B]' + host + '[/B][/COLOR][CR]'

    if response.sucess == True: color_sucess = '[COLOR yellow][B]'
    else: color_sucess = '[COLOR red][B]'

    txt += 'sucess: ' + color_sucess + str(response.sucess) + '[/B][/COLOR][CR]'

    if response.code == 200: color_code = '[COLOR springgreen][B]'
    else: color_code = '[COLOR orangered][B]'

    txt += 'code: ' + color_code + str(response.code) + '[/B][/COLOR][CR]'

    txt += 'error: ' + str(response.error) + '[CR]'
    txt += 'length: ' + str(len(response.data))

    new_web = scrapertools.find_single_match(str(response.headers), "'location':.*?'(.*?)'")

    if response.sucess == False:
        if '<urlopen error timed out>' in str(response.code) or '<urlopen error' in str(response.code):
            if not 'Sugerencias:' in txt:
                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            if 'actuales:' in txt:
                if 'Sin proxies' in txt: txt += '[COLOR red][B]Configure Proxies a Usar ...[/B][/COLOR][CR]'
                else:
                  if not 'Configure Nuevos Proxies a Usar' in txt: txt += '[COLOR red][B]Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
                  txt += 'Obtenga Nuevos Proxies desde [COLOR yellow][B]All-providers[/B][/COLOR] ó [COLOR yellow][B]Proxyscrape.com[/B][/COLOR][CR]'
            else:
               if config.get_setting(cfg_proxies_channel, default=''): txt += '[COLOR red][B]Obtenga nuevos proxies[/B][/COLOR]'

               txt += '[COLOR gold][B]Puede Marcar el canal como Desactivado[/B][/COLOR][CR]'
               txt += '[COLOR tomato][B]Compruebe su Internet y/ó el Canal, a través de un Navegador Web[/B][/COLOR][CR]'
               txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'

        else:
           if '| 502: Bad gateway</title>' in response.data:  txt += '[CR]gate: [COLOR orangered][B]Host error[/B][/COLOR]'
           elif '<title>Attention Required! | Cloudflare</title>' in response.data: txt += '[CR]blocked: [COLOR orangered][B]Cloudflare[/B][/COLOR]'
           elif '/images/trace/captcha/nojs/h/transparent.' in response.data: txt += '[CR]captcha: [COLOR orangered][B]Invisible Captcha[/B][/COLOR]'
           else:
              if len(response.data) > 0:
                  txt += '[CR]resp: [COLOR orangered][B]Unknow[/B][/COLOR]'

                  txt += '[CR][CR]'
                  txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                  txt += str(response.headers) + '[CR]'

                  if len(response.data) < 1000:
                      txt += '[CR][CR]'
                      txt += '[COLOR moccasin][B]Data:[/B][/COLOR][CR]'
                      txt += str(response.data) + '[CR]'
    else:
        if len(response.data) > 1000:
            if response.code == 301 or response.code == 308: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Permanente (ver Headers 'location':)[/B][/COLOR]"
            elif response.code == 302 or response.code == 307: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal (ver Headers) 'location':[/B][/COLOR]"

            if new_web:
                txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'

                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                txt += str(response.headers) + '[CR]'
        else:
            if len(response.data) < 1000:
                if new_web == '/login':
                    txt += '[CR]login: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'
                    new_web = ''

                    if response.code == 301 or response.code == 302 or response.code == 307 or response.code == 308:
                        if 'dominios:' in txt:
                            txt += "[CR]obtener: [COLOR yellow][B]Puede Obtener Otro Dominio desde Configurar Dominio a usar ...[/B][/COLOR]"

                        txt += "[CR]comprobar: [COLOR red][B]Nuevo Dominio (verificar la Web vía internet[/B][/COLOR]"

                else:
                   if response.code == 301 or response.code == 308: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Permanente (ver Headers 'location':)[/B][/COLOR]"
                   elif response.code == 302 or response.code == 307: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal (ver Headers) 'location':[/B][/COLOR]"
                   else: txt += "[CR][CR][COLOR orangered][B]Comprobar Dominio (ver Headers 'location':)[/B][/COLOR]"

                if new_web:
                    if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                    elif '/wp-admin/install.php' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                    else: txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'
            else:
                if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                elif '/wp-admin/install.php' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'

            if 'status:' in txt:
                if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]account: [COLOR goldenrod][B]Suspendida[/B][/COLOR]'
                else: txt += '[CR]account: [COLOR goldenrod][B]Podría estar en Mantenimiento[/B][/COLOR]'

            if not "'location': '/login'" in str(response.headers):
                if not 'status:'in txt:
                    txt += '[CR][CR]'
                    txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                    txt += str(response.headers) + '[CR]'

            if len(response.data) > 0:
                if not '/cgi-sys/suspendedpage.cgi' or not '/wp-admin/install.php' in new_web:
                    txt += '[CR][CR]'
                    txt += '[COLOR moccasin][B]Data:[/B][/COLOR][CR]'
                    txt += str(response.data) + '[CR]'

    if 'active: True' in txt:
        if not 'Sugerencias:' in txt:
            if 'Invisible Captcha' in txt or 'Obtenga nuevos proxies' in txt or 'Host error' in txt or 'No se puede establecer una' in txt or 'Cloudflare' in txt or 'Unknow' in txt:
                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

                if 'Invisible Captcha' in txt:
                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += '[COLOR red][B]Configure Proxies a Usar ...[/B][/COLOR][CR]'
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += '[COLOR red][B]Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
                           txt += '[COLOR plum][B]Obtenga Nuevos Proxies desde el proveedor[/B] [/COLOR][COLOR yellow][B]All-providers[/B][/COLOR] ó [COLOR yellow][B]Proxyscrape.com[/B][/COLOR][CR]'

                    txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'
 
                elif 'Obtenga nuevos proxies' in txt:
                    if 'Sin proxies' in txt: txt += '[COLOR red][B]Configure Proxies a Usar ...[/B][/COLOR][CR]'
                    else:
                       if not 'Configure Nuevos Proxies a Usar' in txt: txt += '[COLOR red][B]Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
                       txt += '[COLOR plum][B]Obtenga Nuevos Proxies desde el proveedor[/B] [COLOR yellow][B]All-providers[/B][/COLOR] ó [COLOR yellow][B]Proxyscrape.com[/B][/COLOR][CR]'

                    txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'

                elif 'Host error' in txt:
                    txt += '[COLOR gold][B]Puede Marcar el canal como Desactivado[/B][/COLOR][CR]'

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += '[COLOR red][B] Configure Proxies a Usar ...[/B][/COLOR][CR]'
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += '[COLOR red][B]Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
                           txt += '[COLOR plum][B]Obtenga Nuevos Proxies desde el proveedor[/B] [COLOR yellow][B]All-providers[/B][/COLOR] ó [COLOR yellow][B]Proxyscrape.com[/B][/COLOR][CR]'

                    txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'

                elif 'No se puede establecer una' in txt:
                    txt += 'conexión:[COLOR yellow][B]No se pudo establecer la conectividad[/B][/COLOR][CR]'

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += '[COLOR red][B]Configure Proxies a Usar ...[/B][/COLOR][CR]'
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += '[COLOR red][B]Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
                           txt += '[COLOR plum][B]Obtenga Nuevos Proxies desde el proveedor[/B] [COLOR yellow][B]All-providers[/B][/COLOR] ó [COLOR yellow][B]Proxyscrape.com[/B][/COLOR][CR]'
                    else: txt += '[COLOR tomato][B]Compruebe su Internet y/ó el Canal, a través de un Navegador Web[/B][/COLOR][CR]'

                    txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'

                elif 'Cloudflare' in txt:
                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += '[COLOR red][B]Configure Proxies a Usar ...[/B][/COLOR][CR]'
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += '[COLOR red][B]Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
                           txt += '[COLOR plum][B]Obtenga Nuevos Proxies desde el proveedor[/B] [COLOR yellow][B]All-providers[/B][/COLOR] ó [COLOR yellow][B]Proxyscrape.com[/B][/COLOR][CR]'
                    else: txt += '[COLOR gold][B]Puede Marcar el canal como Desactivado[/B][/COLOR][CR]'

                    txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'

                elif 'Unknow' in txt:
                    if not '<p>Por causas ajenas a' in txt: txt += '[COLOR goldenrod][B]Puede estar en Mantenimiento[/B][/COLOR][CR]'
                    txt += '[COLOR gold][B]Puede Marcar el canal como Desactivado[/B][/COLOR][CR]'

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += '[COLOR red][B]Configure Proxies a Usar ...[/B][/COLOR][CR]'
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += '[COLOR red][B] Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
                           txt += '[COLOR plum][B]Obtenga Nuevos Proxies desde el proveedor[/B] [COLOR yellow][B]All-providers[/B][/COLOR] ó [COLOR yellow][B]Proxyscrape.com[/B][/COLOR][CR]'

                    txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'

                elif '<p>Por causas ajenas a' in txt:
                    txt += '[COLOR darkorange][B]Parece estar Bloqueado por su Operadora de Internet[/B][/COLOR][CR]'

                    if 'actuales:' in txt:
                        if 'Sin proxies' in txt: txt += '[COLOR red][B]Configure Proxies a Usar ...[/B][/COLOR][CR]'
                        else:
                           if not 'Configure Nuevos Proxies a Usar' in txt: txt += '[COLOR red][B] Configure Nuevos Proxies a Usar ...[/B][/COLOR][CR]'
                           txt += '[COLOR plum][B]Obtenga Nuevos Proxies desde el proveedor[/B] [COLOR yellow][B]All-providers[/B][/COLOR] ó [COLOR yellow][B]Proxyscrape.com[/B][/COLOR][CR]'

                    txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'

                else:
                    txt += '[COLOR gold][B]Puede Marcar el canal como Desactivado[/B][/COLOR][CR]'
                    txt += '[COLOR tomato][B]Compruebe su Internet y/ó el Canal, a través de un Navegador Web[/B][/COLOR][CR]'
                    txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/I][/B][/COLOR][CR]'

    if not 'Sugerencias:' in txt:
        if 'Suspendida' in txt:
            txt += '[COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            txt += '[COLOR goldenrod][B]Puede estar Renovando el Dominio o quizás estar en Mantenimiento[/B][/COLOR]'

        elif response.sucess == False:
            txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            txt += '[COLOR gold][B]Puede Marcar el canal como Desactivado[/B][/COLOR][CR]'
            txt += '[COLOR tomato][B]Compruebe su Internet y/ó el Canal, a través de un Navegador Web[/B][/COLOR][CR]'
            txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/B][/I][/COLOR][CR]'

    return response, txt


def test_server(server_name):
    logger.info()

    server_id = server_name.lower()

    server_json = server_id + '.json'
    filename_json = os.path.join(config.get_runtime_path(), 'servers', server_json)

    try:
       data = filetools.read(filename_json)
       dict_server = jsontools.load(data)
    except:
       el_server = ('Falta [B][COLOR %s]' + server_json) % color_alert
       platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')
       return

    if dict_server['active'] == False:
        el_server = ('[B][COLOR %s]' + server_name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_server + '[COLOR %s] inactivo [/COLOR][/B]' % color_alert)
        return

    if 'find_videos' in dict_server: dict_server['find_videos']['patterns'] = dict_server['find_videos'].get('patterns', list())
    else:
        el_server = ('[B][COLOR %s]' + server_name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_server + 'Falta [COLOR %s] find_videos [/COLOR][/B]' % color_alert)
        return

    if config.get_setting('developer_mode', default=False):
        txt = '[COLOR moccasin][B]Internet:[/COLOR]  [COLOR yellow]Status Developer Mode[/B][/COLOR][CR][CR]'
    else:
        txt = test_internet()

    txt += '[COLOR moccasin][B]Balandro:[/B][/COLOR] ' + config.get_addon_version() + '[CR][CR]'

    bloc = dict_server['find_videos']['patterns']

    servers = scrapertools.find_multiple_matches(str(bloc), '.*?"url".*?"(.*?)"')
    if not servers: servers = scrapertools.find_multiple_matches(str(bloc), ".*?'url'.*?'(.*?)'")

    if not servers:
        el_server = ('Falta url [B][COLOR %s]' + server_name) % color_alert
        platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')
        return

    url_servidor = ''

    server_poe = "'" + server_id + "'"
    esta_en_poe = False

    for url in servers:
        if server_poe in str(servers_poe):
           for x in servers_poe:
               if x[0] == server_id:
                  esta_en_poe = True
                  server_poe = x[0]
                  url_servidor = server_id
                  break

        if not esta_en_poe:
           server_poe = ''

           try:
              type = url.split('/')[0].strip()
              servidor = url.split('/')[2].strip()

              if type:
                  if servidor: url_servidor = type + '//' + servidor + '/'
           except:
              url_servidor = url

        continue

    txt += '[COLOR moccasin][B]Parámetros:[/B][/COLOR][CR]'

    try:
       patterns = dict_server['find_videos']['patterns']

       for pattern in patterns:
           tab_pat = scrapertools.find_single_match(str(pattern), "'pattern': '(.*?)'").strip()
           url_pat = scrapertools.find_single_match(str(pattern), "'url': '(.*?)'").strip()

           if not tab_pat or not url_pat: continue

           txt += 'patron: ' + str(tab_pat) + '[CR]'
           txt += 'urlpat: ' + str(url_pat) + '[CR][CR]'
    except:
       txt += 'patrones: ' + str(bloc) + '[CR][CR]'

    try:
       notes = dict_server['notes']
    except: 
       notes = ''

    txt_diag = ''

    if 'Alternative' in notes:
        notes = notes.replace('Alternative vía:', '').strip()
        txt_diag  += 'alternativas: ' + '[COLOR plum][B]' + str(notes) + '[/B][/COLOR][CR]'
    else:
        if notes: txt_diag  += 'notes: ' + '[COLOR plum][B]' + str(notes) + '[/B][/COLOR][CR]'

    if txt_diag:
        txt += '[COLOR moccasin][B]Diagnosis:[/B][/COLOR][CR]'
        txt += txt_diag
    else:
        txt += '[CR][COLOR moccasin][B]Diagnosis:[/B][/COLOR][CR]'

    if url_servidor == '': url_servidor = 'Indefinido'
    elif '\\' in url_servidor: url_servidor = 'Variable'

    if not url_servidor: txt += 'url: [COLOR red][B] Falta [/B][/COLOR][CR]'
    else:
       txt += 'url: ' + url_servidor
       txt = info_server(server_name, server_poe, url_servidor, txt)

    avisado = False

    if 'Variable' in txt or 'Indefinido' in txt: pass
    elif server_id in str(servers_poe): pass
    else:
       if not 'code: [COLOR springgreen][B]200' in txt:
           platformtools.dialog_ok(config.__addon_name + ' [COLOR yellow][B]' + server_name.capitalize() + '[/B][/COLOR]', '[COLOR red][B][I]El test del Servidor NO ha resultado Satisfactorio.[/I][/B][/COLOR]', '[COLOR yellow][B]Por favor, compruebe la información del Test del Servidor.[/B][/COLOR]')
           avisado = True

    if servers_unsatisfactory == 'unsatisfactory':
        if not avisado: return

    platformtools.dialog_textviewer(server_name.capitalize(), txt)


def info_server(server_name, server_poe, url, txt):
    el_server = ('Accediendo [B][COLOR %s]' + server_name) % color_infor
    platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')

    server_id = server_name.lower()

    if server_id == server_poe: return txt
    elif url == 'Indefinido': return txt
    elif url == 'Variable': return txt

    response, txt = acces_server(server_name, url, txt, follow_redirects=False)

    if response.sucess == False:
        if not 'Host error' in txt:
            if not 'Cloudflare' in txt:
               if not 'Invisible Captcha' in txt:
                   if not 'timed out' in txt:
                       platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B][COLOR cyan] Redirect[/COLOR]')

                       response, txt = acces_server(server_name, url, txt, follow_redirects=True)

    return txt

def acces_server(server_name, url, txt, follow_redirects=None):
    el_server = ('Testeando [B][COLOR %s]' + server_name) % color_avis
    platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')

    server_id = server_name.lower()

    response = httptools.downloadpage(url, follow_redirects=follow_redirects, raise_weberror=False, bypass_cloudflare=False)

    if follow_redirects == False:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso: [/B][/COLOR][CR]'
    else:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Redirect: [/B][/COLOR][CR]'

    txt += 'host: [COLOR pink][B]' + url + '[/B][/COLOR][CR]'

    if response.sucess == True: color_sucess = '[COLOR yellow][B]'
    else: color_sucess = '[COLOR red][B]'

    txt += 'sucess: ' + color_sucess + str(response.sucess) + '[/B][/COLOR][CR]'

    if response.code == 200: color_code = '[COLOR springgreen][B]'
    else: color_code = '[COLOR orangered][B]'

    txt += 'code: ' + color_code  + str(response.code) + '[/B][/COLOR][CR]'

    txt += 'error: ' + str(response.error) + '[CR]'
    txt += 'length: ' + str(len(response.data))

    new_web = scrapertools.find_single_match(str(response.headers), "'location':.*?'(.*?)'")

    if response.sucess == False:
        if '| 502: Bad gateway</title>' in response.data:  txt += '[CR]gate: [COLOR orangered][B]Host error[/B][/COLOR]'
        elif '<title>Attention Required! | Cloudflare</title>' in response.data: txt += '[CR]blocked: [COLOR orangered][B]Cloudflare[/B][/COLOR]'
        elif '/images/trace/captcha/nojs/h/transparent.' in response.data: txt += '[CR]captcha: [COLOR orangered][B]Invisible Captcha[/B][/COLOR]'
        else:
           if len(response.data) > 0:
               txt += '[CR]resp: [COLOR orangered][B]Unknow[/B][/COLOR]'

               txt += '[CR][CR]'
               txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
               txt += str(response.headers) + '[CR]'

               if len(response.data) < 1000:
                   txt += '[CR][CR]'
                   txt += '[COLOR moccasin][B]Data:[/B][/COLOR][CR]'
                   txt += str(response.data) + '[CR]'
    else:
        if len(response.data) > 1000:
            if response.code == 301 or response.code == 308: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Permanente (ver Headers 'location':)[/B][/COLOR]"
            elif response.code == 302 or response.code == 307: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal (ver Headers) 'location':[/B][/COLOR]"

            if new_web:
                txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'

                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                txt += str(response.headers) + '[CR]'
        else:
            if len(response.data) < 1000:
                if response.code == 301 or response.code == 308: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Permanente (ver Headers 'location':)[/B][/COLOR]"
                elif response.code == 302 or response.code == 307: txt += "[CR][CR][COLOR orangered][B]Nuevo Dominio Temporal (ver Headers) 'location':[/B][/COLOR]"
                else: txt += "[CR][CR][COLOR orangered][B]Comprobar Dominio (ver Headers 'location':)[/B][/COLOR]"

                if new_web:
                    if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                    elif '/wp-admin/install.php' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                    else: txt += '[CR]nuevo: [COLOR springgreen][B]' + new_web + '[/B][/COLOR]'
            else:
                if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'
                elif '/wp-admin/install.php' in new_web: txt += '[CR]status: [COLOR red][B]' + new_web + '[/B][/COLOR]'

            if 'status:'in txt:
                if '/cgi-sys/suspendedpage.cgi' in new_web: txt += '[CR]account: [COLOR goldenrod][B]Suspendida[/B][/COLOR]'
                else: txt += '[CR]account: [COLOR goldenrod][B]Podría estar en Mantenimiento[/B][/COLOR]'
            else:
                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
                txt += str(response.headers) + '[CR]'

            if len(response.data) > 0:
                if not '/cgi-sys/suspendedpage.cgi' in new_web or not '/wp-admin/install.php' in new_web:
                    txt += '[CR][CR]'
                    txt += '[COLOR moccasin][B]Data:[/B][/COLOR][CR]'
                    txt += str(response.data) + '[CR]'

    if not 'Sugerencias:' in txt:
        if 'Invisible Captcha' in txt:
            txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'
            txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/B][/I][/COLOR][CR]'

        elif 'Suspendida' in txt:
            txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            txt += '[COLOR goldenrod][B]Puede estar Renovando el Dominio o quizás estar en Mantenimiento[/B][/COLOR]'

        elif response.sucess == False:
            txt += '[CR][CR][COLOR moccasin][B]Sugerencias:[/B][/COLOR][CR]'

            txt += '[COLOR gold][B]Puede Descartar el Servidor en la Configuración (categoría Play)[/B][/COLOR][CR]'
            txt += '[COLOR tomato][B]Compruebe su Internet y/ó el Servidor, a través de un Navegador Web[/B][/COLOR][CR]'
            txt += '[COLOR yellow][B][I]Apague su Router durante 5 minutos aproximadamente, Re-Inicielo e inténtelo de nuevo[/B][/I][/COLOR][CR]'

    return response, txt


def test_internet():
    platformtools.dialog_notification(config.__addon_name, 'Comprobando [B][COLOR %s]Internet[/COLOR][/B]' % color_avis)

    your_ip = ''

    try:
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

    if not your_ip: your_ip = '[COLOR red] Sin Conexión [/COLOR]'

    txt = '[COLOR moccasin][B]Internet:[/B][/COLOR]  %s ' % your_ip
    txt += '[CR][CR]'

    return txt

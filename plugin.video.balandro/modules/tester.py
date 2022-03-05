# -*- coding: utf-8 -*-

import os, re

from platformcode import config, logger, platformtools
from core import httptools, scrapertools, filetools, jsontools


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis  = config.get_setting('notification_avis_color', default='yellow')
color_exec  = config.get_setting('notification_exec_color', default='cyan')


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

    txt = test_internet()

    txt += '[COLOR moccasin][B]Parámetros:[/B][/COLOR][CR]'
    txt += 'id: ' + str(params['id']) + '[CR]'
    txt += 'searchable: ' + str(params['searchable']) + '[CR]'
    txt += 'search_types: ' + str(params['search_types']) + '[CR]'
    txt += 'categories: ' + str(params['categories']) + '[CR]'
    txt += 'language: ' + str(params['language']) + '[CR]'

    try:
       txt += 'clusters: ' + str(params['clusters']) + '[CR]'
    except:
       pass

    txt += 'notes: ' + str(params['notes'])

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

       if dominio:
           host = dominio
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
           if not host:
               host = scrapertools.find_single_match(bloc, ".*?host.*?'(.*?)'")

    host = host.strip()

    if not host:
        if dominio:
            host = dominio

    if not host or not '//' in host:
        el_canal = ('Falta Dominio/Host/Clon/Metodo en [B][COLOR %s]' + channel_py) % color_alert
        platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')
        return

    txt = info_channel(channel_name, channel_poe, host, dominio, txt)

    platformtools.dialog_textviewer(channel_name, txt)


def info_channel(channel_name, channel_poe, host, dominio, txt):
    el_canal = ('Accediendo [B][COLOR %s]' + channel_name) % color_avis
    platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')

    channel_id = channel_name.lower()

    if dominio:
       txt_dominio = 'dominio'
    else:
       txt_dominio = ''

    response, txt = acces_channel(channel_name, host, txt_dominio, txt, follow_redirects=False)

    if channel_id == channel_poe:
        return txt

    if response.sucess == False:
        response, txt = acces_channel(channel_name, host, '', txt, follow_redirects=True)

    if not dominio:
        dominio = config.get_setting('dominio', channel_id, default='')
        if dominio:
            response, txt = acces_channel(channel_name, dominio, 'dominio', txt, follow_redirects=False)

    return txt


def acces_channel(channel_name, host, dominio, txt, follow_redirects=None):
    el_canal = ('Testeando [B][COLOR %s]' + channel_name) % color_infor
    platformtools.dialog_notification(config.__addon_name, el_canal + '[/COLOR][/B]')

    channel_id = channel_name.lower()

    text_with_proxies = ''

    cfg_proxies_channel = 'channel_' + channel_id + '_proxies'
    if not config.get_setting(cfg_proxies_channel, default=''):
        response = httptools.downloadpage(host, follow_redirects=follow_redirects, raise_weberror=False)
    else:
        response = httptools.downloadpage_proxy(channel_id, host, follow_redirects=follow_redirects, raise_weberror=False)
        text_with_proxies = '[COLOR red] con proxies [/COLOR]'

    if dominio:
        dominio = '[COLOR coral]' + dominio + '[/COLOR]'

    if follow_redirects == False:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso: ' + dominio + ' ' + text_with_proxies + '[/B][/COLOR][CR]'
        txt += 'host: ' + host + '[CR]'
    else:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso Redirect: ' + dominio + ' ' + text_with_proxies + '[/B][/COLOR][CR]'
        txt += 'host: ' + host + '[CR]'

    if response.sucess == True:
        color_sucess = '[COLOR yellow][B]'
    else:
        color_sucess = '[COLOR red][B]'

    txt += 'sucess: ' + color_sucess + str(response.sucess) + '[/B][/COLOR][CR]'

    txt += 'code: ' + str(response.code) + '[CR]'
    txt += 'error: ' + str(response.error) + '[CR]'
    txt += 'data length: ' + str(len(response.data))

    if response.sucess == True:
        if len(response.data) < 1000:
            txt += '[CR][CR]'
            txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
            txt += str(response.headers) + '[CR]'

            if len(response.data) > 0:
                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Data:[/B][/COLOR][CR]'
                txt += str(response.data) + '[CR]'

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

    if 'find_videos' in dict_server:
        dict_server['find_videos']['patterns'] = dict_server['find_videos'].get('patterns', list())
    else:
        el_server = ('[B][COLOR %s]' + server_name) % color_avis
        platformtools.dialog_notification(config.__addon_name, el_server + 'Falta [COLOR %s] find_videos [/COLOR][/B]' % color_alert)
        return

    txt = test_internet()

    bloc = str(dict_server['find_videos']['patterns'])

    servers = scrapertools.find_multiple_matches(str(bloc), '.*?"url".*?"(.*?)"')
    if not servers:
        servers = scrapertools.find_multiple_matches(str(bloc), ".*?'url'.*?'(.*?)'")

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
                  if servidor:
                      url_servidor = type + '//' + servidor + '/'
           except:
              url_servidor = url

        continue

    txt += '[COLOR moccasin][B]Parámetros:[/B][/COLOR][CR]'
    txt += 'patterns: ' + str(bloc) + '[CR][CR]'

    if url_servidor == '':
        url_servidor = 'Indefinido'
    elif '\\' in url_servidor:
        url_servidor = 'Variable'

    if not url_servidor:
       txt += 'url: [COLOR red][B] Falta [/B][/COLOR][CR]'
    else:
       txt += 'url: ' + url_servidor
       txt = info_server(server_name, server_poe, url_servidor, txt)

    platformtools.dialog_textviewer(server_name, txt)


def info_server(server_name, server_poe, url, txt):
    el_server = ('Accediendo [B][COLOR %s]' + server_name) % color_infor
    platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')

    server_id = server_name.lower()

    if server_id == server_poe:
        return txt
    elif url == 'Indefinido':
        return txt
    elif url == 'Variable':
        return txt

    response, txt = acces_server(server_name, url, txt, follow_redirects=False)

    if response.sucess == False:
        response, txt = acces_server(server_name, url, txt, follow_redirects=True)

    return txt

def acces_server(server_name, url, txt, follow_redirects=None):
    el_server = ('Testeando [B][COLOR %s]' + server_name) % color_avis
    platformtools.dialog_notification(config.__addon_name, el_server + '[/COLOR][/B]')

    server_id = server_name.lower()

    text_with_proxies = ''

    response = httptools.downloadpage(url, follow_redirects=follow_redirects, raise_weberror=False)

    if follow_redirects == False:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso: [/B][/COLOR][CR]'
        txt += 'host: ' + url + '[CR]'
    else:
        txt += '[CR][CR]'
        txt += '[COLOR moccasin][B]Acceso Redirect: [/B][/COLOR][CR]'
        txt += 'host: ' + url + '[CR]'

    if response.sucess == True:
        color_sucess = '[COLOR yellow][B]'
    else:
        color_sucess = '[COLOR red][B]'

    txt += 'sucess: ' + color_sucess + str(response.sucess) + '[/B][/COLOR][CR]'

    txt += 'code: ' + str(response.code) + '[CR]'
    txt += 'error: ' + str(response.error) + '[CR]'
    txt += 'data length: ' + str(len(response.data))

    if response.sucess == True:
        if len(response.data) < 100:
            txt += '[CR][CR]'
            txt += '[COLOR moccasin][B]Headers:[/B][/COLOR][CR]'
            txt += str(response.headers) + '[CR]'

            if len(response.data) > 0:
                txt += '[CR][CR]'
                txt += '[COLOR moccasin][B]Data:[/B][/COLOR][CR]'
                txt += str(response.data) + '[CR]'

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
        try:
           your_ip = httptools.downloadpage('http://ipinfo.io/ip').data
        except:
           pass

    if not your_ip:
        try:
           your_ip = httptools.downloadpage('http://www.icanhazip.com/').data
        except:
           pass

    if not your_ip:
        your_ip = '[COLOR red] Sin Conexión [/COLOR]'

    txt = '[COLOR moccasin][B]Internet:[/B][/COLOR]  %s ' % your_ip
    txt += '[CR][CR]'

    return txt

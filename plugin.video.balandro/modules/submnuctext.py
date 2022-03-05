# -*- coding: utf-8 -*-

import os

from platformcode import logger, config, platformtools
from core.item import Item


color_alert = config.get_setting('notification_alert_color', default='red')
color_infor = config.get_setting('notification_infor_color', default='pink')
color_adver = config.get_setting('notification_adver_color', default='violet')
color_avis = config.get_setting('notification_avis_color', default='yellow')
color_exec = config.get_setting('notification_exec_color', default='cyan')


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

    elif item.from_channel == 'megadede2':
        from channels import megadede2
        item.channel = 'megadede2'
        megadede2.configurar_proxies(item)

    elif item.from_channel == 'megaserie':
        from channels import megaserie
        item.channel = 'megaserie'
        megaserie.configurar_proxies(item)

    elif item.from_channel == 'mejortorrents':
        from channels import mejortorrents
        item.channel = 'mejortorrents'
        mejortorrents.configurar_proxies(item)

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

    elif item.from_channel == 'ppeliculas':
        from channels import ppeliculas
        item.channel = 'ppeliculas'
        ppeliculas.configurar_proxies(item)

    elif item.from_channel == 'repelishd':
        from channels import repelishd
        item.channel = 'repelishd'
        repelishd.configurar_proxies(item)

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

def _quitar_proxies(item):
    el_canal = ('Quitando proxies [B][COLOR %s]' + item.from_channel.capitalize() + '[/COLOR][/B]') % color_avis
    platformtools.dialog_notification(config.__addon_name, el_canal)

    config.set_setting('proxies', '', item.from_channel)
    platformtools.itemlist_refresh()


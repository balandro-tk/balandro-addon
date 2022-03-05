# -*- coding: utf-8 -*-

import sys

PY3 = False
if sys.version_info[0] >= 3: PY3 = True

import time, random

from platformcode import logger, config, platformtools
from core import scrapertools

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


try:
    import requests
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    existe_script = True
except:
    existe_script = False


color_alert = config.get_setting('notification_alert_color', default='red')

# ~ useragent = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
useragent = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"

ver_stable_chrome = config.get_setting("ver_stable_chrome", default=True)
if ver_stable_chrome:
    cfg_last_ver_chrome = config.get_setting('chrome_last_version', default='')
    if not cfg_last_ver_chrome == '':
        chrome_version = cfg_last_ver_chrome
        useragent = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36" % chrome_version


default_headers = dict()
default_headers["User-Agent"] = useragent
default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
default_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
default_headers["Accept-Charset"] = "UTF-8"
default_headers["Accept-Encoding"] = "gzip"

headers = default_headers


def read(url, channel):
    logger.info()

    if not existe_script:
        platformtools.dialog_notification(config.__addon_name, '[B][COLOR %s]Falta script.module.requests[/COLOR][/B]' % color_alert)
        return ''

    if not url: return ''

    # ~ Sin proxies
    if not channel:
        data = read_data(url)

        if not data:
            espera = 3
            platformtools.dialog_notification('Requests', 'Espera requerida de %s segundos' % espera)
            time.sleep(int(espera))

            data = read_data(url)

        return data


    # ~ Con proxies
    proxies = config.get_setting('proxies', channel, default='').replace(' ', '')

    # ~ Si los proxies estan separados por ; orden aleatorio
    if ';' in proxies:
        proxies = proxies.replace(',', ';').split(';')
        random.shuffle(proxies)
    else:
        proxies = proxies.split(',')

    if len(proxies) == 0: proxies = ['']

    source = ''

    if proxies:
         for n, proxy in enumerate(proxies):
             px = {'http': proxy, 'https': proxy}

             source = read_proxy(url, px)

             if source: break

             espera = 5
             platformtools.dialog_notification(channel.capitalize(), 'Espera requerida de %s segundos' % espera)
             time.sleep(int(espera))

             source = read_proxy(url, px)

    return source


def read_proxy(url, px):
    source = ''

    try:
        source = requests.Session()
        source = requests.get(url, headers=headers, proxies=px, verify=False, timeout=30).content
    except:
        source = read_proxy2(url, px)

    if source: 
        if '<title>Please Wait... | Cloudflare</title>' in str(source):
            platformtools.dialog_notification(config.__addon_name, 'Verificando [B][COLOR %s]reCAPTCHA[/COLOR][/B]' % color_alert)
            source = read_proxy2(url, px)

        return source

    new_url = scrapertools.find_single_match(source, 'window.location.href.*?"(.*?)"')
    if new_url:
        try:
           source = requests.Session()
           source = requests.get(new_url, headers=headers, proxies=px, verify=False, timeout=30).content
        except:
           logger.error('[COLOR red]Error read proxy location[/COLOR]')
           return ''

    return source


def read_proxy2(url, px):
    data = ''

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url, headers=headers, proxies=px)
        if PY3:
            data = urlopen(req).read().decode('utf-8')
        else:
            data = urlopen(req).read()
    except:
        logger.error('[COLOR red]Error read proxy2[/COLOR]')
        return ''

    return data 


def read_data(url):
    data = ''

    try:
        data = requests.Session()
        data = requests.get(url, headers=headers, verify=False, timeout=30).content
    except:
        data = read_data2(url)

    if data:
       if '<title>Please Wait... | Cloudflare</title>' in str(data):
           platformtools.dialog_notification(config.__addon_name, 'Verificando [B][COLOR %s]reCAPTCHA[/COLOR][/B]' % color_alert)
           data = read_data2(url)

       return data

    new_url = scrapertools.find_single_match(data, 'window.location.href.*?"(.*?)"')
    if new_url:
        try:
           data = requests.Session()
           data = requests.get(new_url, headers=headers, verify=False, timeout=30).content
        except:
           logger.error('[COLOR red]Error read data location[/COLOR]')
           return ''

    return data


def read_data2(url):
    data = ''

    try:
        headers={'User-Agent': 'Mozilla/5.0'}
        req = Request(url, headers=headers)
        if PY3:
            data = urlopen(req).read().decode('utf-8')
        else:
            data = urlopen(req).read()
    except:
        logger.error('[COLOR red]Error read data2[/COLOR]')
        return ''

    return data

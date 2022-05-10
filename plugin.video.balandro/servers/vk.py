# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib

from core import httptools, scrapertools
from platformcode import logger
import base64, time


def normalizar_url(page_url):
    try:
        page_url = page_url.replace('&amp;', '&')
        oid, nid = scrapertools.find_single_match(page_url, "oid=(\d+)&id=(\d+)")
        return 'https://vk.com/video%s_%s' % (oid, nid)
    except:
        return page_url.replace('http://', 'https://')


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    page_url = normalizar_url(page_url)
    
    url_savevk = 'https://savevk.com/' + page_url.replace('https://vk.com/', '')
    
    data = httptools.downloadpage(url_savevk).data
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, 'window\.videoParams = \{(.*?)\};')

    p_id = scrapertools.find_single_match(bloque, 'id: "([^"]+)')
    p_server = scrapertools.find_single_match(bloque, 'server: "([^"]+)')
    p_token = scrapertools.find_single_match(bloque, 'token: "([^"]+)')
    # ~ p_sig = scrapertools.find_single_match(bloque, 'sig: "([^"]+)')
    p_credentials = scrapertools.find_single_match(bloque, 'credentials: "([^"]+)')
    p_c_key = scrapertools.find_single_match(bloque, 'c_key: "([^"]+)')
    p_e_key = scrapertools.find_single_match(bloque, 'e_key: "([^"]+)')
    p_i_key = scrapertools.find_single_match(bloque, 'i_key: "([^"]+)')
    if not p_id or not p_server or not p_token: return video_urls

    # ~ url = 'https://%s/method/video.sig?callback=jQuery1_1&token=%s&videos=%s&extra_key=%s&ckey=%s&sig=%s&_=%s' % \
        # ~ (base64.b64decode(p_server[::-1]), p_token, p_id, p_e_key, p_c_key, p_sig, int(time.time()))

    url = 'https://%s/method/video.get?credentials=%s&token=%s&videos=%s&extra_key=%s&ckey=%s' % \
        (base64.b64decode(p_server[::-1]), p_credentials, p_token, p_id, p_e_key, p_c_key)

    data = httptools.downloadpage(url, headers={'Referer': url_savevk}).data.replace('\\/', '/')
    # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, '"files":\{(.*?)\}')

    matches = scrapertools.find_multiple_matches(bloque, '"([^"]+)":"([^"]+)')
    for lbl, url in matches:
        video_urls.append([lbl, url])

    return video_urls


def get_video_url_ant(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    page_url = normalizar_url(page_url)
    
    data = httptools.downloadpage('https://getvideo.org/en').data
    token = scrapertools.find_single_match(data, '<meta name="csrf-token" content="([^"]+)')
    
    time.sleep(1)

    post = {'ajax': '1', 'token': token, 'url': page_url}
    data = httptools.downloadpage('https://getvideo.org/en/get_video', post=urllib.urlencode(post)).data

    matches = scrapertools.find_multiple_matches(data, ' href="([^"]+)" class="[^"]*" data="([^"]+)')
    for url, lbl in matches:
        url_final = urllib.unquote(url.split('&url=')[1])
        if url_final:
            video_urls.append([lbl, url_final])

    video_urls.reverse()
    return video_urls

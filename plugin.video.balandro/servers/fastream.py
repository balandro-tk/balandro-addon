# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core import httptools, scrapertools, servertools
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    if '|' in page_url: page_url, referer = page_url.split('|', 1)

    data = httptools.downloadpage(page_url).data

    if 'File is no longer available as it expired or has been deleted' in data:
        return 'El archivo no existe o ha sido borrado'

    try:
        packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
        unpacked = jsunpack.unpack(packed)
    except:
        unpacked = ''

    if unpacked:
        data_var = scrapertools.find_single_match(unpacked, "(?is)var player\s?=.+?sources.+?\[(.+?)\]")
        matches = scrapertools.find_multiple_matches(str(data_var), 'sources.*?file.*?"(.*?)"')

        if not matches: data_var = str(unpacked)
    else:
        data_var = scrapertools.find_single_match(data, "(?is)var player\s?=.+?sources.+?\[(.+?)\]")
        matches = scrapertools.find_multiple_matches(str(data_var), 'sources:.*?file.*?"(.*?)"')

        if not matches: data_var = str(data)

    if not matches: matches = scrapertools.find_multiple_matches(str(data_var), 'sources:.*?file.*?"(.*?)"')

    for url in matches:
        video_urls.append(['.m3u8', url])

    if not (len(video_urls)) == 1: return video_urls

    if not 'master.m3u8' in str(video_urls): return video_urls

    video_urls = servertools.get_parse_hls(video_urls)

    return video_urls

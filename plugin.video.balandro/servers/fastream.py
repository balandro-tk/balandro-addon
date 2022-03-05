# -*- coding: utf-8 -*-

import re

from platformcode import logger
from core import httptools, scrapertools, servertools
from lib import jsunpack

def resolve_patterns(page_url):
    if '/embed-' in page_url:
        return page_url

    server_parameters = servertools.get_server_parameters('fastream')
    patterns = server_parameters.get('find_videos', {}).get('patterns')

    for pattern in patterns:
        for match in re.compile(pattern['pattern'], re.DOTALL).finditer(page_url):
            url = pattern['url']

            for x in range(len(match.groups())):
                url = url.replace('\\{}'.format(x + 1), match.groups()[x])

            page_url = url

    return page_url


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)

    video_urls = []

    if '|' in page_url:
        page_url, referer = page_url.split('|', 1)

    page_url = resolve_patterns(page_url)

    if 'referer' in locals():
         page_url += referer

    data = httptools.downloadpage(page_url).data

    if 'File is no longer available as it expired or has been deleted' in data:
        return 'El archivo no existe o ha sido borrado'

    try:
        packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
        unpacked = jsunpack.unpack(packed)
    except:
        unpacked = ''

    if unpacked:
        data = scrapertools.find_single_match(unpacked, "(?is)var player\s?=.+?sources.+?\[(.+?)\]")
        matches = scrapertools.find_multiple_matches(data, "src:\s?[\"'](.+?)[\"']")
    else:
        data_var = scrapertools.find_single_match(data, "(?is)var player\s?=.+?sources.+?\[(.+?)\]")
        matches = scrapertools.find_multiple_matches(data_var, "src:\s?[\"'](.+?)[\"']")

    if not matches:
        matches = scrapertools.find_multiple_matches(data, 'sources:.*?"(.*?)"')

    for url in matches:
        if 'referer' in locals():
            url += '|Referer={}'.format(referer)

        video_urls.append(['.m3u8', url])

    if not (len(video_urls)) == 1:
        return video_urls

    if not 'master.m3u8' in str(video_urls):
        return video_urls

    video_urls = servertools.get_parse_hls(video_urls)

    return video_urls

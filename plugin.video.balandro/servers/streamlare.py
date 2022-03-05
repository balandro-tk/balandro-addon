# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    vid = scrapertools.find_single_match(page_url, "/v/([A-z0-9]+)")
    if not vid:
        vid = scrapertools.find_single_match(page_url, "/e/([A-z0-9]+)")

    base_url = "https://streamlare.com/api/video/get/"

    data = httptools.downloadpage(base_url, post={'id': vid}).data

    if 'Video file not found' in data:
        return "El archivo no existe o ha sido borrado"

    url = scrapertools.find_single_match(str(data), '"src":"(.*?)"')
    url = url.replace('\\/', '/')

    if url:
        video_urls.append(['mp4', url])

    return video_urls

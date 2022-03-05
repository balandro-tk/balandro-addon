# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    
    vid = scrapertools.find_single_match(page_url, "embed/([A-z0-9_-]+)")
    if not vid: return 'Vídeo no detectado'
    
    data = httptools.downloadpage('https://api.movcloud.net/stream/' + vid).data
    # ~ logger.debug(data)
    
    url = scrapertools.find_single_match(data, '"file":"([^"]+)')
    if url: video_urls.append(["mp4", url])

    return video_urls

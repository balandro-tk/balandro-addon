# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    headers = {}
    if url_referer: headers['Referer'] = url_referer
        
    data = httptools.downloadpage(page_url, headers=headers).data
    # ~ logger.debug(data)

    if "borrado" in data or "Deleted" in data:
        return 'El fichero ha sido borrado'

    if not 'sources' in data:
        ck = scrapertools.find_single_match(data, 'document\.cookie\s*=\s*"([^;]+)')
        if ck:
            headers['Cookie'] = ck
            data = httptools.downloadpage(page_url, headers=headers).data
            # ~ logger.debug(data)

    bloque = scrapertools.find_single_match(data, 'sources:.\[.*?\]')
    matches = scrapertools.find_multiple_matches(bloque, '(http.*?)"')
    for videourl in matches:
        extension = scrapertools.get_filename_from_url(videourl)[-4:]
        # ~ video_urls.append([extension, videourl])
        video_urls.append([extension, videourl+'|Referer=https://vidlox.me/'])

    # ~ video_urls.reverse() # calidad increscendo !?
    return video_urls

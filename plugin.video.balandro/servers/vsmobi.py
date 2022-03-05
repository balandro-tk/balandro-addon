# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger

def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []
    
    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    bloque = scrapertools.find_single_match(data, 'file: "([^"]+)')
    # ~ file: "[240p]https://dst1.v-s.mobi/fzRIpgTgles7FldwoJnYPSHkSvYGt3dexUXJwqS3ZFk/240p.mp4,[360p]https://dst1.v-s.mobi/fzRIpgTgles7FldwoJnYPSHkSvYGt3dexUXJwqS3ZFk/360p.mp4",
    
    for vid in bloque.split(','):
        lbl = scrapertools.find_single_match(vid, '\[([^\]]+)\]')
        if lbl: 
            url = vid.replace('[%s]' % lbl, '')
        else:
            lbl = 'mp4'
            url = vid
        video_urls.append([lbl, url+'|Referer=https://v-s.mobi/'])

    return video_urls

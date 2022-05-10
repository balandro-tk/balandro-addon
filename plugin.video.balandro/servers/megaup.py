# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)
    
    url = scrapertools.find_single_match(data, "href='([^']+)'>download now</a>")
    if url:
        import time
        from platformcode import platformtools
        espera = 6
        platformtools.dialog_notification('Cargando MegaUp', 'Espera de %s segundos requerida' % espera)
        time.sleep(int(espera))
        
        headers = { 'Referer': page_url }
        url = httptools.downloadpage(url, headers=headers, follow_redirects=False, only_headers=True).headers.get('location', '')

        if url:
            video_urls.append(['mp4', url])

    return video_urls

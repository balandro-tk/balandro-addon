# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    if '/download/videos/' in page_url:
        video_urls.append(['mp4', page_url])
        return video_urls

    vid = scrapertools.find_single_match(page_url, '(?:watch|embed)/([A-z0-9\-]+)')
    if not vid: return video_urls
    
    dom = '/'.join(page_url.split('/')[:3])

    try:
        data = httptools.downloadpage(dom + '/api/v1/videos/' + vid).data
        # ~ logger.debug(data)

        data_json = jsontools.load(data)
        try:
            lista = sorted(data_json['files'], key=lambda x: x['resolution']['id'])
        except:
            lista = data_json['files']
        
        for vid in lista:
            if 'fileDownloadUrl' not in vid: continue
            url = vid['fileDownloadUrl']
            if url.startswith('/'): url = dom + url

            try: 
                lbl = ['resolution']['label']
            except:
                lbl = None
            if not lbl: lbl = 'mp4'

            video_urls.append([lbl, url])
    except:
        pass

    return video_urls

'''
https://peertube.fr/videos/embed/3f661b5d-cea9-4416-86ee-284e220b6287
https://peertube.servebeer.com/videos/embed/7caeeb51-43c6-4bb0-82b6-92185c952111
https://lostpod.space/videos/watch/755d0a1c-2fe8-4839-b802-912c9fd6fe83
https://video.ploud.fr/videos/embed/868ae794-9fa9-48a1-a34b-b5847bdfba8e
https://tube.midov.pl/videos/embed/e4e1d387-53f0-45e9-a36a-e72ea85f0b59
https://peertube.librelabucm.org/videos/watch/c362d544-80b1-4c1f-8c39-80a4fdb0a7d9

https://video.fdlibre.eu/download/videos/c362d544-80b1-4c1f-8c39-80a4fdb0a7d9-720.mp4
https://video.fdlibre.eu/download/videos/c362d544-80b1-4c1f-8c39-80a4fdb0a7d9-1440.mp4
'''
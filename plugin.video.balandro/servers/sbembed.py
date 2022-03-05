# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('/e/', '/play/').replace('/d/', '/play/')
    page_url = page_url.replace('embed-', '')

    data = httptools.downloadpage(page_url).data

    if "was not found on this server" in data:
        return 'El fichero no existe o ha sido borrado'

    packed = scrapertools.find_single_match(data, "text/javascript'>(eval.*?)\s*</script>")
    unpacked = jsunpack.unpack(packed)
    matches = scrapertools.find_multiple_matches(unpacked, r'sources:\[\{\s*file:"([^"]+)"')

    for video_url in matches:
        video_urls.append(['m3u8', video_url])

    return video_urls

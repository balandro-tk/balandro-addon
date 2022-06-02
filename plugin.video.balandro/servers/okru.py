# -*- coding: utf-8 -*-

import re

from core import httptools, scrapertools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("url=" + page_url)
    video_urls = []

    data = httptools.downloadpage(page_url).data

    if "copyrightsRestricted" in data or "COPYRIGHTS_RESTRICTED" in data:
        return 'El archivo ha sido eliminado por violación del copyright'
    elif "notFound" in data:
        return 'El archivo no existe o ha sido eliminado'

    data = scrapertools.decodeHtmlentities(data).replace('\\', '')

    for tipo, url in re.findall(r'\{"name":"([^"]+)","url":"([^"]+)"', data, re.DOTALL):
        url = url.replace("%3B", ";").replace("u0026", "&")
        video_urls.append([tipo, url])

    return video_urls

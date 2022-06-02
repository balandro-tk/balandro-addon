# -*- coding: utf-8 -*-

from core import httptools, scrapertools, jsontools
from platformcode import logger


def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    id = scrapertools.find_single_match(page_url, '/e/(\w+)')

    post = {"id": id}

    data = httptools.downloadpage("https://streamlare.com/api/video/stream/get", post=post).data

    jdata = jsontools.load(data)

    try:
        media_url = jdata["result"]["file"]
    except:
        media_url = scrapertools.find_single_match(str(jdata), ".*?'file': '(.*?)'")

    if media_url:
        video_urls.append(["m3u", media_url])

    return video_urls

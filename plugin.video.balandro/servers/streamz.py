# -*- coding: utf-8 -*-

from core import httptools, scrapertools
from platformcode import logger
from lib import jsunpack

def get_video_url(page_url, url_referer=''):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []

    page_url = page_url.replace('streamz.cc/', 'streamzz.to/').replace('streamz.vg/', 'streamzz.to/').replace('streamz.ws/', 'streamzz.to/').replace('streamz.to/', 'streamzz.to/')

    data = httptools.downloadpage(page_url).data
    # ~ logger.debug(data)

    httptools.downloadpage('https://streamzz.to/count.php?bcd=1')

    packeds = scrapertools.find_multiple_matches(data, "function\(p,a,c,k.*?</script>")
    for packed in packeds:
        unpacked = jsunpack.unpack(packed)
        # ~ logger.info(unpacked)

        url = scrapertools.find_single_match(unpacked.replace("\\'", "'"), "src:'([^']+)")
        if url and url.startswith('http') and 'getlink' in url:
            lbl = scrapertools.find_single_match(unpacked, 'var (\w+)')
            url = httptools.downloadpage(url, headers={'Referer': page_url}, follow_redirects=False, only_headers=True).headers.get('location', '')
            if url:
                if '/issue.mp4' in url: continue

                url += "|User-Agent=%s" % httptools.get_user_agent()

                video_urls.append(['mp4 '+ lbl, url])

    return video_urls

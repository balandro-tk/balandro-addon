# -*- coding: utf-8 -*-

import sys, random

from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools


host = 'https://www.documaniatv.com/'

metodos = ['0', '1', '2', '3', '4', 'Aleatorio']

cnomv = 'DocumaniaTv'
canal = 'documaniatv'

url_check_header = host + 'article.html'

plot = 'Es posible que para poder utilizar este canal necesites configurar algún proxy, ya que no es accesible desde algunos países/operadoras.'
plot += '[CR]Si desde un navegador web no te funciona el sitio ' + host + ' necesitarás un proxy.'

tex_cpau = '[COLOR yellow]O bien, si persiste este aviso vuelva a [/COLOR][COLOR red] Configurar proxies a usar ...[/COLOR]'
tex_esrn = ' por favor espere unos segundos ... y Reintentelo de nuevo'
tex_inua = '[COLOR red] Agente inválido. [/COLOR][COLOR yellow] '

perpage = 25

documaniatv_rua = config.get_setting('channel_documaniatv_rua', default='')

if config.get_setting('developer_mode', default=False): developer = True
else: developer = False

# Versiones Chrome
cod_cver = [70, 71, 78, 79, 80, 81, 83, 84, 85, 86, 87, 88, 89, 90, 91]

cver = random.choice(cod_cver)
alea = random.randint(3000, 4000)
verc = '%s.0.%s.100'  % (cver, alea)

# Versiones Firefox
cod_fver = [60, 66, 68, 70, 72, 73, 74, 76, 77, 78, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91]
fver = random.choice(cod_fver)

ff_versions = [78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96]  # (Windows NT 10.0; Win64; x64; rv:%s.0)
ff_rnd = str(random.choice(ff_versions))

# last chrome
ver_chrome = ''
if config.get_setting("ver_stable_chrome", default=True):
    if config.get_setting('chrome_last_version', default=''): ver_chrome = config.get_setting('chrome_last_version')

# Lista custom_headers
list_headers = []

list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:%s.0) Gecko/20100101 Firefox/%s.0' % (fver, fver)})

if ver_chrome:
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36' % ver_chrome})
else:
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36' % verc})

list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36 Firefox/%s.0' % (verc, fver)})

list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:%s.0) Gecko/20100101 Firefox/%s.0' % (ff_rnd, ff_rnd)})

list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:%s.0) Safari/537.36 (KHTML, like Gecko) Chrome/%s Gecko/20100101 Firefox/%s.0' % (fver, verc, fver)})

if developer == True:
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:%s.0) Gecko/20100101 Firefox/%s.0' % (fver, fver)})

    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)'})
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Firefox/%s.0' % (fver)})

    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; + http://www.google.com/bot.html) Chrome/%s Safari/537.36 Gecko/20100101 Firefox/%s.0' % (verc, fver)})
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; + http://www.google.com/bot.html) (Chrome/W.X.Y.Z; Chrome/%s) Safari/537.36 Gecko/20100101 Firefox/%s.0' % (verc, fver)})

    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36 Gecko/20100101 Firefox/%s.0' % (verc, fver)})

    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N; X11; Linux x86_64) (compatible; MSIE 7.0; Windows NT 10.0; WOW64; rv:%s.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506) Chrome/%s Firefox/%s.0' % (fver, verc, fver)})
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) (Windows NT 10.0; WOW64; rv:%s.0; Win64; x64; U) (Macintosh; Intel Mac OS X 10.8; rv:%s.0) Gecko/20100101 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36 Firefox/%s.0' % (fver, fver, verc, fver)})

    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Version/10.0 Mobile/14D27 Chrome/%s Safari/537.36 Firefox/%s.0' % (verc, fver)})

    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) (Windows NT 10.0; WOW64; rv:%s.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36 Gecko/20100101 Firefox/%s.0' % (fver, verc, fver)})

    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/%s Mobile Safari/537.36  Firefox/%s.0' % (verc, fver)})

    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36 Firefox/%s.0' % (verc, fver)})
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:%s.0) Chrome/%s Gecko/20100101 Firefox/%s.0' % (fver, verc, fver)})
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:%s.0) Chrome/%s Safari/537.36 Gecko/20100101 Firefox/%s.0' % (fver, verc, fver)})
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36 Gecko/20100101 Firefox/%s.0' % (verc, fver)})
    list_headers.append({'Referer': host, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:%s.0) Chrome/%s Gecko/20100101 Firefox/%s.0' % (fver, verc, fver)})


def localize_header(test, last_chrome):
    documaniatv_rua = config.get_setting('channel_documaniatv_rua', default='')

    if developer == True:
        if test == True:
            ver = verc
            if not last_chrome == '': ver = last_chrome
            platformtools.dialog_ok(cnomv, 'Test con releases Chrome [COLOR yellow][B] %s [/B][/COLOR], y Firefox [COLOR yellow][B] %s [/B][/COLOR]' % (str(ver), str(fver)))

    headers_check = ''

    test_ua_validos = 0

    documaniatv_proxies = config.get_setting('channel_documaniatv_proxies', default='')

    if documaniatv_proxies == '': return headers_check, ''
    else:
       if ';' in documaniatv_proxies: documaniatv_proxies = documaniatv_proxies.replace(',', ';').split(';')
       else: documaniatv_proxies = documaniatv_proxies.split(',')

    elements = len(list_headers)

    for ilh in range(0, elements):
        headers_check = list_headers[ilh]

        if developer == True:
            if test == True:
                if not last_chrome == '':
                   if verc in str(headers_check):
                      headers_old = str(headers_check['User-Agent'])
                      headers_new = headers_old.replace(verc, last_chrome)
                      headers_check = {'Referer': host, 'User-Agent': headers_new}
                   else: continue

        eletab = ilh + 1

        if test == False:
            if str(documaniatv_rua) == '': break
        else: platformtools.dialog_notification(cnomv, 'Test Agente [COLOR yellow] %s [/COLOR] de %s' % (str(eletab), str(elements)))

        data = ''

        try:
            if test == False:
                if len(documaniatv_proxies) >= 2: platformtools.dialog_notification(cnomv, '[COLOR yellow]Cursando acceso proxy[/COLOR]')

            resp = do_downloadpage(canal, url = url_check_header, headers = headers_check)
            data = resp.data

            if developer == True:
                if test == True:
                    if host in data: platformtools.dialog_notification(cnomv, + '[COLOR blue]' + str(eletab) + '[/COLOR]')

            if not host in data: data = ''
            elif len(data) == 0: data = ''

            if data: test_ua_validos += 1
        except:
            if developer == True: platformtools.dialog_ok(cnomv + '  Rua: [COLOR blue]' + str(eletab) + '[/COLOR]', tex_inua + 'Error[/COLOR]', str(headers_check))

        try:
            if not data == '':
                if 'Problema detectado con navegador' in data:
                    if developer == True: platformtools.dialog_ok(cnomv + '  Rua: [COLOR blue]' + str(eletab) + '[/COLOR]', tex_inua + 'Comtrol ' + str(resp) + ' [/COLOR][COLOR cyan] Problema navegador[/COLOR]', str(headers_check['User-Agent']))
                else:
                    if type(resp.code) == int and resp.code == 410 or resp.code == 403:
                        if developer == True: platformtools.dialog_ok(cnomv + '  Rua: [COLOR blue]' + str(eletab) + '[/COLOR]', tex_inua + 'Respuesta ' + str(resp.code) + '[/COLOR]', str(headers_check['User-Agent']))
        except: pass

        if data == '':
            if test == False:
                if not str(documaniatv_rua) == '': break

                platformtools.dialog_notification(cnomv, 'Cursando consulta [COLOR yellow]%s[/COLOR]' % str(eletab))
                if eletab >= 4: break
            else: platformtools.dialog_ok(cnomv + '  Rua: [COLOR blue]' + str(eletab) + '[/COLOR]', tex_inua + 'Test ' + str(resp.error) + '[/COLOR]', str(headers_check['User-Agent']))

            headers_check = ''
            continue

        if test == True: continue

        break

    if headers_check == '':
       if developer == True:
           if test_ua_validos == 0: platformtools.dialog_ok(cnomv, 'Ningun agente válido' + tex_esrn, '', tex_cpau)

       if test == False: ilh = ''

    return headers_check, ilh


def obtener_last_chrome():
    ver_stable_chrome = config.get_setting("ver_stable_chrome", default=True)

    if ver_stable_chrome:
        cfg_last_ver_chrome = config.get_setting('chrome_last_version', default='')
        if not cfg_last_ver_chrome == '': last_chrome = cfg_last_ver_chrome
    else:
        try:
           data = httptools.downloadpage('https://omahaproxy.appspot.com/all?csv=1').data
           last_chrome = scrapertools.find_single_match(data, "win64,stable,([^,]+),")
           if not last_chrome: last_chrome = None
        except:
           last_chrome = None

    return last_chrome


def test_headers(item):
    documaniatv_proxies = config.get_setting('channel_documaniatv_proxies', default='')

    if documaniatv_proxies == '':
        platformtools.dialog_notification(cnomv, '[COLOR red]No hay proxies configurados[/COLOR]')
        return

    si_no = platformtools.dialog_yesno(cnomv, '[COLOR yellow]Test Solo con el último release de Chrome ?[/COLOR]')

    last_chrome = ''
    if str(si_no) == '1': last_chrome = obtener_last_chrome()

    localize_header(True, last_chrome)


def configurar_metodo(item):
    metodo = config.get_setting('channel_documaniatv_rua', default='')

    if metodo:
        if str(metodo) == '0': num_metodo = 0
        elif str(metodo) == '1': num_metodo = 1
        elif str(metodo) == '2': num_metodo = 2
        elif str(metodo) == '3': num_metodo = 3
        elif str(metodo) == '4': num_metodo = 4
        else:
           cod_metod = [0, 1, 2, 3, 4]
           fmet = random.choice(cod_metod)
           num_metodo = fmet
    else: num_metodo = 0

    ret = platformtools.dialog_select('DocumaniaTv - Métodos de acceso', metodos, preselect=num_metodo)
    if ret == -1: return False

    if metodos[ret] == 'Aleatorio':
        cod_metod = [0, 1, 2, 3, 4]
        fmet = random.choice(cod_metod)
        metodos[ret] = fmet

    config.set_setting('channel_documaniatv_rua', metodos[ret])

    return True


def configurar_proxies(item):
    from core import proxytools
    return proxytools.configurar_proxies_canal(item.channel, host)


def do_downloadpage(url, headers=None, post=None):
    timeout = 40

    data = httptools.downloadpage_proxy(canal, url=url, headers=headers, post=post, timeout=timeout, bypass_cloudflare=False).data

    if data:
        if not host in data:
            if developer == True:
                platformtools.dialog_notification(cnomv, '[COLOR red]Posible bloqueo IP ó hidden CAPTCHA[/COLOR]')
                return ''

    return data


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone ( title = 'Configurar método acceso a usar ... [COLOR plum](si bloqueo ó sin resultados)[/COLOR]',
                                 action = 'configurar_metodo', folder = False, text_color = 'yellowgreen' ))

    itemlist.append(item.clone ( title = 'Configurar proxies a usar ... [COLOR plum](si bloqueo ó sin resultados)[/COLOR]',
                                 action = 'configurar_proxies', folder = False, plot = plot, text_color = 'red' ))

    itemlist.append(item.clone( title = 'Buscar documental ...', action = 'search', search_type = 'documentary', text_color='cyan' ))

    itemlist.append(item.clone( title = 'Catálogo', action = 'newvideos' ))
    itemlist.append(item.clone( title = 'Top 100', action = 'top_100' ))
    itemlist.append(item.clone( title = 'Por canal', action = 'canales' ))
    itemlist.append(item.clone( title = 'Por categoría', action = 'categorias' ))
    itemlist.append(item.clone( title = 'Por tema', action = 'series', url = host + 'top-series-documentales.html' ))

    if developer == True: itemlist.append(item.clone ( title = 'Test agentes a utilizar ...', action = 'test_headers', folder = False, text_color = 'yellow' ))

    documaniatv_proxies = config.get_setting('channel_documaniatv_proxies', default='')

    if documaniatv_proxies == '': platformtools.dialog_notification(cnomv, '[COLOR red]No hay proxies configurados[/COLOR]')
    else:
       if str(documaniatv_rua) == '': platformtools.dialog_notification(cnomv, '[COLOR red]Se requieren nuevos proxies[/COLOR]')

    return itemlist


def newvideos(item):
    logger.info()
    itemlist = []

    referer = host + 'documentales-nuevos.html'

    url = host + 'documentales-nuevos.html'
    itemlist.append(item.clone( title = 'Últimos', action = 'list_all', url = url, referer = referer ))

    url = host + 'documentales-nuevos.html?d=month'
    itemlist.append(item.clone( title = 'Los de este mes', action = 'list_all', url = url, referer = referer ))

    url = host + 'documentales-nuevos.html?d=yesterday'
    itemlist.append(item.clone( title = 'Los de ayer', action = 'list_all', url = url, referer = referer ))

    url = host + 'documentales-nuevos.html?d=today'
    itemlist.append(item.clone( title = 'Los de hoy', action = 'list_all', url = url, referer = referer ))

    return itemlist


def top_100(item):
    logger.info()
    itemlist = []

    url = 'top-documentales.html'
    
    referer = host + url
    
    itemlist.append(item.clone( title = 'Top 100 documentales', action = 'list_all', url = host + url, page = 0, referer = referer))
    itemlist.append(item.clone( title = 'Top 100 más Populares', action = 'list_all', url = host + url + '?do=rating', page = 0 , referer = referer))
    itemlist.append(item.clone( title = 'Top 100 más Recientes', action = 'list_all', url = host + url +'?do=recent', page = 0 , referer = referer))
    itemlist.append(item.clone( title = 'Top 100 de Arte y Cine', action = 'list_all', url = host + url + '?c=arte-y-cine', page = 0 , referer = referer))
    itemlist.append(item.clone( title = 'Top 100 de Biografías', action = 'list_all', url = host + url + '?c=biografias' , referer = referer))
    itemlist.append(item.clone( title = 'Top 100 de Ciencia y Tecnología', action = 'list_all', url = host + url + '?c=ciencia-y-tecnologia', page = 0, referer = referer ))
    itemlist.append(item.clone( title = 'Top 100 de Deporte', action = 'list_all', url = host + url + '?c=deporte', page = 0 , referer = referer))
    itemlist.append(item.clone( title = 'Top 100 de Historia', action = 'list_all', url = host + url + '?c=historia', page = 0, referer = referer ))
    itemlist.append(item.clone( title = 'Top 100 de Naturaleza', action = 'list_all', url = host + url + '?c=naturaleza', page = 0, referer = referer ))
    itemlist.append(item.clone( title = 'Top 100 de Política', action = 'list_all', url = host + url + '?c=politica', page = 0 , referer = referer))
    itemlist.append(item.clone( title = 'Top 100 de Social', action = 'list_all', url = host + url + '?c=social', page = 0 , referer = referer))
    itemlist.append(item.clone( title = 'Top 100 de Viajes', action = 'list_all', url = host + url + '?c=viajes', page = 0 , referer = referer))

    return itemlist


def canales(item):
    logger.info()
    itemlist = []

    url = host + 'documentales/bbc/'
    itemlist.append(item.clone( action = 'list_all', title = 'BBC', url = url, referer = url ))

    url = host + 'documentales/documentos-tv/'
    itemlist.append(item.clone( action = 'list_all', title = 'Documentos tv', url = url, referer = url ))

    url = host + 'documentales/history-channel/'
    itemlist.append(item.clone( action = 'list_all', title = 'History channel', url = url, referer = url ))

    url = host + 'documentales/la-noche-tematica/'
    itemlist.append(item.clone( action='list_all', title = 'La noche temática', url = url, referer = url ))

    url = host + 'documentales/national-geographic/'
    itemlist.append(item.clone( action='list_all', title = 'National geographic', url = url, referer = url ))

    url = host + 'documentales/segunda-guerra-mundial/'
    itemlist.append(item.clone( action='list_all', title = 'Segunda guerra mundial', url = url, referer = url ))

    return itemlist


def categorias(item):
    logger.info()
    itemlist = []

    documaniatv_proxies = config.get_setting('channel_documaniatv_proxies', default='')
    
    if documaniatv_proxies == '':
        platformtools.dialog_notification(cnomv, '[COLOR red]No hay proxies configurados[/COLOR]')
        return

    #data = do_downloadpage(host, headers = custom_headers)
    item.url=host
    
    data=get_data(item)
    
    bloque = scrapertools.find_single_match(data, '<ul class="dropdown-menu">(.*?)</ul>')

    matches = scrapertools.find_multiple_matches(bloque, '<a href="([^"]+)".*?class="">([^<]+)')

    for url, title in matches:
        if 'documentales/' in url: continue

        itemlist.append(item.clone ( action = 'list_all', title = title, url = url ))

    return sorted(itemlist, key=lambda it: it.title)


def series(item):
    logger.info()
    itemlist = []

    documaniatv_proxies = config.get_setting('channel_documaniatv_proxies', default='')

    if documaniatv_proxies == '':
        platformtools.dialog_notification(cnomv, '[COLOR red]No hay proxies configurados[/COLOR]')
        return

    acces_headers = custom_headers
    if item.referer: acces_headers['Referer'] = item.referer

    #data = do_downloadpage(item.url, headers = acces_headers)
    data=get_data(item)
    matches = scrapertools.find_multiple_matches(data, '<div class="pm-li-category">.*?<a href="([^"]+)".*?title="(.*?)".*?<img src="(.*?)"')

    for url, title, thumb in matches:
        title = title.capitalize()

        if title == 'Bbc': continue
        elif title == 'Documentos tv': continue
        elif title == 'History channel': continue
        elif title == 'La noche tematica': continue
        elif title == 'National geographic': continue
        elif title == 'Segunda guerra mundial' in url: continue

        itemlist.append(item.clone ( action = 'list_all', title = title, thumbnail = thumb, url = url ))

    next_page_link = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')

    if next_page_link:
       itemlist.append(item.clone ( title = 'Siguientes ...', action = 'series', url = next_page_link, referer = next_page_link, text_color='coral' ))

    return itemlist


def list_all(item):
    logger.info()
    itemlist = []
    
        
    documaniatv_proxies = config.get_setting('channel_documaniatv_proxies', default='')

    if documaniatv_proxies == '':
        platformtools.dialog_notification(cnomv, '[COLOR red]No hay proxies configurados[/COLOR]')
        return
    else:
        data=get_data(item)
    
    matches = scrapertools.find_multiple_matches(data, '<li class="col-xs-6 col-sm-6 col-md-4">(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<li class="col-xs-6 col-sm-6 col-md-3">(.*?)</li>')
    if not matches: matches = scrapertools.find_multiple_matches(data, '<li class="col-xs-6 col-sm-4 col-md-3">(.*?)</li>')

    num_matches = len(matches)
    desde = 0
    hasta = num_matches

    if item.page:
        desde = item.page * perpage
        hasta = desde + perpage

    for article in matches[desde:hasta]:
        url, title = scrapertools.find_single_match(article, '<a href="([^"]+)".*?title="([^"]+)"')

        thumb = scrapertools.find_single_match(article, 'data-echo="([^"]+)"')
        durada = scrapertools.htmlclean(scrapertools.find_single_match(article, '<span class="pm-label-duration">(.*?)</span>'))

        if durada: durada = '[COLOR tan](%s)[/COLOR]' % durada

        itemlist.append(item.clone ( action = 'findvideos', url = url, title = title, thumbnail = thumb, 
                                     fmt_sufijo = durada, contentType = 'movie', contentTitle = title, contentExtra = 'documentary' ))

    next_page_link = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)"')

    if not next_page_link:
        if '/documentales-nuevos.html?d=month' in item.url or '/search.php?keywords=' in item.url:
            next_page_link = scrapertools.find_single_match(data, '"Pagination">.*?<li class="active">.*?<li class="">.*?</li>.*?href="(.*?)"')
            if next_page_link:
                if not next_page_link.startswith('http'): next_page_link = host + next_page_link

    if next_page_link:
        itemlist.append(item.clone ( title = 'Siguientes ...', action = 'list_all', url = next_page_link, referer = next_page_link, text_color='coral' ))
    else:
        if item.page:
            if num_matches > hasta: itemlist.append(item.clone( title='Siguientes ...', page = item.page + 1, action = 'list_all', text_color='coral' ))

    return itemlist

def get_data(item):
    import requests
    data=''
    
    documaniatv_proxies = config.get_setting('channel_documaniatv_proxies', default='')
    
    cookies={}
    proxies={}
    
    for proxy in documaniatv_proxies.split(','):
        proxies['http']= proxy
        # En el momento que forzamos proxies por https, nos salta por browser-sin-javascript
        #proxies['https']= proxy

        headers={'referer': item.referer, 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
        
        if item.url.startswith('/'): 
            url=host+item.url 
        else: 
            url=item.url
        
        #data = do_downloadpage(item.url, headers = acces_headers)
        
        session=requests.Session()
        session = requests.get(url, headers = headers, proxies=proxies,verify=False)
        cookies=session.cookies.get_dict() 
        if cookies=={}:
            cookies={'__HOST-PHPSESSID':'Sc9hd6V%2CLDHr9OYYz0QgNbmJgyLWokKyVeeZsbHsyQ9B1tN0','docu-token':        'TW9uZGF5TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzk2LjAuNDY2NC4xMTAgU2FmYXJpLzUzNy4zNg%3D%3D'}
        
        data=session.text.replace('\n','')

        if data=='': data = requests.get(item.url, headers = headers,cookies=cookies,proxies=proxies,veryfy=False).text.replace('\n','')
        if data!='': break 
    
    return data
    
def findvideos(item):
    logger.info()
    itemlist = []

    notification_d_ok = config.get_setting('notification_d_ok', default=True)

    acces_headers = custom_headers
    acces_headers['Referer'] = item.url

    #data = do_downloadpage(item.url, headers = acces_headers)
    data=get_data(item)
        
    if len(data) == 0:
        import time
        espera = 5

        platformtools.dialog_notification('Re-Cargando vídeo', 'Espera requerida de %s segundos' % espera)
        time.sleep(int(espera))

        #data = do_downloadpage(item.url, headers = acces_headers)
        data=get_data(item)
    if 'lo sentimos este documental ha sido eliminado' in data.lower():
        platformtools.dialog_notification(cnomv, '[COLOR red]Documental eliminado[/COLOR]')
        return

    elif '<div class="alert alert-danger"' in data:
        if ' de mantenimiento' in data.lower() or ' retornar a la normalidad' in data.lower():
            if notification_d_ok: platformtools.dialog_ok(cnomv, 'Canal en Mantenimiento')
            else: platformtools.dialog_notification(cnomv, '[COLOR moccasin]Canal en Mantenimiento[/COLOR]')
            return

    elif '<meta name="captcha-bypass"' in data:
        platformtools.dialog_ok(cnomv, '[COLOR cyan]Vídeo temporalmente bloqueado,' + tex_esrn + '[/COLOR]', '', tex_cpau)
        return

    url_final = ''

    url_embed = scrapertools.find_single_match(data, '"VideoObject".*?' + item.url + '.*?https:(.*?)"')

    if not url_embed:
        if '"contentUrl":"' in data: url_embed = scrapertools.find_single_match(data, '"contentUrl":"(.*?)"')

        if not url_embed:
            if '<iframe src="' in data: 
                url_embed = scrapertools.find_single_match(data, '<iframe src="(//cnubis\.com/[^"]+)')
                if not url_embed: url_embed = scrapertools.find_single_match(data, '<iframe src="(https://cnubis\.com/[^"]+)')

        if not url_embed:
            if '"Playerholder"' in data: url_embed = scrapertools.find_single_match(data, '"Playerholder".*?file:.*?"(.*?)"')

        if not url_embed:
            if '"VideoPlay"' in data: url_embed = scrapertools.find_single_match(str(data), '"VideoPlay".*?file:.*?"(.*?)"')

        if not url_embed:
            if '"TheVid"' in data: url_embed = scrapertools.find_single_match(str(data), '"TheVid".*?file:.*?"(.*?)"')

        if not url_embed:
            if '/age-verification.js' in data:
                descartar_xxx = config.get_setting('descartar_xxx', default=False)
                if descartar_xxx:
                    platformtools.dialog_notification(cnomv, '[COLOR moccasin]Temática para adultos[/COLOR]')
                    return

        if not url_embed:
            url_embed = scrapertools.find_single_match(data, 'https://fs1.cnubis.com/(.*?)"')
            if url_embed: url_embed = 'https://fs1.cnubis.com/' + url_embed

    if url_embed:
        if url_embed.startswith('//'): url_embed = 'https:' + url_embed

        if url_embed.endswith('mp4') == True: url = url_embed
        else:
           data = do_downloadpage(url_embed, headers = custom_headers)

           if '<meta name="captcha-bypass"' in data:
               platformtools.dialog_ok(cnomv, '[COLOR blue]Vídeo transitoriamente bloqueado,' + tex_esrn + '[/COLOR]', '', tex_cpau)
               return

           url = scrapertools.find_single_match(data, 'id="jwPlayerContainer">Cargando video.*?file:.*?"(.*?)"')

        if url:
            if url.startswith('//'): url = 'https:' + url
            if url.endswith('mp4') == False: url = url + '&.mp4'

            url_final = url

    if not url_final:
        url_final = scrapertools.find_single_match(data, '<div id="player".*?jwplayer.*?playlist:.*?"(.*?)"')
        if not url_final:
            url_final = scrapertools.find_single_match(data, '<div id="player".*?jwplayer.*?file:.*?"(.*?)"')

        if url_final.startswith(host):
            data = do_downloadpage(url_final, headers = acces_headers)
            url_final = scrapertools.find_single_match(data, '"file":"(.*?)"')

            if not url_final:
                platformtools.dialog_notification(cnomv, '[COLOR violet]Parece que hay bloqueo de IP[/COLOR]')
                return

        if url_final.endswith('mp4') == False: url_final = ''

    if url_final:
        if url_final.startswith(host):
            data = do_downloadpage(url_final, headers = acces_headers)
            url_final = scrapertools.find_single_match(data, '"file":"(.*?)"')

            if not url_final:
                platformtools.dialog_notification(cnomv, '[COLOR violet]Al parecer hay bloqueo de IP[/COLOR]')
                return

    if not url_final:
        if len(data) == 0: platformtools.dialog_ok(cnomv, '[COLOR tan]Vídeo sin respuesta del canal,' + tex_esrn + '[/COLOR]', '', tex_cpau)
        else: platformtools.dialog_notification(cnomv, '[COLOR violet]Al parecer cambió la estructura[/COLOR]')
        return

    itemlist.append(Item ( channel = item.channel, action = 'play', server = 'directo', title = '', url = url_final, language = 'Esp' ))

    return itemlist


def search(item, texto):
    logger.info()
    try:
        documaniatv_proxies = config.get_setting('channel_documaniatv_proxies', default='')

        if documaniatv_proxies == '': return []

        item.url = host + 'search.php?keywords=' + texto.replace(" ", "+")
        return list_all(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# Primer custom_headers valido
configurar_test = False

if sys.argv[2]:
    if str(sys.argv[1]) == '-1': configurar_test = True

if configurar_test == False:
    if not str(documaniatv_rua) == '': custom_headers = list_headers[documaniatv_rua]
    else:
        custom_headers, index = localize_header(False, '')
        if not index == '':
            config.set_setting('channel_documaniatv_rua', index)
            custom_headers = list_headers[index]
        else: custom_headers = ''
else:
   if not str(documaniatv_rua) == '': custom_headers = list_headers[documaniatv_rua]
   else: custom_headers = ''

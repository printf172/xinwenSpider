# -*- coding: utf-8 -*-
# @Time    : 12/11/20 5:14 PM
# @Author  : wangjie
import re
import time
from types import resolve_bases

import requests
from pymysql.converters import escape_string


def test01():
    str = 'http://www.ordosds.jcy.gov.cn/jcyw/index.shtml'
    findall = re.split('/', str)
    print(findall[len(findall) - 1])

def test02():
    uri1 = "www.ordos.gov.cn"
    s = time.time()
    if re.search('www.nmwushen.jcy.gov.cn|www.wsqzx.gov.cn|wsqdjw.gov.cn|wsqrd.gov.cn|www.wsq.gov.cn|eeds.nmgbb.gov.cn|www.ordosds.jcy.gov.cn|dsdj.gov.cn|www.dsgqt.gov.cn|www.ordosdsrd.gov.cn|www.ds.gov.cn|nyj.ordos.gov.cn|fpb.ordos.gov.cn|sjj.ordos.gov.cn|ordosqyg.org.cn|ordosbwg.org.cn|xfj.ordos.gov.cn|sthjj.ordos.gov.cn|cgj.ordos.gov.cn|www.ordos.jcy.gov.cn|zrzyj.baotou.gov.cn|ga.ordos.gov.cn|ordoszk.gov.cn|sfj.ordos.gov.cn|dzj.ordos.gov.cn|ordosdj.gov.cn|tjj.ordos.gov.cn|ordosdx.cn|ordosfl.gov.cn|zjj.ordos.gov.cn|yjglj.ordos.gov.cn|kjj.ordos.gov.cn|jtj.ordos.gov.cn|ordosredcross.org.cn|nmj.ordos.gov.cn|fgw.ordos.gov.cn|rsj.ordos.gov.cn|czj.ordos.gov.cn|www.ordos.gov.cn', uri1):
        pass
    e = time.time()
    print(e - s)

    s = time.time()
    list = ['www.nmwushen.jcy.gov.cn','www.wsqzx.gov.cn','wsqdjw.gov.cn','wsqrd.gov.cn','www.wsq.gov.cn','eeds.nmgbb.gov.cn','www.ordosds.jcy.gov.cn','dsdj.gov.cn','www.dsgqt.gov.cn','www.ordosdsrd.gov.cn','www.ds.gov.cn','nyj.ordos.gov.cn','fpb.ordos.gov.cn','sjj.ordos.gov.cn','ordosqyg.org.cn','ordosbwg.org.cn','xfj.ordos.gov.cn','sthjj.ordos.gov.cn','cgj.ordos.gov.cn','www.ordos.jcy.gov.cn','zrzyj.baotou.gov.cn','ga.ordos.gov.cn','ordoszk.gov.cn','sfj.ordos.gov.cn','dzj.ordos.gov.cn','ordosdj.gov.cn','tjj.ordos.gov.cn','ordosdx.cn','ordosfl.gov.cn','zjj.ordos.gov.cn','yjglj.ordos.gov.cn','kjj.ordos.gov.cn','jtj.ordos.gov.cn','ordosredcross.org.cn','nmj.ordos.gov.cn','fgw.ordos.gov.cn','rsj.ordos.gov.cn','czj.ordos.gov.cn','www.ordos.gov.cn']
    for i in list:
        if uri1.__contains__(uri1):
            break
    e = time.time()
    print(e - s)

def test03():
    str= 'http://www.yjhlzx.gov.cn/zxhy/zxhy/'
    findall = re.findall('/?(.*?)/', str)
    str_len = len(findall[len(findall) - 1])
    print(str_len)
    print(str[:-(str_len+1)])

def test04():
    str=r" ../jgdj/dwgk/"
    if str.startswith('..'):
        print(1)

def test05():
    str="http://eeds.nmgbb.gov.cn/wsq/xzd_wsq/zxdt_wsq/tzgg_wsq/201901/t20190125_171654.html"
    split = str.split('/')
    print(split[len(split) - 1])

def test06():
    str = '2006-04-20 16:06:30'
    search = re.search('(.*)-(.*)-(.*) (.*):(.*):(.*)', str)
    groups = search.groups()
    print(len(groups))

def test07():
    str =  'http://saibeinews.net/a/guoji/list_1_1.html'
    sub = re.search('\d_([0-9]+?)', str).end(1)
    sub_ = str[0:sub-1]
    i = len(str)
    i_ = str[sub:i]
    print(i_)

def test08():
    url = 'http://fgw.baotou.gov.cn/gzdt2_{}.jhtml'.format('1')
    print(url)

def test09():
    url = 'https://www.btggzyjy.cn/zxdt/20210618/ef8141e1-379a-44ef-b34b-5c8b68183650.html'
    split = url.split('/')
    id = split[len(split)-1].replace('.html', '')
    cookies = {
        'JSESSIONID': '6B9FFA597E4F650E1781442E93E33015',
    }
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.btggzyjy.cn',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.btggzyjy.cn/zxdt/20210618/ef8141e1-379a-44ef-b34b-5c8b68183650.html',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
    }

    params = (
        ('cmd', 'addPageView'),
    )

    data = {
        'viewGuid': 'cms_' + id,
        'siteGuid': '7eb5f7f1-9041-43ad-8e13-8fcb82ea831a'
    }

    response = requests.post('https://www.btggzyjy.cn/EpointWebBuilder/frontAppAction.action', headers=headers, params=params, cookies=cookies, data=data).json()
    if response:
        print(eval(response.get('custom'))['viewCount'])

def test10():
    url = 'http://fgw.chifeng.gov.cn/dtzx?pi=*'
    url_ = url.replace('*', '1')
    print(url_)

def test11():
    i = '1'
    if i==1:
        print(11)

def test12():
    i ='001'
    print(int(i)+1)

def test13():
    str = '"as"d\nas"'
    print(escape_string(str))

def test14():
    str= '1a;sd'
    sp = str.split(';')
    print(type(sp))

def test15():
    import pysolr
    #这个url很重要，不能填错了
    solr = pysolr.Solr('http://139.129.228.177:8983/solr/sd/', timeout=10)
    results = solr.add([
    {
        "id": "22222",
        "title": "A test document",
        }
    ])
    # results = solr.search('*:*')
    rest = solr.delete(id='11111')
    solr.commit()
    print(results)

def test16():
    headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Cookie': '__jsluid_h=48e6e6d68dcc3d40987f678359b47d37; JSESSIONID=EFF73568AF293DD11A2346789CF4D6EC; bdshare_firstime=1620782132682',
            'Host': 'www.baidu.com',
            # 'Referer': '',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        }

    if 'Cookie' in headers.keys():
        headers.pop('Cookie')
    print(headers)

    
def test17():
    text = """
    curl 'http://www.yichun.gov.cn/api-ajax_list-2.html' \  -H 'Connection: keep-alive' \  -H 'Pragma: no-cache' \  -H 'Cache-Control: no-cache' \  -H 'Accept: application/json, text/javascript, */*; q=0.01' \  -H 'DNT: 1' \  -H 'X-Requested-With: XMLHttpRequest' \  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' \  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \  -H 'Origin: http://www.yichun.gov.cn' \  -H 'Referer: http://www.yichun.gov.cn/news-list-zwyw.html' \  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7' \  -H 'Cookie: __jsluid_h=7e70de60a4ad8596bbbd68a721fb9192; UM_distinctid=17a83b09267381-0c9800b8a1feb6-34647600-1aeaa0-17a83b09268ab3; Hm_lvt_60c0cfac04e2e3897021638fc6187a90=1628561807; _ci_session=d8kk2te2rtkmi4p74unpevmer2ljam7e; Hm_lvt_620fa68a327715d031a2ce61b44b47fb=1628561823; Hm_lpvt_620fa68a327715d031a2ce61b44b47fb=1628561823; Hm_lpvt_60c0cfac04e2e3897021638fc6187a90=1628561823' \  --data-raw 'ajax_type%5B%5D=2_news&ajax_type%5B%5D=6023&ajax_type%5B%5D=2&ajax_type%5B%5D=news&ajax_type%5B%5D=Y-m-d&ajax_type%5B%5D=40&ajax_type%5B%5D=15&ajax_type%5B7%5D%5B%5D=displayorder+DESC&ajax_type%5B7%5D%5B%5D=inputtime+DESC&ajax_type%5B7%5D%5B%5D=is_top+DESC&ajax_type%5B8%5D=&is_ds=1' \  --compressed \  --insecure
    """
    text = text.replace('\\', '')
    print(text)

def test18():
    str1 = 'http://www.jgsdaily.com/intview/2020/0219/125690.shtml'
    if "www.jgsdaily.com" in 'http://www.ycda.gov.cn/bwcxljsm/bwcxljsm/201911/t20191114_1849491.html':
        print(1)


if __name__ == '__main__':
    test18()
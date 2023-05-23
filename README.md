# 新闻网数据爬取

* 爬取配置
* 列表解析配置
* start


## 爬取配置

### 1 、 config.ini

```python
[DATABASE]
host = 
port = 
user =
password = 
db_name = 
dbchar = utf8mb4


[CRAWLER]
city_list=1501,1502,1503,1504,1505,1506,1508,1509,1525,3608,3609,3606,4331,1301,2101
#详情去重队列
quchong_detail_queue=xinwen:
#列表去重队列
quchong_list_queue=xinwenlist:
#mysql url队列
mysql_list_queue=xinwen.mysql.com:1111
#列表url队列
list_queue=news.urls:1111
#详情url队列
detail_queue=redis.xinwen.seedQueue.com:1111
solr_url=
#if use proxy ip
useproxyip=false
#proxy ip API address
proxyapi=
crawl_progressnum = 1
redis_host=
redis_port=
redis_pwd=
```
备注：mysql表的设置在 mysqlUtil.py

## 解析配置

### 1 、详情解析配置

```python
city_list：                城市列表
special_title_regex：      特殊的标题-正则
special_title_xpath：      特殊的标题-xpath
special_content_xpath：    特殊的内容-xpath
special_time_regex:        特殊的内容-正则
special_time_xpath:        特殊的内容-xpath
special_author_xpath:      特殊的内容-xpath
special_author_regex:      特殊的内容-正则
cookies:                   Cookie
url_reg_no_contains:       不包含的url（支持正则,以;隔开）
url_reg_contains:          包含的url（支持正则,以;隔开）
spider_depth:              采集深度
```

### 2、列表解析配置

```python
urls：        对应的是spider_depth，按深度采集url
paging：      列表页
```

* 规则：urls：url;url;url;...        (其中第一个url按spider_depth配置的深度采集，之后的url只采集当前页；后续只采集匹配到第一个url的域名的链接)
* 规则：paging: 支持两种配置规则。（如果两种都包含中间用>隔开）

​      1、http://www.ordoszgh.gov.cn/ghdt/ghyw/index_*.html,1,58;

​      2、支持curl配置

      curl 'http://www.jian.gov.cn/api-ajax_list-@.html' \  -H 'Connection: keep-alive' \
      -H 'Accept: application/json, text/javascript, */*; q=0.01' \
      -H 'X-Requested-With: XMLHttpRequest' \
      -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' \
      -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
      -H 'Origin: http://www.jian.gov.cn' \
      -H 'Referer: http://www.jian.gov.cn/news-list-jinrijian.html' \
      -H 'Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7' \
      -H 'Cookie: UM_distinctid=17b047bbb301f5-01e80566dbdeba-2343360-e1000-17b047bbb315ea; Hm_lvt_620fa68a327715d031a2ce61b44b47fb=1628735824; _ci_session=crr0es2q4joeeig73lfgifc9hfpitlm9; Hm_lvt_ef4614aaaaf3a5eac21998c65040de03=1628058260,1628474409,1628734260,1628833500; td_cookie=4286205087; Hm_lpvt_ef4614aaaaf3a5eac21998c65040de03=1628833937' \
      --data-raw 'ajax_type%5B%5D=21_news&ajax_type%5B%5D=12&ajax_type%5B%5D=21&ajax_type%5B%5D=news&ajax_type%5B%5D=Y-m-d&ajax_type%5B%5D=40&ajax_type%5B%5D=20&ajax_type%5B%5D=0&ajax_type%5B8%5D=&is_ds=1' \
      --compressed \
      --insecure!1!421>

​	3、不包含的url（采用正则搜索）

​			用;隔开 

## Start

### 1、修改

xinwenSite/Config.ini

### 2、启动采集

```python
sh start.sh
```

**支持两个命令:** 

s: 启动采集

k: 停止采集



**启动顺序：**

url_to_redis.py

main.py

xwSiteUrlToRedis.py

xinwenSearch.py

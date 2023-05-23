# -*- coding: utf-8 -*-
# @Time    : 4/9/21 4:39 PM
# @Author  : wangjie
import init
import os
import traceback


from worker.extractor.article_extractor import ArticleExtractor
from ulogger import setLogger
from flask import Flask, request


app = Flask(__name__)

log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"run")


'''
    获取详情
'''
@app.route('/get/html', methods=["GET"])
def get_html():
    try:
        url = request.args.get('url')
        special_title_regex = request.args.get('special_title_regex','')
        special_title_xpath = request.args.get('special_title_xpath','')
        special_content_xpath = request.args.get('special_content_xpath','')
        special_time_regex = request.args.get('special_time_regex','')
        special_time_xpath = request.args.get('special_time_xpath','')
        special_author_xpath = request.args.get('special_author_xpath','')
        special_author_regex = request.args.get('special_author_regex','')
        cookies = request.args.get('cookies','')
        return ArticleExtractor.get_html(url, special_title_regex, special_title_xpath, special_content_xpath, special_time_regex, special_time_xpath,special_author_xpath, special_author_regex,cookies)
    except Exception:
        return traceback.format_exc()


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port='1721')

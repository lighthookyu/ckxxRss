# -*- coding: utf-8 -*-
import requests
import PyRSS2Gen
from lxml import html
from flask import Flask, request, send_from_directory
import datetime

app = Flask(__name__)


def get_detail(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        }
        resp = requests.get(url, headers=headers)
        resp = requests.get(url, headers=headers)   # 真的要两次是吧
        selectors = html.fromstring(resp.text)
        paragraphs = selectors.xpath('//div[@class="articleTextAll hide"]')
        detail, postTime = '', ''
        # 只有一页的网页采取这个逻辑
        if len(paragraphs) != 0:
            detail = html.tostring(paragraphs[0],
                                   encoding="utf-8",
                                   pretty_print=True,
                                   method="html").decode("utf-8")
            postTime = selectors.xpath('//span[@id="pubtime_baidu"]/text()')[0]
        else:  # 翻页的网页采取这个逻辑
            pages = len(selectors.xpath('//ul[@class="pageUl"]/li')) - 2  # 减去翻页按钮

            # 第一页
            paragraphs = selectors.xpath('//div[@class="articleText"]')
            detail = html.tostring(paragraphs[0],
                                   encoding="utf-8",
                                   pretty_print=True,
                                   method="html").decode("utf-8")
            postTime = selectors.xpath('//span[@id="pubtime_baidu"]/text()')[0]

            # 第二页开始循环爬取
            i = 2
            url_id = url[:-6]
            while i <= pages:
                url = '{}_{}.shtml'.format(url_id, i)
                resp = requests.get(url, headers=headers)
                resp = requests.get(url, headers=headers)
                selectors = html.fromstring(resp.text)
                paragraphs = selectors.xpath('//div[@class="articleText"]')
                detail = detail + html.tostring(paragraphs[0],
                                                encoding="utf-8",
                                                pretty_print=True,
                                                method="html").decode("utf-8")
                i += 1

        return detail, postTime
    except Exception as e:
        print('detail err: {}'.format(e))


def get_ckxx(block):
    url = 'http://www.cankaoxiaoxi.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
    }
    resp = requests.get(url, headers=headers)
    resp = requests.get(url, headers=headers)
    selectors = html.fromstring(resp.text)
    newsTitle = {
        'yaowen': selectors.xpath('//ul[@class="yaowen-list"]/li/a/text()'),  # 要闻
        'zhongguo': selectors.xpath('//ul[@class="list-block"]/li/a/text()')[:11],  # 中国
        'guancha': selectors.xpath('//ul[@class="list-block"]/li/a/text()')[11:17],  # 观察中国
        'guoji': selectors.xpath('//ul[@class="list-block"]/li/a/text()')[17:29],  # 国际
        'luntan': selectors.xpath('//ul[@class="list-block"]/li/a/text()')[29:34],  # 论坛
        'junshi': selectors.xpath('//ul[@class="list-block"]/li/a/text()')[34:44],  # 军事
        'jingji': selectors.xpath('//ul[@class="list-block"]/li/a/text()')[54:64],  # 经济
        'zhiku': selectors.xpath('//ul[@class="list-block"]/li/a/text()')[72:82],  # 智库
    }
    newsHref = {
        'yaowen': selectors.xpath('//ul[@class="yaowen-list"]/li/a/@href'),  # 要闻
        'zhongguo': selectors.xpath('//ul[@class="list-block"]/li/a/@href')[:11],  # 中国
        'guancha': selectors.xpath('//ul[@class="list-block"]/li/a/@href')[11:17],  # 观察中国
        'guoji': selectors.xpath('//ul[@class="list-block"]/li/a/@href')[17:29],  # 国际
        'luntan': selectors.xpath('//ul[@class="list-block"]/li/a/@href')[29:34],  # 论坛
        'junshi': selectors.xpath('//ul[@class="list-block"]/li/a/@href')[34:44],  # 军事
        'jingji': selectors.xpath('//ul[@class="list-block"]/li/a/@href')[54:64],  # 经济
        'zhiku': selectors.xpath('//ul[@class="list-block"]/li/a/@href')[72:82],  # 智库
    }
    kv = {
        'yaowen': '要闻',
        'zhongguo': '中国',
        'guancha': '观察中国',
        'guoji': '国际',
        'luntan': '论坛',
        'junshi': '军事',
        'jingji': '经济',
        'zhiku': '智库',
    }
    try:
        respInfo = []
        i = 0
        while i < len(newsTitle[block]):
            detail, pubTime = get_detail(newsHref[block][i])
            respInfo.append(
                PyRSS2Gen.RSSItem(
                    title=newsTitle[block][i],
                    link=newsHref[block][i],
                    guid=newsTitle[block][i],
                    description=detail,
                    pubDate=pubTime,
                )
            )
            i += 1
        rss = PyRSS2Gen.RSS2(
            title='CKXX FEED-{}'.format(kv[block]),
            link='lighthook.xyz/feed/ckxx',
            description='ckxx infomation',
            lastBuildDate=datetime.datetime.now(),
            items=respInfo,
        )
        rss.write_xml(open("/tmp/a.xml", "w", encoding='utf-8'))
        return True
    except IndexError:
        return None
    except Exception as err:
        print(err)
        return None


@app.route('/get', methods=['GET'])
def rss_main():
    block = request.args.get('block')
    if get_ckxx(block) is not None:
        try:
            return send_from_directory('/tmp', 'a.xml')
        except Exception as e:
            return str(e)


if __name__ == '__main__':
    app.debug = True
    app.config['JSON_AS_ASCII'] = False
    app.run(host="0.0.0.0", port=9000, threaded=True)
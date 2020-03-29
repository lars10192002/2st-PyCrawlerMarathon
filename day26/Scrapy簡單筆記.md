1. 安裝scrapy
```
conda install scrapy
```

2. 建立一個符合scrapy框架結構的叫myproject的專案
```
scrapy startproject myproject
```

3. 透過命令列列來來產⽣生出⼀一個符合框架的爬蟲類別scrapy genspider [爬蟲名稱] [爬蟲⽬目標網址] 
- cd myproject 後下cmd
```
scrapy genspider PTTCrawler www.ptt.cc
```
會在/spider 下 新增一個PTTCrawler.py

```py

# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pprint import pprint
#scrapy.Spider => 爬蟲 ID，在整個 project 中必須要是唯⼀一值
# 範例目標網址: https://www.ptt.cc/bbs/Gossiping/M.1557928779.A.0C1.html
class PttcrawlerSpider(scrapy.Spider):
    name = 'PTTCrawler'
    allowed_domains = ['www.ptt.cc']
    start_urls = ['https://www.ptt.cc/bbs/NSwitch/M.1585368504.A.25A.html']
    cookies = {'over18': '1'} # 過濾成年人的cookies

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        # 假設網頁回應不是 200 OK 的話, 我們視為傳送請求失敗
        if response.status != 200:
            print('Error - {} is not available to access'.format(response.url))
            return

        # 將網頁回應的 HTML 傳入 BeautifulSoup 解析器, 方便我們根據標籤 (tag) 資訊去過濾尋找
        soup = BeautifulSoup(response.text)

        
        # 取得文章內容主體
        main_content = soup.find(id='main-content')
        
        # 假如文章有屬性資料 (meta), 我們在從屬性的區塊中爬出作者 (author), 文章標題 (title), 發文日期 (date)
        metas = main_content.select('div.article-metaline')
        author = ''
        title = ''
        date = ''
        if metas:
            if metas[0].select('span.article-meta-value')[0]:
                author = metas[0].select('span.article-meta-value')[0].string
            if metas[1].select('span.article-meta-value')[0]:
                title = metas[1].select('span.article-meta-value')[0].string
            if metas[2].select('span.article-meta-value')[0]:
                date = metas[2].select('span.article-meta-value')[0].string

            # 從 main_content 中移除 meta 資訊（author, title, date 與其他看板資訊）
            #
            # .extract() 方法可以參考官方文件
            #  - https://www.crummy.com/software/BeautifulSoup/bs4/doc/#extract
            for m in metas:
                m.extract()
            for m in main_content.select('div.article-metaline-right'):
                m.extract()
        
        # 取得留言區主體
        pushes = main_content.find_all('div', class_='push')
        for p in pushes:
            p.extract()
        
        # 假如文章中有包含「※ 發信站: 批踢踢實業坊(ptt.cc), 來自: xxx.xxx.xxx.xxx」的樣式
        # 透過 regular expression 取得 IP
        # 因為字串中包含特殊符號跟中文, 這邊建議使用 unicode 的型式 u'...'
        try:
            ip = main_content.find(text=re.compile(u'※ 發信站:'))
            ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
        except Exception as e:
            ip = ''
        
        # 移除文章主體中 '※ 發信站:', '◆ From:', 空行及多餘空白 (※ = u'\u203b', ◆ = u'\u25c6')
        # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
        #
        # 透過 .stripped_strings 的方式可以快速移除多餘空白並取出文字, 可參考官方文件 
        #  - https://www.crummy.com/software/BeautifulSoup/bs4/doc/#strings-and-stripped-strings
        filtered = []
        for v in main_content.stripped_strings:
            # 假如字串開頭不是特殊符號或是以 '--' 開頭的, 我們都保留其文字
            if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--']:
                filtered.append(v)

        # 定義一些特殊符號與全形符號的過濾器
        expr = re.compile(u'[^一-龥。；，：“”（）、？《》\s\w:/-_.?~%()]')
        for i in range(len(filtered)):
            filtered[i] = re.sub(expr, '', filtered[i])
        
        # 移除空白字串, 組合過濾後的文字即為文章本文 (content)
        filtered = [i for i in filtered if i]
        content = ' '.join(filtered)
        
        # 處理留言區
        # p 計算推文數量
        # b 計算噓文數量
        # n 計算箭頭數量
        p, b, n = 0, 0, 0
        messages = []
        for push in pushes:
            # 假如留言段落沒有 push-tag 就跳過
            if not push.find('span', 'push-tag'):
                continue
            
            # 過濾額外空白與換行符號
            # push_tag 判斷是推文, 箭頭還是噓文
            # push_userid 判斷留言的人是誰
            # push_content 判斷留言內容
            # push_ipdatetime 判斷留言日期時間
            push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
            push_userid = push.find('span', 'push-userid').string.strip(' \t\n\r')
            push_content = push.find('span', 'push-content').strings
            push_content = ' '.join(push_content)[1:].strip(' \t\n\r')
            push_ipdatetime = push.find('span', 'push-ipdatetime').string.strip(' \t\n\r')

            # 整理打包留言的資訊, 並統計推噓文數量
            messages.append({
                'push_tag': push_tag,
                'push_userid': push_userid,
                'push_content': push_content,
                'push_ipdatetime': push_ipdatetime})
            if push_tag == u'推':
                p += 1
            elif push_tag == u'噓':
                b += 1
            else:
                n += 1
        
        # 統計推噓文
        # count 為推噓文相抵看這篇文章推文還是噓文比較多
        # all 為總共留言數量 
        message_count = {'all': p+b+n, 'count': p-b, 'push': p, 'boo': b, 'neutral': n}
        
        # 整理文章資訊
        data = {
            'url': response.url,
            'article_author': author,
            'article_title': title,
            'article_date': date,
            'article_content': content,
            'ip': ip,
            'message_count': message_count,
            'messages': messages
        }
        yield data


```
4.執行 scrapy crawl PTTCrawler 開始抓取資料

```
scrapy crawl PTTCrawler
```


XPath + Item Pipeline
5.透過 Item 設定爬完的文章資訊資料格式
- 透過 Item Pipeline 設定爬文存成 JSON 的流程

```py
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PTTArticleItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    article_id = scrapy.Field()
    article_author = scrapy.Field()
    article_title = scrapy.Field()
    article_date = scrapy.Field()
    article_content = scrapy.Field()
    ip = scrapy.Field()
    message_count = scrapy.Field()
    message = scrapy.Field()
    

```
6. 修改部分PTTCrawler.py
- 原本整理文章的dict,改用PTTArticleItem處理

```py
# 整理文章資訊
        data = PTTArticleItem()
        article_id = str(Path(urlparse(response.url).path).stem)
        data['url'] = response.url
        data['article_id'] = article_id
        data['article_author'] = author
        data['article_title'] = title
        data['article_date'] = date
        data['article_content'] = content
        data['ip'] = ip
        data['message_count'] = message_count
        data['messages'] = messages
        yield data
```

7.新增main.py CrawlerProcess 就會建立爬蟲流程 

```py
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    target_urls = {
        # 'https://www.ptt.cc/bbs/NSwitch/M.1585473903.A.F30.html',
        'https://www.ptt.cc/bbs/NSwitch/M.1585368504.A.25A.html'
    }
    process = CrawlerProcess(get_project_settings())
    process.crawl('PTTCrawler', start_urls = target_urls, filename = 'test.json')
    process.start()

if __name__ == "__main__":
    main()
```

8.修改PttcrawlerSpider

```py
class PttcrawlerSpider(scrapy.Spider):
    name = 'PTTCrawler'
    def __init__(self, start_urls, filename=None):
        self.cookies = {'over18': '1'}
        self.start_urls = start_urls
        self.filename = filename
        super().__init__()

```

9.自訂JSONPipeline
```py

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import json

from pathlib import Path
from datetime import datetime

class MyprojectPipeline(object):
    def process_item(self, item, spider):
        return item

class JSONPipeline(object):
    def open_spider(self, spider):
        self.start_crawl_datetime = datetime.now().strftime('%Y%m%dT%H:%M:%S')

        # 在開始爬蟲的時候建立暫時的 JSON 檔案
        # 避免有多筆爬蟲結果的時候，途中發生錯誤導致程式停止會遺失所有檔案
        self.dir_path = Path(__file__).resolve().parents[1] / 'crawled_data'
        self.runtime_file_path = str(self.dir_path / '.tmp.json.swp')
        if not self.dir_path.exists():
            self.dir_path.mkdir(parents=True)
        spider.log('Create temp file for store JSON - {}'.format(self.runtime_file_path))

        # 設計 JSON 存的格式為
        # [
        #  {...}, # 一筆爬蟲結果
        #  {...}, ...
        # ]
        self.runtime_file = open(self.runtime_file_path, 'w+', encoding='utf8')
        self.runtime_file.write('[\n')
        self._first_item = True

    def process_item(self, item, spider):
        # 把資料轉成字典格式並寫入文件中
        if not isinstance(item, dict):
            item = dict(item)

        if self._first_item:
            self._first_item = False
        else:
            self.runtime_file.write(',\n')

        self.runtime_file.write(json.dumps(item, ensure_ascii=False))
        return item

    def close_spider(self, spider):
        self.end_crawl_datetime = datetime.now().strftime('%Y%m%dT%H:%M:%S')

        # 儲存 JSON 格式
        self.runtime_file.write('\n]')
        self.runtime_file.close()
        
        # 將暫存檔改為以日期為檔名的格式
        self.store_file_path = self.dir_path / '{}-{}.json'.format(self.start_crawl_datetime,
                                                                   self.end_crawl_datetime)
        # 假如 PTT 爬蟲有給定存檔檔名，就使用給予的檔名
        if spider.name == 'PTTCrawler' and spider.filename:
            if Path(spider.filename).suffix == '.json':
                self.store_file_path = self.dir_path / spider.filename
            else:
                self.store_file_path = self.dir_path / '{}.json'.format(spider.filename)

        self.store_file_path = str(self.store_file_path)
        os.rename(self.runtime_file_path, self.store_file_path)
        spider.log('Save result at {}'.format(self.store_file_path))

```
# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pprint import pprint

# url = https://www.ptt.cc/bbs/NSwitch/M.1585368504.A.25A.html
class PttcrawlerSpider(scrapy.Spider):
    name = 'PTTCrawler'
    allowed_domains = ['www.ptt.cc']
    start_urls = ['https://www.ptt.cc/bbs/NSwitch/M.1585368504.A.25A.html']
    cookies = {'over18':'1'}
    print("----------------------- start ------------------------")
    def start_request(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        print("---------------> parse")
        
        #check status must be 200 , if not ack error
        if response.status!= 200:
            print('Error - {} '.format(response.url))
            return

        #start parse use BeautifulSoup 
        soup = BeautifulSoup(response.text)
        
        #get article content
        main_content = soup.find(id='main-content')

        metas = main_content.select('div.article-metaline')
        author = ''
        title = ''
        date = ''
        if metas:
            if metas[0].select('span.article-meta-value'[0]):
                author = metas[0].select('span.article-meta-value'[0]).string
            if metas[1].select('span.article-meta-value'[0]):
                title = metas[1].select('span.article-meta-value'[0]).string
            if metas[2].select('span.article-meta-value'[0]):
                date = metas[2].select('span.article-meta-value'[0]).string
                print('=========> ',date)

            for m in metas:
                m.extract()
            for m in main_content.select('div.article-metaline-right'):
                m.extract()


        pushes = main_content.find_all('div', class_='push')
        for p in pushes:
            p.extract()

        try:
            ip = main_content.find(text=re.compile(u'※ 發信站:'))
            ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
        except Exception as e:
            ip = ''

        filtered = []
        for v in main_content.stripped_strings:
            if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--']:
                filtered.append(v)

        expr = re.compile(u'[^一-龥。；，：“”（）、？《》\s\w:/-_.?~%()]')
        for i in range(len(filtered)):
            filtered[i] = re.sub(expr, '', filtered[i])

        filtered = [i for i in filtered if i]
        content = ' '.join(filtered)

        p, b, n = 0, 0, 0
        messages = []
        for push in pushes:
            if not push.find('span', 'push-tag'):
                continue
            
            push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
            push_userid = push.find('span', 'push-userid').string.strip(' \t\n\r')
            push_content = push.find('span', 'push-content').strings
            push_content = ' '.join(push_content)[1:].strip(' \t\n\r')
            push_ipdatetime = push.find('span', 'push-ipdatetime').string.strip(' \t\n\r')

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
        
        message_count = {'all': p+b+n, 'count': p-b, 'push': p, 'boo': b, 'neutral': n}
        
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
        print(type(data))
        yield data
        
        



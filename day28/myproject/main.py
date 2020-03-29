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
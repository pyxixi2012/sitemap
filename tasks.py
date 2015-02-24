from app import celery, app, db, models
from spider import SitemapSpider
import datetime
import scrapy
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
import os


@celery.task(name='tasks.crawl_domains', bind=True)
def crawl_domains(self, sitemap):
    db.session.add(sitemap)

    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapy_settings'
    os.putenv('SCRAPY_SETTINGS_MODULE', 'scrapy_settings')

    # Setup the spider
    spider = SitemapSpider(sitemap.get_domains())
    spider.sitemap_id = sitemap.id
    crawler = Crawler(get_project_settings())
    crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(spider)

    # Update the sitemap
    sitemap.crawl_started = datetime.datetime.now()
    sitemap.task_id = self.request.id
    sitemap.crawl_status = 'started'
    db.session.commit()

    # Run the crawler
    try:
        crawler.start()
        scrapy.log.start()
        reactor.run()
    except Exception as e:
        sitemap.crawl_status = 'server_error'
        sitemap.crawl_ended = datetime.datetime.now()
        db.session.commit()
        return
    finally:
        try:
            reactor.stop()
        except: pass

    # It is finished, store the results
    sitemap.crawl_status = spider.reason
    if spider.sitemap is not None:
        sitemap.sitemap = unicode(spider.sitemap)
    sitemap.crawl_ended = datetime.datetime.now()
    db.session.commit()

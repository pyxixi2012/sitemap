from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.utils.url import url_is_from_any_domain
from scrapy import log
from scrapy.exceptions import CloseSpider
from lxml import etree
import settings
from app import db, models


class ExceptionMiddleware(object):
    def process_exception(self, request, exception, spider):
        se = models.SitemapError(spider.sitemap_id, "%s.%s" % (exception.__class__.__module__, exception.__class__.__name__), str(exception))
        db.session.add(se)
        db.session.commit()

class SitemapSpider(CrawlSpider):
    """
        Scanpy spider that will crawl an entire site to find all URLs
    """
    name = 'sitemapspider'
    scraped_urls = set()

    def __init__(self, domains, limit=settings.PAGE_LIMIT, *args, **kwargs):
        self.allowed_domains = domains + ['www.%s' % (d,) for d in domains]
        self.start_urls = ['http://%s' % (d,) for d in domains]
        self.limit = limit

        self.rules = (
            Rule(LinkExtractor(allow=('.*',), allow_domains=self.allowed_domains, unique=True, canonicalize=True), callback='parse_item', follow=True),
        )

        super(SitemapSpider, self).__init__(*args, **kwargs)

    def parse_start_url(self, response):
        self.parse_item(response)

    def parse_item(self, response):
        # Don't log redirects
        if response.status >= 300 and response.status < 400:
            return None

        if not url_is_from_any_domain(response.url, self.allowed_domains):
            return None

        self.scraped_urls.add(response.url.rstrip('/'))

        l = len(self.scraped_urls)
        if l % 100 == 0:
            self.log("%s URLs scraped" % (l,), level=log.INFO)
        if l >= self.limit:
            raise CloseSpider('page_limit')

    def closed(self, reason):
        self.reason = reason
        if reason == 'finished' or reason == 'page_limit':
            # Generate the sitemap
            urlset = etree.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

            for u in self.scraped_urls:
                url = etree.Element('url')
                loc = etree.Element('loc')
                loc.text = u
                url.append(loc)
                urlset.append(url)

            self.sitemap = etree.tostring(urlset, encoding="UTF-8", xml_declaration=True)

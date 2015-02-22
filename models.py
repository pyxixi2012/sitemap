from app import db
import json
import datetime
import xml.dom.minidom as minidom


class Sitemap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domains = db.Column(db.UnicodeText(), nullable=False)
    date_started = db.Column(db.DateTime)
    ip = db.Column(db.String(15), nullable=False)
    task_id = db.Column(db.String(255), nullable=True)
    crawl_started = db.Column(db.DateTime, nullable=True)
    crawl_ended = db.Column(db.DateTime, nullable=True)
    crawl_status = db.Column(db.String(256), nullable=False)
    sitemap = db.Column(db.UnicodeText(2**31), nullable=True)

    def __init__(self, domains, ip):
        self.domains = json.dumps(domains)
        self.date_started = datetime.datetime.now()
        self.ip = ip
        self.crawl_status = 'pending'

    def get_domains(self):
        return json.loads(self.domains)
        
    def get_json(self):
        o = {}
        o['id'] = self.id
        o['domains'] = self.get_domains()
        o['started'] = str(self.date_started)
        o['status'] = self.crawl_status

        if self.crawl_started is not None:
            o['crawl_started'] = str(self.crawl_started)
        if self.crawl_ended is not None:
            o['crawl_ended'] = str(self.crawl_ended)

        return o

    def get_sitemap(self):
        if self.crawl_ended is None or self.sitemap is None:
            return None

        xml = minidom.parseString(self.sitemap)
        return xml.toprettyxml()

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
    sitemap = db.Column(db.UnicodeText, nullable=True)
    errors = db.relationship('SitemapError', backref='sitemap', lazy='dynamic')

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

        if self.errors.count() > 0:
            o['status'] = 'error'

        if self.crawl_started is not None:
            o['crawl_started'] = str(self.crawl_started)
        if self.crawl_ended is not None:
            o['crawl_ended'] = str(self.crawl_ended)

        o['errors'] = []
        for e in self.errors:
            o['errors'].append(e.get_json())

        return o

    def get_sitemap(self):
        if self.crawl_ended is None or self.sitemap is None or self.errors.count() > 0:
            return None

        xml = minidom.parseString(self.sitemap)
        return xml.toprettyxml()

class SitemapError(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sitemap_id = db.Column(db.Integer, db.ForeignKey('sitemap.id'))
    error_name = db.Column(db.UnicodeText, nullable=False)
    error_details = db.Column(db.UnicodeText, nullable=True)

    def __init__(self, sitemap_id, error, details=None):
        self.sitemap_id = sitemap_id
        self.error_name = error
        self.error_details = details

    def get_json(self):
        return {'name': self.error_name, 'details': self.error_details}
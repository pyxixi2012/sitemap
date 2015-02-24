DOWNLOADER_MIDDLEWARES = {
  'spider.ExceptionMiddleware': 450,
}

EXTENSIONS = {
  "scrapy_sentry.extensions.Errors":10,
}

# Local overrides
try:
  from local_scrapy_settings import *
except ImportError: pass
DOWNLOADER_MIDDLEWARES = {
  'spider.ExceptionMiddleware': 450,
}

EXTENSIONS = {}

# Local overrides
try:
  from local_scrapy_settings import *
except ImportError: pass

try:
  if SENTRY_DSN is not None:
    EXTENSIONS['scrapy_sentry.extensions.Errors'] = 10
except KeyError: pass
except NameError: pass
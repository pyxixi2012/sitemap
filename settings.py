import scrapy
import os


# Database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', os.getenv('DATABASE_URL', 'sqlite://'))

# Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_RESULT_BACKEND = "db+%s" % (SQLALCHEMY_DATABASE_URI,)
CELERYD_MAX_TASKS_PER_CHILD = 1

# Scrapy
LOG_LEVEL=scrapy.log.DEBUG
DEPTH_PRIORITY=1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

# Sitemap-specific settings
PAGE_LIMIT = 1000

SENTRY_DSN = os.getenv('SENTRY_DSN', None)

# Any settings specified in local_settings.py should override these defaults
try:
    from local_settings import *
except ImportError: pass

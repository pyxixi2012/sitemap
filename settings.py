import scrapy
import os


# Database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite://')

# Redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PREFIX = 'sitemap::'

# Celery
CELERY_BROKER_URL = 'redis://%s:%s' % (REDIS_HOST, REDIS_PORT)
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

# Any settings specified in local_settings.py should override these defaults
try:
    from local_settings import *
except ImportError: pass

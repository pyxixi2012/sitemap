from flask import Flask, request
from celery import Celery
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
import logging


app = Flask(__name__)
app.config.from_object('settings')

@app.before_request
def _cache_data():
  request.get_data()

try:
  if app.config['SENTRY_DSN'] is not None:
    sentry = Sentry(app, level=logging.ERROR, wrap_wsgi=True)
except KeyError: pass

# Setup database
db = SQLAlchemy(app)

# Setup task queue
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

TaskBase = celery.Task
class ContextTask(TaskBase):
    abstract = True
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)
celery.Task = ContextTask

import scrapy_settings
import models
import tasks

from views import *

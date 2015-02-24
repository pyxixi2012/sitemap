from flask import Flask
from celery import Celery
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry


app = Flask(__name__)
app.config.from_object('settings')

sentry = Sentry(app)

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

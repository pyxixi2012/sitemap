# sitemap

This is a XML sitemap generator written using Flask, Scrapy, and Celery. You can view it in action at http://p.jacobparry.ca/sitemap/

To run it on your own, you'll need to enlist the help of `supervisord` or something similar to keep the Celery workers
running in the background. An example configuration file for `supervisord` is shown below.

```
[program:sitemap-celery]
command=/path/to/venv/bin/celery -A app.celery worker --loglevel=INFO
directory=/path/to/program
user=www-data
numprocs=1
stdout_logfile=/var/log/sitemap.log
stderr_logfile=/var/log/sitemap.log
startsecs=10
stopwaitsecs=600
killasgroup=true
```

You'll also need to keep the Flask application running in the usual way, such as using `mod_wsgi` or `uWSGI`.

All default settings can be overriden in a `local_settings.py` file. I'd suggest changing `SQLALCHEMY_DATABASE_URI` to
be accurate for your setup. You'll also want to look in `settings.py` when you change things, since any setting that
depends on a changed value will also need to be set. For example, if you change `REDIS_HOST` you'll also need to change
`CELERY_BROKER_URL`.

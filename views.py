from app import app, db, models, tasks, sentry
from flask import request, render_template, abort, jsonify, make_response
import json
import settings
import urlparse


@app.route('/')
def index():
    dsn = settings.SENTRY_DSN

    if dsn is not None:
        up = urlparse.urlparse(dsn)
        dsn = "%s://%s@%s%s%s" % (up.scheme, up.username, up.hostname, ":%s" % (up.port,) if up.port > 0 else '', up.path)

    return render_template('index.html', dsn=dsn)

def clean_domain(domain):
    domain = domain.replace('http://', '').replace('https://', '').rstrip('/')
    if domain.startswith('www.'):
        domain = domain[4:]

    if '/' in domain:
        return None

    if not '.' in domain:
        return None

    return domain

@app.route('/api/start', methods=['POST'])
def api_start():
    data = request.get_json(force=True)
    if not 'domains' in data:
        return abort(400)
    domains = data['domains']

    # Sanitize the domains
    nd = set()
    for d in domains:
        d = clean_domain(d)
        if d is not None:
            nd.add(d)

    if len(nd) <= 0:
        return abort(400)

    nd = list(nd)

    sm = models.Sitemap(nd, request.remote_addr)
    db.session.add(sm)
    db.session.commit()

    task = tasks.crawl_domains.delay(sm)

    return json.dumps(sm.get_json()), 201

@app.route('/api/status', methods=['POST'])
def api_status():
    data = request.get_json(force=True)
    if not 'task_ids' in data:
        return abort(400)

    task_ids = [int(i) for i in data['task_ids']]

    tasks = []
    for id in task_ids:
        tasks.append(models.Sitemap.query.get(id))

    return json.dumps([ sm.get_json() for sm in tasks ])

@app.route('/api/history', methods=['GET'])
def api_history():
    tasks = models.Sitemap.query.filter_by(ip=request.remote_addr).order_by(models.Sitemap.id.desc()).limit(20).all()
    return json.dumps([ s.get_json() for s in reversed(tasks) ])

@app.route('/download/<int:task_id>')
def download(task_id):
    sitemap = models.Sitemap.query.get_or_404(task_id)

    xml = sitemap.get_sitemap()
    if xml is None:
        return abort(404)

    resp = make_response(sitemap.get_sitemap())
    resp.headers["Content-Disposition"] = "attachment; filename=sitemap.xml"
    return resp

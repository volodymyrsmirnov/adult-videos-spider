#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Spiders management interface
"""

from requests.auth import HTTPBasicAuth
import requests
import anyjson

from flask import *
from functools import wraps

manager = Blueprint('manager', __name__, template_folder='templates')

import ConfigParser
config = ConfigParser.ConfigParser()
config.read("masturbators/scrapy.cfg")

def check_auth(username, password):
	return username == current_app.config["MANAGER_USER"] and password == current_app.config["MANAGER_PASSWORD"]

def authenticate():
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return f(*args, **kwargs)
	return decorated

def call_scrapyd_api(method, data={}, post=False):
	endpoint = "{0}{1}.json".format(config.get("deploy", "url"), method)
	auth = HTTPBasicAuth(config.get("deploy", "username"), config.get("deploy", "password"))

	if post:
		r = requests.post(endpoint, data=data, auth=auth)
	else:
		r = requests.get(endpoint, params=data, auth=auth)

	if not r.status_code == requests.codes.ok:
		return None

	print r.text

	return anyjson.loads(r.text)

@manager.route("/")
@requires_auth
def panel():
	spiders = call_scrapyd_api("listspiders", data={"project": config.get("deploy", "default_project")})
	jobs = call_scrapyd_api("listjobs", data={"project": config.get("deploy", "default_project")}) 

	url = "http://{0}:{1}@{2}".format(config.get("deploy", "username"), config.get("deploy", "password"), config.get("deploy", "url").replace("http://", ""))

	return render_template(
		"manager/panel.html",
		spiders=spiders,
		jobs=jobs,
		url=url
	)

@manager.route("/run/<spidername>/")
def run_spider(spidername):
	call_scrapyd_api("schedule", data={"project": config.get("deploy", "default_project"), "spider":spidername}, post=True)
	return redirect(url_for(".panel"))

@manager.route("/finish/<jobid>/")
def finish_job(jobid):
	call_scrapyd_api("cancel", data={"project": config.get("deploy", "default_project"), "job":jobid}, post=True)
	return redirect(url_for(".panel"))


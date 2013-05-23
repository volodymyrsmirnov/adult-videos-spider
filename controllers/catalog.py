#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Catalog main view controller
"""
from flask import *

catalog = Blueprint('catalog', __name__, template_folder='templates')

from models import *
from application import cache, app
from flask.ext.babel import refresh as language_refresh

@catalog.url_defaults
def add_language_code(endpoint, values):
	"""
	Set default value for lang_code url segment
	"""
	try:
		values.setdefault('lang_code', g.lang_code)
	except: pass

@catalog.url_value_preprocessor
def pull_lang_code(endpoint, values):
	"""
	Pull lang_code value from the list of request parameters
	"""
	g.lang_code = values.pop('lang_code')

	if not g.lang_code in app.config.get("LANGUAGES"):
		return abort(404)	

	language_refresh()

@cache.cached(timeout=60)
def get_list_of_tags():
	return db.session.query(
		VideoTag, 
		db.func.count(video_tags.c.video_id).label('total'),
		db.func.sum(Video.views).label('views'),
	).join(video_tags, Video).group_by(VideoTag).order_by('views DESC, total DESC').first()

@catalog.route("/")
def index():
	return render_template("catalog/index.html", tags=get_list_of_tags())

@catalog.route("/tag/<int:id>/<slug>/")
@catalog.route("/tag/<int:id>/<slug>/<int:page>/")
def tag(id, slug, page=0):
	pass

@catalog.route("/video/<int:id>/<slug>.html")
def video(id, slug):
	pass

@catalog.route("/page/<slug>.html")
def page(slug):
	pass
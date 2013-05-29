#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Catalog main view controller
"""
import math
import datetime

from flask import *

from slugify import slugify

catalog = Blueprint('catalog', __name__, template_folder='templates')

from models import *
from forms import ContactForm, contact_topics
from application import cache, app, mail, redis
from flask.ext.babel import gettext
from flask.ext.babel import refresh as language_refresh
from flask.ext.mail import Message

from translate import Translator

def translate_video_title(what):
	to_language = g.lang_code

	if to_language == "en":
		return what

	key = "{0}_{1}".format(what, to_language)

	translation = redis.get(key)

	if translation:
		return translation

	translator = Translator(to_lang=to_language)
	
	try:
		translation = translator.translate(what)
		redis.set(key, translation)
	except:
		translation = what

	return translation

@catalog.context_processor
def context_processor():
	return dict(
		translate_video_title=translate_video_title,
	)

@catalog.url_defaults
def add_language_code(endpoint, values):
	"""
	Set default value for lang_code url segment
	"""
	try: values.setdefault('lang_code', g.lang_code)
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

@cache.cached(timeout=3600)
def get_list_of_tags():
	return db.session.query(
			VideoTag, 
			db.func.count(video_tags.c.video_id).label('total'),
			db.func.sum(Video.views).label('views'),
	).join(video_tags, Video).group_by(VideoTag).order_by('views DESC, total DESC').all()

@catalog.route("/")
def index():
	return render_template (
		"catalog/index.html", 
		tags=get_list_of_tags(), 
	)

@catalog.route("/sitemaps/all.xml")
@catalog.route("/sitemaps/<int:id>.xml")
@cache.cached(timeout=86400)
def sitemap(id=None):
	items_count = Video.query.count()
	sitemaps_count = math.ceil(items_count / 10000.0)

	if id == None:
		response = render_template(
			"catalog/sitemap_index.xml", 
			sitemaps_count=sitemaps_count,
			now=datetime.datetime.now()
		)

		return Response(response, mimetype='text/xml')
	elif id in range(0, int(sitemaps_count)):
		videos = db.session.query(Video.id, Video.title, Video.import_date).order_by(db.asc(Video.import_date)).offset(id * 10000).limit(10000).all()

		response = render_template(
			"catalog/sitemap.xml", 
			videos=videos,
			slugify=slugify
		)

		return Response(response, mimetype='text/xml')
	else:
		return abort(404)

@catalog.route("/search/", methods=["GET", "POST"])
@catalog.route("/search/<what>/")
@catalog.route("/search/<what>/page/<int:page>/")
def search(what=None, page=1):
	if request.method == "POST" and "search_term" in request.values:
		return redirect(url_for("catalog.search", what=request.values["search_term"], _method="GET"))

	if len(what) not in range(4, 32):
		return abort(404)

	search_ilike = "%{0}%".format(what)

	page = Video.query.filter(
		(Video.title.ilike(search_ilike)) |
		(Video.tags.any(VideoTag.name.ilike(search_ilike))) |
		(Video.stars.any(VideoStar.name.ilike(search_ilike)))
	).order_by(Video.import_date).paginate(page=page, per_page=40)

	description = gettext("Search %(title)s free porn sex video online", title=what.lower())

	return render_template (
		"catalog/videos.html", 
		search_term=what,
		page=page,
		description=description
	)	

@catalog.route("/tag/thumb/<int:id>/<slug>.jpg")
def tag_thumb(id, slug):
	"""
	TODO: rewrite this function
	"""
	thumb = db.session.query(VideoThumb.url).join(
		video_tags, video_tags.c.video_id == VideoThumb.video_id
	).filter(video_tags.c.tag_id == id).limit(100).from_self().order_by(db.func.random()).first()

	return redirect(thumb[0])

@catalog.route("/tag/<int:id>/<slug>/")
@catalog.route("/tag/<int:id>/<slug>/page/<int:page>/")
def tag(id, slug, page=1):
	tag = VideoTag.query.get_or_404(id)

	order_by = db.desc(Video.import_date)

	page = tag.videos.order_by(order_by).paginate(page=page, per_page=40)

	description = gettext("Watch %(title)s free porn sex video online", title=tag.name)

	return render_template (
		"catalog/videos.html", 
		page=page,
		tag=tag,
		description=description
	)

@catalog.route("/star/<int:id>/<slug>/")
@catalog.route("/star/<int:id>/<slug>/page/<int:page>/")
def star(id, slug, page=1):
	star = VideoStar.query.get_or_404(id)

	order_by = db.desc(Video.import_date)

	page = star.videos.order_by(order_by).paginate(page=page, per_page=40)

	description = gettext("Watch free porn sex video online starring %(title)s", title=star.name)

	return render_template (
		"catalog/videos.html", 
		page=page,
		star=star,
		description=description
	)

@catalog.route("/video/<int:id>/<slug>.html")
def video(id, slug):
	video = Video.query.get_or_404(id)

	title = translate_video_title(video.title)

	keywords = title.lower().replace(" ", ", ")
	description = gettext("Watch %(title)s free porn sex video online", title=title.lower())

	for tag in video.tags:
		keywords += ", " + tag.name

	video.views += 1

	db.session.commit()

	return render_template (
		"catalog/video.html", 
		video=video,
		keywords=keywords,
		description=description
	)

@catalog.route("/report_video_not_playing/", methods=["POST"])
def report_video_not_playing():
	from tasks import check_video_availability

	if not "id" in request.form: 
		return abort(404)

	video = Video.query.get_or_404(request.form["id"])

	check_video_availability.delay(video.id)

	return gettext("Thank you for your report, our robot will recheck that video automatically.")

@catalog.route("/<slug>.html", methods=["GET", "POST"])
def page(slug):
	form = None

	if not slug in ["disclaimer", "contact_us"]:
		return abort(404)

	if slug == "contact_us":
		form = ContactForm(request.values)

		if request.method == "POST" and form.validate_on_submit():
			flash("contact_us_submitted")

			if not request.headers.getlist("X-Forwarded-For"): ip = request.remote_addr
			else: ip = request.headers.getlist("X-Forwarded-For")[0]

			subject = dict(contact_topics)[form.topic.data]

			msg = Message(subject)
			msg.sender = "MyLust.XXX Contact Form <noreply@mylust.xxx>"
			msg.body = "{name} - {email} - {ip} \n\n {message}".format(name=form.name.data, email=form.email.data, ip=ip, message=form.message.data)
			msg.add_recipient(app.config["CONTACT_EMAIL"])

			mail.send(msg)

			return redirect(url_for("catalog.page", slug="contact_us"))
	
	return render_template (
		"catalog/page_{0}.html".format(slug), 
		form=form,
		hide_search=True
	)

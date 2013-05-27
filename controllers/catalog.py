#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Catalog main view controller
"""
from flask import *

catalog = Blueprint('catalog', __name__, template_folder='templates')

from models import *
from forms import ContactForm, contact_topics
from application import cache, app, mail
from flask.ext.babel import gettext
from flask.ext.babel import refresh as language_refresh
from flask.ext.mail import Message

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


@catalog.route("/tag/thumb/<int:id>/<slug>.jpg")
@cache.cached(timeout=3600)
def tag_thumb(id, slug):
	"""
	TODO: rewrite this function
	"""
	thumb = db.session.query(VideoThumb.url).join(
		video_tags, video_tags.c.video_id == VideoThumb.video_id
	).filter(video_tags.c.tag_id == id).order_by(db.func.random()).first()

	if thumb == None:
		abort(404)

	return redirect(thumb[0])

@catalog.route("/tag/<int:id>/<slug>/")
@catalog.route("/tag/<int:id>/<slug>/page/<int:page>/")
def tag(id, slug, page=1):
	tag = VideoTag.query.get_or_404(id)

	order_by = db.desc(Video.import_date)

	page = tag.videos.order_by(order_by).paginate(page=page, per_page=40)

	return render_template (
		"catalog/tag.html", 
		page=page,
		tag=tag
	)

@catalog.route("/video/<int:id>/<slug>.html")
def video(id, slug):
	video = Video.query.get_or_404(id)

	video.views += 1

	db.session.commit()

	return render_template (
		"catalog/video.html", 
		video=video
	)

@catalog.route("/report_video_not_playing/", methods=["POST"])
def report_video_not_playing():
	if not "id" in request.form: 
		return abort(404)

	video = Video.query.get_or_404(request.form["id"])

	# TODO: add celery function for checking the video status

	return gettext("Thank you for your report, our robot will recheck that video automatically.")

@catalog.route("/page/<slug>.html", methods=["GET", "POST"])
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
	
	return render_template("catalog/page_{0}.html".format(slug), form=form)

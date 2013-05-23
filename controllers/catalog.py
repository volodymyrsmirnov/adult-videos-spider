#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Catalog main view controller
"""

from flask import Blueprint

catalog = Blueprint('catalog', __name__, template_folder='templates')

from models import *

@catalog.route("/")
def index():

	categories = db.session.query(
		VideoTag, 
		db.func.count(video_tags.c.video_id).label('total'),
		db.func.sum(Video.views).label('views'),
	).join(video_tags, Video).group_by(VideoTag).order_by('views DESC, total DESC').first()

	print categories[0].get_random_thumbs()

	return "hello worlds"
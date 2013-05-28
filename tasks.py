#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
import requests

from celery import Celery
from celery import chord

celery = Celery(__name__)

if os.path.exists(".production"): 
	celery.config_from_object('configs.Production')
else: 
	celery.config_from_object('configs.Testing')

from models import db, Video

@celery.task
def check_video_availability(video_id):
	"""
	Check for video availability 
	"""
	video = Video.query.get(video_id)

	if not video: return None

	r = requests.get(video.remote_url)

	if r.status_code == 200 and "is no longer available" not in r.text:
		return True
	else:
		db.session.delete(video)
		db.session.commit()
		return False
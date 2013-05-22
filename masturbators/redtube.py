#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Redtube.com Masturbator

Uses RedTube official API
Details: http://api.redtube.com/docs/
"""

from models import KVS

import time
import anyjson
import datetime
import requests

from masturbator import Masturbator, MasturbatorException

from models import db, KVS, Video, VideoTag, VideoThumb, VideoStar

class RedtubeMasturbator(Masturbator):
	"""
	Redtube masturbator class
	"""
	redtube_id = 0
	data = None

	def __init__(self, redtube_id=1):
		self.redtube_id = redtube_id

	def get_latest_redtube_id(self):

		start_if_undef = 451830

		start_id = KVS.get("redtube_max_id")

		if not start_id:
			start_id = start_if_undef

		continue_search = True

		while continue_search:
			url_patten = "http://www.redtube.com/{0:d}".format(start_id)
			r = requests.head(url_patten)

			print ("URL {0} returned status code {1}".format(url_patten, r.status_code))

			if r.status_code == 200:
				start_id += 1
			else:
				continue_search= False
				KVS.set("redtube_max_id", start_id)

		return True

	def fap(self):
		url_pattern = "http://api.redtube.com/?data=redtube.Videos.getVideoById&video_id={0:d}&output=json&thumbsize=medium".format(self.redtube_id)
		r = self.request(url_pattern)

		try: 
			self.data = anyjson.deserialize(r)
		except ValueError: 
			raise MasturbatorException("wrong json datatype in response")

		video = self.data.get("video") 

		if not video:
			raise MasturbatorException("video not present in response")

		item = dict()

		try:
			item['id'] = int(video.get("video_id"))
		except ValueError:
			item['id'] = None

		item['url'] = video.get("url")
		
		if video.get("publish_date"):
			item['publish_date'] = datetime.datetime.strptime(video.get("publish_date"), "%Y-%m-%d %H:%M:%S")

		item['title'] = video.get("title")

		item['tags'] = list()
		item['thumbs'] = list()
		item['stars'] = list()

		try:
			duration_time = time.strptime(video.get("duration"), "%M:%S")
		except ValueError:
			duration_time = time.strptime(video.get("duration"), "%H:%M:%S")

		item['duration'] = datetime.timedelta(
			hours= duration_time.tm_hour,
			minutes=duration_time.tm_min,
			seconds=duration_time.tm_sec
		).total_seconds() 
		
		if video.get("tags"):
			for tag_id, tag_name in video.get("tags").items():
				item['tags'].append(tag_name.lower())

		thumbs = video.get("thumbs")

		if thumbs:
			for thumb in thumbs:
				item['thumbs'].append(thumb.get("src"))

		if video.get("stars"):
			for star_id, star_name in video.get("stars").items():
				 item['stars'].append(star_name.lower())

		return item

	def save(self):
		item = self.fap()

		video = Video()
		video.title = item.get("title")
		video.masturbator = "redtube"
		video.remote_id = item.get("id")
		video.remote_url = item.get("url")
		video.remote_date = item.get("publish_date")
		video.duration = item.get("duration")

		db.session.add(video)
		db.session.commit()

		for tag_name in item.get("tags"):
			tag = VideoTag.query.filter_by(name=tag_name).first()

			if tag == None:
				tag = VideoTag()
				tag.name = tag_name

			video.tags.append(tag)

		for thumb_url in item.get("thumbs"):
			thumb = VideoThumb()
			thumb.url = thumb_url

			video.thumbs.append(thumb)

		for star_name in item.get("stars"):
			star = VideoStar.query.filter_by(name=star_name).first()

			if star == None:
				star = VideoStar()
				star.name = star_name

			video.stars.append(star)

		db.session.commit()

		return True

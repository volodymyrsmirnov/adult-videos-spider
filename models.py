#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Application data storage models
"""

from application import db

import pickle
import datetime

video_tags = db.Table('mylust_tag_to_video',
	db.Column('tag_id', db.BigInteger, db.ForeignKey('mylust_video_tag.id')),
	db.Column('video_id', db.BigInteger, db.ForeignKey('mylust_video.id'))
)

video_stars = db.Table('mylust_star_to_video',
	db.Column('star_id', db.BigInteger, db.ForeignKey('mylust_video_star.id')),
	db.Column('video_id', db.BigInteger, db.ForeignKey('mylust_video.id'))
)

class Video(db.Model):
	"""
	Main video model
	"""
	__tablename__ = 'mylust_video'

	id = db.Column(db.BigInteger, primary_key=True)

	title = db.Column(db.Unicode(256), index=True)
	duration = db.Column(db.Integer, default=0)

	masturbator = db.Column(db.String(32), index=True)

	remote_id = db.Column(db.BigInteger)
	remote_url = db.Column(db.String(256))

	remote_date = db.Column(db.DateTime(), nullable=True)
	import_date = db.Column(db.DateTime(), default=datetime.datetime.now)

	views = db.Column(db.BigInteger, default=0)

	tags = db.relationship('VideoTag', secondary=video_tags, backref=db.backref('videos', lazy='dynamic'))
	thumbs = db.relationship('VideoThumb', backref='video', lazy='dynamic')
	stars = db.relationship('VideoStar', secondary=video_stars, backref=db.backref('videos', lazy='dynamic'))

	def __repr__(self):
		return "<Video '{0}'>".format(self.remote_url)

class VideoStar(db.Model):
	"""
	Video star
	"""
	__tablename__ = 'mylust_video_star'

	id = db.Column(db.BigInteger, primary_key=True)
	name = db.Column(db.Unicode(256), index=True, unique=True)

	def __repr__(self):
		return "<VideoStar '{0}'>".format(self.name.title())

class VideoThumb(db.Model):
	"""
	Video thumbnail
	"""
	__tablename__ = 'mylust_video_thumb'

	id = db.Column(db.BigInteger, primary_key=True)
	url = db.Column(db.String(256))

	video_id = db.Column(db.BigInteger, db.ForeignKey('mylust_video.id'))

	def __repr__(self):
		return "<VideoThumb '{0}'>".format(self.url)

class VideoTag(db.Model):
	"""
	Video tag / category
	"""
	__tablename__ = 'mylust_video_tag'

	id = db.Column(db.BigInteger, primary_key=True)
	name = db.Column(db.Unicode(256), index=True, unique=True)

	def __repr__(self):
		return "<VideoTag '{0}'>".format(self.name.title())

	def get_random_thumbs(self):
		"""
		Get 3 thumbs for random video in the category
		"""
		return self.videos.order_by(
			db.func.random()
		).first().thumbs.limit(3).all()

class KVS(db.Model):
	"""
	Key-value DB storage abstraction for saving different data 
	"""
	__tablename__ = 'mylust_kvs'

	key = db.Column(db.String(256), primary_key=True, unique=True)
	value = db.Column(db.PickleType())

	@staticmethod
	def get(key):
		item = KVS.query.get(key)

		if not item:
			return None

		try:
			return item.value
		except pickle.UnpicklingError:
			return None

	@staticmethod
	def set(key, value):
		item = KVS.query.get(key)

		if not item:
			item = KVS()
			item.key = key
			item.value = value

			db.session.add(item)

		try:
			item.value = value
		except pickle.PicklingError:
			return False

		db.session.commit()
		return True
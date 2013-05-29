#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Application configs
"""
from flask.ext.babel import lazy_gettext

from datetime import timedelta

class Production(object):
	"""
	Production config
	"""
	DOMAIN = 'http://mylust.xxx'

	CONTACT_EMAIL = 'contact@mylust.xxx'

	SQLALCHEMY_DATABASE_URI = 'postgres://mylust:Nrn75enDLb5eJ9KL@localhost/mylust'
	
	SECRET_KEY = "JNJNnlasdaksjNOINIusdasuiuIBY"

	LANGUAGES = {
		'en': lazy_gettext('English'),
		# 'ru': lazy_gettext('Russian'),
	}

	MANAGER_USER = "masturbator"
	MANAGER_PASSWORD = "Gya4b08M"

	CSRF_ENABLED = True

	# Path to GeoIP database
	GEOIP_V4_DB_PATH = "/usr/share/GeoIP/GeoIP.dat"

	CELERYBEAT_SCHEDULE = {
		'redtube-update-latest-id': {
			'task': 'tasks.redtube_update_latest_id',
			'schedule': timedelta(hours=24),
		},
	}

	BROKER_URL = 'redis://localhost:6379/0'
	# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

	CELERY_TASK_SERIALIZER = 'json'
	CELERY_RESULT_SERIALIZER = 'json'
	CELERY_TIMEZONE = 'UTC'
	CELERY_ENABLE_UTC = True

	CACHE_TYPE = 'memcached'
	CACHE_DEFAULT_TIMEOUT = 300
	CACHE_KEY_PREFIX = 'mylust_'
	CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']

	RECAPTCHA_USE_SSL = False
	RECAPTCHA_PUBLIC_KEY = "6Lc09uESAAAAAN9m-712sJXWx1xZPbGux1T6ckj_"
	RECAPTCHA_PRIVATE_KEY = "6Lc09uESAAAAAERCHgR7ysiPhaUC2TbwLILCMRU1"
	RECAPTCHA_OPTIONS = {}

	# MAIL_SERVER
	# MAIL_PORT
	# MAIL_USE_TLS
	# MAIL_USE_SSL
	# MAIL_DEBUG
	# MAIL_USERNAME
	# MAIL_PASSWORD

	REDIS_HOST = 'localhost'
	REDIS_PORT = 6379
	REDIS_DB = 0

class Testing(Production):
	"""
	Testing config
	"""
	DOMAIN = 'http://127.0.0.1:5000'

	# Debug everything
	DEBUG = True
	SQLALCHEMY_ECHO = True
	MAIL_DEBUG = True
	MAIL_FAIL_SILENTLY = False
	ASSETS_DEBUG = False
	
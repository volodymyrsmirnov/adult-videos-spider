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

	SQLALCHEMY_DATABASE_URI = 'postgres://mylust:Nrn75enDLb5eJ9KL@localhost/mylust'
	
	SECRET_KEY = "JNJNnlasdaksjNOINIusdasuiuIBY"

	LANGUAGES = {
		'en_us': lazy_gettext('English'),
	}

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
	CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

	CELERY_TASK_SERIALIZER = 'json'
	CELERY_RESULT_SERIALIZER = 'json'
	CELERY_TIMEZONE = 'UTC'
	CELERY_ENABLE_UTC = True

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
	ASSETS_DEBUG = True


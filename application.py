#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
MyLust main handler
"""
import sys

reload(sys)
sys.setdefaultencoding("UTF-8")

import os

from flask import *
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask.ext.cache import Cache
from flask.ext.mail import Mail
from flask.ext.redis import Redis

app = Flask(__name__)

if os.path.exists(".production"): 
	app.config.from_object('configs.Production')
else: 
	app.config.from_object('configs.Testing')

babel = Babel(app)
db = SQLAlchemy(app)
cache = Cache(app)
assets = Environment(app)
mail = Mail(app)
redis = Redis(app)

from controllers.catalog import catalog

from models import *

app.register_blueprint(catalog, url_prefix='/<lang_code>')

css = Bundle(

	'source/css/third-party/normalize-1.1.2.css',
	'source/css/third-party/flags.css',

	Bundle(
		'source/css/main.scss',

		filters='scss'
	),

	filters='yui_css',
	output='assets/compiled.css'
)

js = Bundle(
	'source/js/third-party/jquery-1.9.1.min.js',
	'source/js/third-party/jquery-migrate-1.2.1.min.js',
	'source/js/third-party/jquery.unveil.min.js',
	'source/js/third-party/jquery.cookie.js',
	'source/js/third-party/jquery.purl.js',
	'source/js/third-party/jquery.autosize.min.js',

	'source/js/main.js',

	filters='yui_js',
	output='assets/compiled.js'
)

assets.register('css', css)
assets.register('js', js)

@app.route('/')
def redirect_to_language():
	"""
	Redirect browser to best matching language
	"""
	best_language = request.accept_languages.best_match(app.config.get("LANGUAGES").keys())

	if not best_language:
		best_language = 'en'

	return redirect(url_for('catalog.index', lang_code=best_language), code=302)

@app.route('/robots.txt')
def robots():
	"""
	Generate robots.txt
	"""
	response = render_template('robots.txt')
	return Response(response, mimetype='text/plain')

@babel.localeselector
def get_locale():
	"""
	Get locale from global variable
	"""
	lang_code = getattr(g, 'lang_code', None)
	
	if lang_code is not None:
		return lang_code

	return request.accept_languages.best_match(app.config.get('LANGUAGES').keys())

if __name__ == '__main__':
	app.run(debug=True)


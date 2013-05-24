#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
MyLust main handler
"""

import os

from flask import *
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask.ext.cache import Cache

app = Flask(__name__)

if os.path.exists(".production"): 
	app.config.from_object('configs.Production')
else: 
	app.config.from_object('configs.Testing')

babel = Babel(app)
db = SQLAlchemy(app)
cache = Cache(app)
assets = Environment(app)

from controllers.catalog import catalog

from models import *

app.register_blueprint(catalog, url_prefix="/<lang_code>")

css = Bundle(
	Bundle(
		'source/css/third-party/normalize-1.1.2.css',

		Bundle(
			'source/css/*.scss',

			filters='scss'
		),

		filters='cssmin'
	),

	output='assets/compiled.css'
)

js = Bundle(
	'source/js/third-party/jquery-1.9.1.min.js',
	'source/js/third-party/jquery-migrate-1.2.1.min.js',

	Bundle(
		'source/js/*.js',

		filters='jsmin'
	),

	output='assets/compiled.js'
)

assets.register('css', css)
assets.register('js', js)

@app.route("/")
def redirect_to_language():
	"""
	Redirect browser to best matching language
	"""
	best_language = request.accept_languages.best_match(app.config.get("LANGUAGES").keys())
	return redirect(url_for("catalog.index", lang_code=best_language), code=302)

@babel.localeselector
def get_locale():
	"""
	Get locale from global variable
	"""
	lang_code = getattr(g, 'lang_code', None)
	
	if lang_code is not None:
		return lang_code

	return request.accept_languages.best_match(app.config.get("LANGUAGES").keys())

if __name__ == "__main__":
	app.run(debug=True)


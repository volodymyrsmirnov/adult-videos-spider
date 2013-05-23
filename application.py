#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
MyLust main handler
"""

import os

from flask import Flask
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)

if os.path.exists(".production"): 
	app.config.from_object('configs.Production')
else: 
	app.config.from_object('configs.Testing')

babel = Babel(app)
db = SQLAlchemy(app)

from controllers.catalog import catalog

from models import *

app.register_blueprint(catalog)

if __name__ == "__main__":
	app.run(debug=True)

	
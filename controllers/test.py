#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Test controller, just for fun
"""

from flask import Blueprint

test = Blueprint('test', __name__, template_folder='templates')

#from masturbators.redtube import RedtubeMasturbator

from models import *

@test.route("/")
def index():

	#test_masturbator = RedtubeMasturbator()
	#test_masturbator.get_latest()

	return "hello worlds"
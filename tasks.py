#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os

from celery import Celery
from celery.task.sets import TaskSet
from celery import chord

celery = Celery(__name__)

if os.path.exists(".production"): 
	celery.config_from_object('configs.Production')
else: 
	celery.config_from_object('configs.Testing')

from masturbators.masturbator import MasturbatorException
from masturbators.redtube import RedtubeMasturbator

from models import KVS

@celery.task
def redtube_get_latest_id():
	"""
	Get the latest video ID available
	"""
	redtube = RedtubeMasturbator()
	return redtube.get_latest_redtube_id()

@celery.task(rate_limit="5/s")
def redtube_parse_id(redtube_id):
	"""
	Parse the redtube api response and insert DB record
	"""
	redtube = RedtubeMasturbator(redtube_id=redtube_id)

	try:
		return redtube.save()
	except MasturbatorException:
		return False

@celery.task
def redtube_after_parse(results):
	"""
	Execute after parse completed
	"""
	KVS.set("redtube_last_parsed_id", KVS.get("redtube_max_id"))
	
	redtube_get_latest_id.delay()

@celery.task
def redtube_parse_new_ids():
	"""
	Parse new redtube ids
	"""
	max_id = KVS.get("redtube_max_id")
	last_id = KVS.get("redtube_last_parsed_id")

	if not last_id:
		last_id = 0

	tasks = []

	for redtube_id in range(last_id, max_id):
		tasks.append(
			redtube_parse_id.subtask((redtube_id, ))
		)

	chord(tasks)(redtube_after_parse.subtask())

if __name__ == "__main__":
	redtube_update_latest_id()

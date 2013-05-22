#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Redtube Masturbator unittest
"""

from masturbators.masturbator import MasturbatorException
from masturbators.redtube import RedtubeMasturbator

import unittest
import datetime

class Redtube(unittest.TestCase):
	redtube = None

	def setUp(self):
		self.redtube = RedtubeMasturbator(redtube_id=1)

	def test_fap(self):
		try:
			result = self.redtube.fap()

			self.assertEqual(set(("id", "url", "title", "tags", "thumbs", "stars", "publish_date", "duration")), set(result))

			self.assertEqual(result["id"], 1)

			self.assertGreater(len(result["url"]), 0)
			self.assertIn("http://www.redtube.com/", result["url"])

			self.assertGreater(len(result["title"]), 0)
			self.assertGreater(len(result["tags"]), 0)
			self.assertGreater(len(result["thumbs"]), 0)
			self.assertGreater(len(result["stars"]), 0)
			self.assertGreater(result["duration"], 0)

			self.assertIsInstance(result['publish_date'], datetime.datetime)

		except MasturbatorException as e:
			self.fail("MasturbatorException: {0}".format(str(e)))

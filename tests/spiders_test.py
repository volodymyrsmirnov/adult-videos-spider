#!/usr/bin/env python
#-*- coding: utf-8 -*- 

import sys, os, requests

sys.path.append(os.path.join(os.getcwd(), "masturbators"))

import masturbators
from masturbators.spiders import redtube_spider
from masturbators.spiders import xhamster_spider
from masturbators.spiders import youporn_spider

from scrapy.http import Response, Request, TextResponse

import unittest, datetime

class Spiders(unittest.TestCase):

	def get_response(self, url):

		try:
			r = requests.get(url)
		except:
			self.fail("Failed getting url {0}".format(url))
			return None

		request = Request(url=url)

		return TextResponse(
			url=url,
        	request=request,
        	body=r.text,
        	encoding="utf-8"
        )

	def test_redtube(self):
		spider = redtube_spider.RedtubeSpider()
		item = spider.parse_video(self.get_response("http://www.redtube.com/1"))

		self.assertEqual(item["duration"], 86)
		self.assertEqual(item["remote_id"], 1)
		self.assertEqual(item["remote_date"], datetime.datetime(2007, 3, 17, 14, 8, 59))
		self.assertEqual(len(item["stars"]), 1)
		self.assertEqual(len(item["tags"]), 10)
		self.assertEqual(len(item["thumbs"]), 16)
		self.assertEqual(item["title"], u'Heather taking it deep again')

	def test_xhamster(self):
		spider = xhamster_spider.XhamsterSpider()
		item = spider.parse_video(self.get_response("http://xhamster.com/movies/3/sexy_victoria_chatting_and_stripping_on_webcam.html"))

		self.assertEqual(item["duration"], 120)
		self.assertEqual(item["remote_id"], 3)
		self.assertEqual(item["remote_date"], datetime.datetime(2007, 5, 23, 16, 50, 36))
		self.assertEqual(len(item["stars"]), 0)
		self.assertEqual(len(item["tags"]), 4)
		self.assertEqual(len(item["thumbs"]), 10)
		self.assertEqual(item["title"], u'Sexy Victoria chatting and stripping on webcam')

	def test_youporn(self):
		spider = youporn_spider.YoupornSpider()
		item = spider.parse_video(self.get_response("http://www.youporn.com/watch/460338/sasha-grey-always-gets-the-job-done/"))

		self.assertEqual(item["duration"], 387)
		self.assertEqual(item["remote_id"], 460338)
		self.assertEqual(item["remote_date"], datetime.datetime(2010, 8, 6, 0, 0))
		self.assertEqual(len(item["stars"]), 1)
		self.assertEqual(len(item["tags"]), 5)
		self.assertEqual(len(item["thumbs"]), 8)
		self.assertEqual(item["title"], u'Sasha Grey always gets the job done!')
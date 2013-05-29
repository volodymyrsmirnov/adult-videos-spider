import time
import datetime
import requests
import anyjson

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from masturbators.items import VideoItem, first_or_none

from models import *

from scrapy.spider import BaseSpider

class PornhubSpider(BaseSpider):
	name = "pornhub"
	allowed_domains = ["www.pornhub.com"]
	start_urls = ["http://www.pornhub.com/view_video.php?viewkey=337950402"]

	rules = (
		Rule(
			SgmlLinkExtractor(
				allow=['/\d+'], 
			),

			callback='parse_video'
		), 

		Rule(
			SgmlLinkExtractor(
				deny=[
					'/click(.*)',
					'/news(.*)',
					'/contact(.*)',
					'(.*)/mostfavored',
					'(.*)/mostviewed',
					'(.*)/toprated',
				],

				deny_domains=[
					'images.cdn.redtube.com',
				]
			),

			follow=True
		),
	)

	def parse(self, response):
		hxs = HtmlXPathSelector(response)

		video = VideoItem()
		video['title'] = first_or_none(hxs.select("//div[@class='hd-title']/h1/text()").extract())

		if not video['title']:
			return None

		video['remote_url'] = response.url

		try:
			video['remote_id'] = int(video['remote_url'].replace("http://www.pornhub.com/view_video.php?viewkey=", ""))
		except ValueError:
			return None

		"""
		duration = Field()
		remote_id = Field()
		remote_url = Field()
		remote_date = Field()
		import_date = Field()
		views = Field()
		tags = Field()
		thumbs = Field()
		stars = Field()
		"""

		print video

		return None
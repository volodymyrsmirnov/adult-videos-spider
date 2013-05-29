import time
import datetime
import re

from urlparse import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from masturbators.items import VideoItem, first_or_none

from models import *

from scrapy.spider import BaseSpider

url_re = re.compile("http://www.youporn.com/watch/(\d+)/.*")

class YoupornSpider(CrawlSpider):
	name = "youporn"
	allowed_domains = ["www.youporn.com"]
	start_urls = ["http://www.youporn.com/sitemap.html"]

	rules = (
		Rule(
			SgmlLinkExtractor(
				allow=['/watch/\d+/.*'], 
			),

			callback='parse_video'
		), 

		Rule(
			SgmlLinkExtractor(
				deny=[
					'/channels(.*)',
					'/cams(.*)',
					'/premium(.*)',
					'/information(.*)',
				],

				allow_domains = ["www.youporn.com"]
			),

			follow=True
		),
	)

	def parse_video(self, response):
		hxs = HtmlXPathSelector(response)

		video = VideoItem()
		video['title'] = first_or_none(hxs.select("//header[@id='watchHeader']//h1/text()").extract())

		if not video['title']:
			return None

		url_parsed = urlparse(response.url)

		video['remote_url'] = "{0}://{1}{2}".format(url_parsed.scheme, url_parsed.netloc, url_parsed.path)

		try:
			url_re_result = url_re.search(video['remote_url'])
			video['remote_id'] = int(url_re_result.group(1))
		except:
			return None

		remote_date = first_or_none(hxs.select("//div[@class='grid_16 omega generalInfo']//li[label[text()='Date:']]/text()").extract())

		try:
			video['remote_date'] = datetime.datetime.strptime(remote_date.strip(), "%B %d, %Y")
		except: 
			pass

		duration = first_or_none(hxs.select("//div[@class='grid_16 omega generalInfo']//li[label[text()='Duration:']]/text()").extract())

		if duration:
			duration = duration.replace("hrs", ":").replace("min", ":").replace("sec", "").strip()

			try:
				duration_time = time.strptime(duration, "%M:%S")
			except ValueError:
				duration_time = time.strptime(duration, "%H:%M:%S")

			video['duration'] = int(datetime.timedelta(
				hours= duration_time.tm_hour,
				minutes=duration_time.tm_min,
				seconds=duration_time.tm_sec
			).total_seconds())


		video['tags'] = set()
		video['thumbs'] = set()
		video['stars'] = set()

		for tag in hxs.select("//ul[@class='listVideoAttributes']//a[contains(@href, '/category')]/text()").extract():
			if tag[0].isupper():
				video['tags'].add(tag.strip().lower())

		for star in hxs.select("//ul[@id='pornstarSection']//a/text()").extract():
			video['stars'].add(star.strip().lower())

		for thumb in hxs.select("//div[@id='tab-thumbnails']//img/@src").extract():
			video['thumbs'].add(thumb)

		return video
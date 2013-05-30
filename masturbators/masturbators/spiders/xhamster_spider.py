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

url_re = re.compile("http://xhamster.com/movies/(\d+)/.*")

class XhamsterSpider(CrawlSpider):
	name = "xhamster"
	allowed_domains = ["xhamster.com"]
	start_urls = ["http://xhamster.com/channels.php"]

	rules = (
		Rule(
			SgmlLinkExtractor(
				allow=['/movies/\d+/.*'], 
			),

			callback='parse_video'
		), 

		Rule(
			SgmlLinkExtractor(
				deny=[
					'/webcam(.*)',
					'/cam(.*)',
					'/start(.*)',
					'/games(.*)',
					'/stories(.*)',
					'/dating(.*)',
					'/photos(.*)',
					'/information(.*)',
				],

				allow_domains = ["xhamster.com"]
			),

			follow=True
		),
	)

	def parse_video(self, response):
		hxs = HtmlXPathSelector(response)

		video = VideoItem()
		video['masturbator'] = self.name

		url_parsed = urlparse(response.url)
		video['remote_url'] = "{0}://{1}{2}".format(url_parsed.scheme, url_parsed.netloc, url_parsed.path)

		try:
			url_re_result = url_re.search(video['remote_url'])
			video['remote_id'] = int(url_re_result.group(1))
		except:
			return None

		video['title'] = first_or_none(hxs.select("//div[@id='playerBox']//h2[@class='gr']/text()").extract())

		if not video['title']:
			return None
		else:
			video['title'] = video['title'].strip()

		remote_date = first_or_none(hxs.select("//td[@id='videoUser']//span[@class='hint']/@hint").extract())

		if remote_date:
			video['remote_date'] = datetime.datetime.strptime(remote_date, "%Y-%m-%d %H:%M:%S %Z")

		duration = first_or_none(hxs.select("//td[@id='videoUser']//div[span[text()='Runtime:']]/text()").extract())

		if duration:
			duration = duration.strip()

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

		for tag in hxs.select("//td[@id='channels']//a/text()").extract():
			video['tags'].add(tag.lower().strip())

		id_str_part = str(video['remote_id'])[-3:]

		thumb_pattern_url = "http://et1.xhamster.com/t/{id_part}/{number}_{id}.jpg"

		for i in range(1, 11):
			video['thumbs'].add(
				"http://et0.xhamster.com/t/{0}/{1}_{2}.jpg".format(id_str_part, i, video['remote_id'])
			)

		return video
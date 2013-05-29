import time
import datetime
import requests
import anyjson

from urlparse import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from masturbators.items import VideoItem, first_or_none

from models import *

class RedtubeSpider(CrawlSpider):
	name = "redtube"
	allowed_domains = ["www.redtube.com"]
	start_urls = ["http://www.redtube.com/channels"]

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

				allow_domains = ["www.redtube.com"],
			),

			follow=True
		),
	)

	def parse_api_response(self, video):
		url = "http://api.redtube.com/?data=redtube.Videos.getVideoById&video_id={0:d}&output=json&thumbsize=medium".format(video['remote_id'])

		self.log("Parsing Redtube API response {0}".format(url))

		try:
			r = requests.get(url, timeout=5, allow_redirects=True)
		except:
			return None

		if not r.status_code == requests.codes.ok:
			return None

		try: 
			data = anyjson.deserialize(r.text)
		except ValueError:
			return None

		if not "video" in data:
			return None

		api_response = data.get("video")

		video["title"] = api_response.get("title")

		if api_response.get("publish_date"):
			video['remote_date'] = datetime.datetime.strptime(api_response.get("publish_date"), "%Y-%m-%d %H:%M:%S")

		video['tags'] = set()
		video['thumbs'] = set()
		video['stars'] = set()

		try:
			duration_time = time.strptime(api_response.get("duration"), "%M:%S")
		except ValueError:
			duration_time = time.strptime(api_response.get("duration"), "%H:%M:%S")

		video['duration'] = int(datetime.timedelta(
			hours= duration_time.tm_hour,
			minutes=duration_time.tm_min,
			seconds=duration_time.tm_sec
		).total_seconds())

		if api_response.get("tags"):
			for tag_id, tag_name in api_response.get("tags").items():
				video['tags'].add(tag_name.lower())

		if api_response.get("thumbs"):
			for thumb in api_response.get("thumbs"):
				video['thumbs'].add(thumb.get("src"))

		if api_response.get("stars"):
			for star_id, star_name in api_response.get("stars").items():
				 video['stars'].add(star_name.lower())

		return video

	def parse_video(self, response):
		hxs = HtmlXPathSelector(response)

		if "is no longer available" in response.body:
			return None

		video = VideoItem()
		video['masturbator'] = self.name

		url_parsed = urlparse(response.url)
		video['remote_url'] = "{0}://{1}{2}".format(url_parsed.scheme, url_parsed.netloc, url_parsed.path)
		
		video['remote_id'] = first_or_none(hxs.select("//input[@name='object_id']/@value").extract())

		if not video['remote_id']:
			return None
		else:
			try: 
				video['remote_id'] = int(video['remote_id'])
			except ValueError:
				return None

		video = self.parse_api_response(video)

		return video
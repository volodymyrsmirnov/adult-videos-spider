from models import Video

import sys
from urlparse import urlparse

from scrapy.exceptions import IgnoreRequest

class DuplicateVideoMiddleware(object):
	def process_request(self, request, spider):

		url_parsed = urlparse(request.url)

		video_url = "{0}://{1}{2}".format(url_parsed.scheme, url_parsed.netloc, url_parsed.path)

		for matcher in spider.settings['VIDEO_URLS']:
			if matcher.match(video_url):
				query = Video.query.filter(Video.remote_url == video_url).first()

				if not query:
					return None

				spider.log("Video with URL {0} exists in database".format(video_url))
				raise IgnoreRequest()
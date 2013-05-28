from models import Video

import sys

from scrapy.exceptions import IgnoreRequest

class DuplicateVideoMiddleware(object):
	def process_request(self, request, spider):
		for matcher in spider.settings['VIDEO_URLS']:
			if matcher.match(request.url):
				query = Video.query.filter(Video.remote_url == request.url).first()

				if not query:
					return None

				spider.log("Video with URL {0} exists in database".format(request.url))
				raise IgnoreRequest()
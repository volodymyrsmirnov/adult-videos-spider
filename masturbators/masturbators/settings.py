# Scrapy settings for masturbators project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

import os, sys, re

sys.path.append(os.path.join(os.getcwd(), ".."))

BOT_NAME = 'masturbators'

SPIDER_MODULES = ['masturbators.spiders']
NEWSPIDER_MODULE = 'masturbators.spiders'

CONCURRENT_ITEMS = 50
CONCURRENT_REQUESTS = 8

DOWNLOAD_DELAY = 0.25

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': 0,
}

ROBOTSTXT_OBEY = True

USER_AGENT = 'search.xxx (+http://search.xxx)'

ITEM_PIPELINES = [
	'masturbators.pipelines.SaveVideoPipeline',
]

DOWNLOADER_MIDDLEWARES = {
	'masturbators.middlewares.DuplicateVideoMiddleware': 543,
}

VIDEO_URLS = [
	re.compile(r"^http:\/\/www\.redtube\.com\/\d+$"),
]

LOG_LEVEL = 'INFO'
COOKIES_ENABLED = False
RETRY_ENABLED = False
DOWNLOAD_TIMEOUT = 15
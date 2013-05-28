# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

def first_or_none(what):
	return (what + [None])[0]

class VideoItem(Item):
	title = Field()
	duration = Field()
	masturbator = Field()
	remote_id = Field()
	remote_url = Field()
	remote_date = Field()
	import_date = Field()
	views = Field()
	tags = Field()
	thumbs = Field()
	stars = Field()

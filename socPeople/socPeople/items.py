# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class FacultyItem(Item):
	facultyId = Field()
	name = Field()
	email = Field()
	department = Field()
	university = Field()
	link = Field()
	education = Field()
	working = Field()
	keywords = Field()

from scrapy.spider import Spider
from scrapy.selector import Selector

from socPeople.items import FacultyItem 

#class FacultyItem(Item):
#	facultyId = Field()
#	name = Field()
#	email = Field()
#	department = Field()
#	university = Field()
#	link = Field()
#	education = Field()
#	working = Field()
#	keywords = Field()

class SocSpider(Spider):
	name = "soc"
	allowed_domains = ["clemson.edu"]
	start_urls = [
			"http://www.clemson.edu/ces/computing/people/index.html",
	]

	def parse(self, response):
		sel = Selector(response)
		faculties = sel.xpath('//div[contains(@class, "span-6")]')
		items = []
		index = 0;
		for faculty in faculties:
			index = index + 1
			print index
			item = FacultyItem()
			item['facultyId'] = index
			item['name'] = faculty.xpath('b/a/text()').extract()
			if not item['name']: 
				item['name'] = faculty.xpath('b/text()').extract()
				item['link'] = "" 
			else:
				item['link'] = faculty.xpath('b/a/@href').extract() 
			item['name'] = item['name'][0]
			item['email'] = faculty.xpath('a[contains(@href, "mailto")]/text()').extract()
			item['education'] = ""
			item['working'] = ""
			item['keywords'] = ""
			item['department'] = "Computing Science"
			item['university'] = "Clemson University"
			items.append(item)

		return items

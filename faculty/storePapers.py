#!/usr/bin/env python

#Use a JSON file which contain a list of professor names as the input file. For each name in the list get a search result from Google Scholar and download all the PDF papers that Google Scholar can find.

from scrapPaper import query

import simplejson as json
import string
import os
import time
import random
import optparse


def main(start, faculty, result, paper):
	faculty = json.load(open(faculty))

	for j in range(start, len(faculty)):
		print str(j + 1) + '  ' + faculty[j]['name']
		name = string.replace(faculty[j]['name'], ' ', '_').lower()
		try:
			os.stat(name)
		except:
			os.mkdir(name)
	
		infoFile = name + '/info.json'
		with open(infoFile, 'w') as f:
			f.write(json.dumps(faculty[j]))

		papers = dict() #all the papers that will get from Google Scholar for a given name
		for i in range(0, result):
			papers = query(faculty[j]['name'], i * 10, papers)
			if(len(papers) >= paper): # has got enough papers then break
				break
			i = i + 1
			#sleep 60~120 seconds to imitate human click
			t = random.uniform(60, 120)
			print 'page', str(i), 'sleep ', t, 's'
			time.sleep(t)

if __name__ == "__main__":
	usage = 'Usage: %prog [options]' 
	parser = optparse.OptionParser(usage)
	parser.add_option("-s", "--start", dest = "start", type = "int", 
			default = 0, help = "give a list of faculty, where you want to start the crawl")
	parser.add_option("-f", "--inputfile", dest = "inputfile", help = "a JSON file which contain a list of names")
	parser.add_option("-r", "--result", dest = "result", default = 10, type = "int", help = "indicate how many result pages you want to crawl")
	parser.add_option("-p", "--paper", dest = "paper", default = 100, type = "int", help = "indicate how many papers you want to crawl")
	(options, args) = parser.parse_args()
	start = options.start
	faculty = options.inputfile
	if faculty == None:
		parser.error("No input file found.\n Use -h or --help to see usage information")
	result = options.result
	paper = options.paper
	main(start, faculty, result, paper)

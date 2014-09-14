#!/usr/bin/env python

from wos import WokmwsSoapClient 

import simplejson as json
import string
import os
import random
import optparse
import time

# maximum papges that we will crawl

def main(start, faculty, paper):
	faculty = json.load(open(faculty))

	soap = WokmwsSoapClient()	

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

		userQuery = faculty[j]['name'].split()
		length = len(userQuery)
		userQuery = 'AU=' + userQuery[length - 1] + ' ' + userQuery[0]

		results = soap.search(userQuery)
		resultFile = name + '/result'
		with open(resultFile, 'w') as f:
			f.write(str(results))
		# 2 requests per second, 5 requests per minute, so sleep 12 seconds 
		time.sleep(12)


if __name__ == "__main__":
	usage = 'Usage: %prog [options]' 
	parser = optparse.OptionParser(usage)
	parser.add_option("-s", "--start", dest = "start", type = "int", 
			default = 0, help = "give a list of faculty, where you want to start the crawl")
	parser.add_option("-f", "--inputfile", dest = "inputfile", help = "a JSON file which contain a list of names")
	parser.add_option("-p", "--paper", dest = "paper", default = 10, type = "int", help = "indicate how many papers you want to crawl [default: %default]")
	(options, args) = parser.parse_args()
	start = options.start
	faculty = options.inputfile
	if faculty == None:
		parser.error("No input file found.\n Use -h or --help to see usage information")
	paper = options.paper
	main(start, faculty, paper)

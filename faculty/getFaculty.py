#! /usr/bin/env python

#Get a list of SOC faculty names from http://www.clemson.edu/ces/computing/people/index.html
#I use scrapy to complete this job, here is the link to scrapy: https://github.com/ayumilong/scrapy

import os
os.system('cd ../socPeople && rm -f faculty.json && scrapy crawl soc -o faculty.json -t json')
os.system('rm -f faculty.json')
os.system('cp ../socPeople/faculty.json faculty.json')

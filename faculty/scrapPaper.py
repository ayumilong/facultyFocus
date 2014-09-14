#!/usr/bin/env python

#scrapPaper - Get papers infomation for a given scholar name from Google Scholar

import urllib2
import cookielib
import re
import hashlib
import random
import sys
import os
import subprocess
import logging
import optparse
import time

import simplejson as json #Simple, fast, extensible JSON encoder/decoder for Python
from BeautifulSoup import BeautifulSoup #Beautiful Soup is a Python library for pulling data out of HTML and XML files

from htmlentitydefs import name2codepoint #Definitions of HTML general entities. This module defines three dictionaries, name2codepoint, codepoint2name, and entitydefs. I use name2codepoint in this script. Name2codepoint is a dicrionary that maps HTML entity names to the Unicode codepoints.


#Web link example of Google Scholar result: scholar.google.com/scholar?q=brian+malloy&btnG=&hl=en&as_sdt=0%2C41

#google id that used in Cookie
googleId = hashlib.md5(str(random.random())).hexdigest()[:16]

GOOGLE_SCHOLAR_URL = "http://scholar.google.com"
# the cookie looks normally like:
#		'Cookie' : 'GSP=ID=%s:CF=4' % google_id }
# where CF is the format (e.g. bibtex). since we don't know the format yet, we
# have to append it later

# blow is an example of the cookie
# GSP=ID=4cdab13a3e00406f:IN=7bfe18530ee97dbe+7e6cc990821af63:CF=4:LM=1401732980:S=d-FH72_jcR3Ee5ap; expires=Wed, 01 Jun 2016 18:16:19 GMT; path=/; domain=.scholar.google.com

HEADERS = {
		   'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.132 Safari/537.36',
		   'Cookie': 'GSP=ID=%s' % googleId,
		   }

#Four different kind of format for presenting bibliographies, citations and references. In this script, I choose to use BibTex 
FORMAT_REFMAN = 2
FORMAT_ENDNOTE = 3
FORMAT_BIBTEX = 4
FORMAT_WENXIANWANG = 5

# an example of bibTex entry
'''
@article{malloy1998alpha,
  title={alpha< sub> 1-ADRENERGIC</sub> RECEPTOR SUBTYPES IN HUMAN DETRUSOR},
  author={Malloy, Brian J and PRICE, DAVID T and Price, R and BIENSTOCK, ALAN M and DOLE, MARK K and FUNK, BONNIE L and RUDNER, XIAOWEN L and RICHARDSON, CHARLENE D and DONATUCCI, CRAIG F and SCHWINN, DEBRA A},
  journal={The Journal of urology},
  volume={160},
  number={3},
  pages={937--943},
  year={1998},
  publisher={Elsevier}
}
'''
# Transfer bibTex entry to JSON format to make it easy to use
def bib2json(bibEntry):
	# find the title
	titleStart = bibEntry.find('title={')
	if titleStart == -1:
		print 'Invalid bibTex entry'
		sys.exit(1)
	else:
		titleStart = titleStart + 7
	titleEnd = bibEntry.find('}', titleStart)
	# get title
	title = bibEntry[titleStart:titleEnd]

	authorStart = bibEntry.find('author={', titleEnd)
	if authorStart == -1:
		print 'Invalid bibTex entry'
		sys.exit(1)
	else:
		authorStart = authorStart + 8
	authorEnd = bibEntry.find('}', authorStart)
	authors = bibEntry[authorStart:authorEnd]
	authors = authors.split(' and ')
	# get a list of authors' name
	author = list()
	for name in authors:
		tmp = dict()
		tmp["name"] = name.lower()
		author.append(tmp)

	yearStart = bibEntry.find('year={', authorEnd)
	if yearStart == -1:
		print 'Invalid bibTex entry'
		sys.exit(1)
	else:
		yearStart = yearStart + 6
	yearEnd = bibEntry.find('}', yearStart)
	# get the year of the paper
	year = bibEntry[yearStart:yearEnd]

	# the json format of this bibTex entry
	result = dict()
	result['title'] = title
	result['authors'] = author
	result['year'] = year
	return result



def query(searchStr, start, papers, outFormat = FORMAT_BIBTEX):
	logging.debug("Query: %s" % searchStr) #Logs a message with level DEBUG on the root logger
	# start means which page do we want to get
	if start != 0:
		search = '/scholar?start=' + str(start) + '&q=' + searchStr.replace(' ', '+')
	else:
		search = '/scholar?q=' + searchStr.replace(' ', '+')
	url = GOOGLE_SCHOLAR_URL + search + "&btnG=&hl=en&as_sdt=0%2C41"
	header = HEADERS
	header['Cookie'] = header['Cookie'] + ":CF=%d" % outFormat
	# set a proxy web server
	#proxy_ip = urllib2.ProxyHandler({'http':'http://23.89.198.161:7808'})
	#opener = urllib2.build_opener(proxy_ip, urllib2.HTTPHandler)
	#urllib2.install_opener(opener)
	
	request = urllib2.Request(url, headers=header)
	try:
		response = urllib2.urlopen(request)
		realUrl = response.geturl()
		if realUrl != url:
			print 'I am a robot!!!'
			sys.exit(1)
		html = response.read()
		html.decode('ascii', 'ignore')
	except Exception as e: 
		print e, '  ', url #print the error code 
		if hasattr(e, 'code'):
			if e.code == 503: #if Google block me then exit
				sys.exit(1)
		return papers 

	#store the result to local file
	rootDir = searchStr.replace(' ', '_').lower()
	try:
		os.stat(rootDir)
	except:
		os.mkdir(rootDir)

	pageDir = rootDir + '/page' + str(start / 10 + 1) #for each result page, creat a diretory
	try:
		os.stat(pageDir)
	except:
		os.mkdir(pageDir)
	
	#store the page source to local file
	sourceCode = pageDir + '/sourcecode.html'
	with open(sourceCode, 'w') as f:
		f.write(html)


	'''
	# read html from a html file
	sourceCode = pageDir + '/sourcecode.html'
	with open(sourceCode, 'r') as f:
		html = f.read()
	'''

	# grab the paper content links, maybe this is a downloadable file link
	paperLinks = get_paper_links(html, pageDir)


	# grab the bibtex entry links
	bibLinks= get_bib_links(html, outFormat)

	# follow the bibtex links to get the bibtex entries
	bibResult = list()
	for i in range(0, len(bibLinks)):
		if paperLinks[i] != 'No Link': #for some result, there is no link for a specific web page
			url = GOOGLE_SCHOLAR_URL + bibLinks[i]
			request = urllib2.Request(url, headers=header)
			try:
				response = urllib2.urlopen(request)
			except Exception as e:
				print e, '   ', url
				sys.exit(1)
			else:
				bib = response.read()
				# transform bibTex entry to json form
				jsonObj = bib2json(bib)
				bibResult.append(jsonObj)
				print 'the', str(i + 1), ' JSON entry:'
				print jsonObj
				t = random.uniform(60, 120)
				print 'wait next bibText entry: ', t, 's'
				# sleep 60~120 seconds to imitate human click
				time.sleep(t)
	
	bibFile = pageDir + '/bibLinks.json'
	with open(bibFile, 'w') as f:
		f.write(json.dumps(bibResult))


	links = list()
	index = -1
	i = 0
	for link in paperLinks:
		if link != 'No Link':
			i = i + 1
			# index in bibResult above
			index = index + 1
			# first, judge if there is this professor name in the author list of bibTex entry
			authors = bibResult[index]['authors'] # get a list of authors' name
			keys = searchStr.lower().split(' ')

			found = True # if or not the current paper is a paper that belong to this professor
			for author in authors:
				found = True
				for key in keys:
					if author['name'].find(key) == -1: # can't find a suitable author, then this paper is not a suitable paper
						found = False
						break # go to try next author 
				if found == True: # find a suitable author
					break

			# second, judge if this paper has been downloaded or not
			if found == True:
				if bibResult[index]['title'] in papers: # we have downloaded this paper already
					continue
				papers[bibResult[index]['title']] = 'true' # add this paper's title to dict papers
			else:
				continue # go to get next paper

			tmp = dict()
			tmp["link"] = link
			links.append(tmp)

			try:
				header = {
		   'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.132 Safari/537.36',
		   }
				# set cookie
				cookie = cookielib.CookieJar()
				cookie_p = urllib2.HTTPCookieProcessor(cookie)
				urllib2.install_opener(urllib2.build_opener(cookie_p))
				request = urllib2.Request(link, headers=header)
				response = urllib2.urlopen(request, timeout = 300)
				info = response.info()
				mainType = info.getmaintype()
				subType = info.getsubtype()
				if mainType == 'text' and subType == 'html': # this is just a web page so download the source code
					with open(pageDir + '/' + str(i) + '.html', 'w') as f:
						f.write(response.read())
						print 'Download ', str(i), '.html'
				elif mainType == 'application': # maybe this is a pdf file, postscript file or msword file
					if subType == 'pdf':
						with open(pageDir + '/' + str(i) + '.pdf', 'w') as f:
							f.write(response.read())
							print 'Download ', str(i), '.pdf'
					elif subType == 'text':
						with open(pageDir + '/' + str(i) + '.txt', 'w') as f:
							f.write(response.read())
							print 'Download ', str(i), '.txt'
					elif subType == 'msword':
						with open(pageDir + '/' + str(i) + '.doc', 'w') as f:
							f.write(response.read())
							print 'Download ', str(i), '.doc'
							# convert this doc file to pdf file
					elif subType == 'postscript':
						with open(pageDir + '/' + str(i) + '.ps', 'w') as f:
							f.write(response.read())
							print 'Download ', str(i), '.ps'
							# convert this postscript file to pdf file
					elif subType == 'octet-stream': # need to get the file type from url
						url = str(link)
						fileType = url[url.rfind('.'):len(url)]
						with open(pageDir + '/' + str(i) + fileType, 'w') as f:
							f.write(response.read())
							print 'Download ', str(i), fileType 
			except Exception as e:
				print e, '   ', url
				continue
	paperFile = pageDir + '/paperLinks.json'
	with open(paperFile, 'w') as f:
		f.write(json.dumps(links))
	print 'after write file ', paperFile

	# return how many related papers we have got from this result page
	return papers 


def get_bib_links(html, outFormat):
	#Return a list of reference links from the html according to its sourcecode
	if outFormat == FORMAT_BIBTEX:
		refRe = re.compile(r'<a href="(/scholar\.bib\?[^"]*)"')
	elif outFormat == FORMAT_ENDNOTE:
		refRe = re.compile(r'<a href="(/scholar\.enw\?[^"]*)"')
	elif outFormat == FORMAT_REFMAN:
		refRe = re.compile(r'<a href="(/scholar\.ris\?[^"]*)"')
	elif outFormat == FORMAT_WENXIANWANG:
		refRe = re.compile(r'<a href="(/scholar\.ral\?[^"]*)"')
	refList = refRe.findall(html)
	# escape html enteties
	refList = [re.sub('&(%s);' % '|'.join(name2codepoint), lambda m:
		unichr(name2codepoint[m.group(1)]), s) for s in refList]

	return refList

# get the correct link of the paper from a list of html tags
def getLink(tags): 
	for tag in tags:
		try:
			if tag.name == 'a':
				return tag['href']
				break
		except:
			continue
	return 'No Link'

def get_paper_links(html, pageDir): #according to the sourcecode to get paper content link from a result page
	#Return a list of real paper links from html
	papers = BeautifulSoup(''.join(html))
	papers = papers.findAll('div', {'class': 'gs_r'}) #according to the sourcecode to find suitable element

	paperList = list()

	i = 0

	for paper in papers:
		i = i + 1
		if(paper.contents[0].name == 'h3'): # this is the profile page of a given professor
			i = i - 1
			continue
		if len(paper) == 1: # no pdf file found
			href = getLink(paper.contents[0].contents[0])
			paperList.append(href)
		elif len(paper) == 2: # pdf maybe found
			tagLens = len(paper.contents[0].contents[1])
			if tagLens == 1: # the original link is a pdf file 
				href = getLink(paper.contents[0].contents[1])
				paperList.append(href)
			elif tagLens == 2: # find the original link
				href = getLink(paper.contents[1].contents[0])
				paperList.append(href)
			else: 
				#maybe has pdf file link
				href = getLink(paper.contents[0].contents[1])
				try:
					# maybe the pdf link is invalid, if not, then donwload it
					response = urllib2.urlopen(href)
					paperList.append(href)
				except:
					href = getLink(paper.contents[1].contents[0])
					paperList.append(href)

		
	return paperList

if __name__ == "__main__":
	usage = 'Usage: %prog [options] {"search terms"}'
	parser = optparse.OptionParser(usage)
	parser.add_option("-d", "--debug", action="store_true", dest="debug",
			default=False, help="show debugging output")
	parser.add_option("-f", "--outputformat", dest='output',
			default="bibtex", help="Output format. Available formats are: bibtex, endnote, refman, wenxianwang [default: %default]")
	parser.add_option("-p", "--pagenumber", dest='page', default=1, type='int', help="The page number of search result that you want [default: %default]")
	(options, args) = parser.parse_args()
	if options.debug == True:
		logging.basicConfig(level=logging.DEBUG)
	if options.output == 'bibtex':
		outFormat = FORMAT_BIBTEX
	elif options.output == 'endnote':
		outFormat = FORMAT_ENDNOTE
	elif options.output == 'refman':
		outFormat = FORMAT_REFMAN
	elif options.output == 'wenxianwang':
		outFormat = FORMAT_WENXIANWANG
	start = (options.page - 1) * 10
	if len(args) != 1:
		parser.error("No argument given, nothing to do.\nUse --help to see usage infomation")
		sys.exit(1)
	args = args[0]
	logging.debug("Assuming you want me to lookup the query: %s." % args)
	# run query
	papers = dict()
	query(args, start, papers)

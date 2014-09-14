#!/usr/bin/env python

#Get Title, Abstract and Keywords(maybe) given a PDF file

import simplejson as json
import string
import os
import time
import random
import optparse
import subprocess 
import re
import shutil


def main(faculty):
	faculty = json.load(open(faculty)) #load a list of names

	for j in range(0, len(faculty)):
		name = string.replace(faculty[j]['name'], ' ', '_').lower()
		try:
			os.stat(name)
		except:
			os.mkdir(name)
		paperDir = name + "/papers";
		try:
			os.stat(paperDir)
			shutil.rmtree(paperDir)
			os.mkdir(paperDir)
		except:
			os.mkdir(paperDir)
	
		info = dict() 
		info['name'] = faculty[j]['name']
		papers = list()
		sequence = 1
		for i in range(0, 10):
			pageDir = name + '/page' + str(i + 1)
			try:
				os.stat(pageDir)
				'''
				# try to get abstract from Google Scholar result page
				sourceCode = pageDir + '/sourcecode.html'
				with open(sourceCode, 'r') as f:
					html = f.read()
				p = BeautifulSoup(''.join(html))
				p = p.findAll('div', {'class': 'gs_rs'})
				print len(p)
				'''

				for k in range(0, 10):
					pdf = pageDir + '/' + str(k + 1) + '.pdf'
					try:
						os.stat(pdf)
						# has pdf file then get title, abstract and keywords
						# pdftotext is simple tool which can transfer pdf file to text file
						text = subprocess.Popen(["pdftotext", "-q", pdf, "-"], stdout=subprocess.PIPE).communicate()[0]
						lines = text.strip().split("\n")
						# find abstract
						hasAbstract = False
						f = 0
						for line in lines:
							if line.find('ABSTRACT') != -1 or line.find('Abstract') != -1:
								hasAbstract = True
								break
							f = f + 1
						if hasAbstract == True:
							s = lines[f:f + 15]
						else:
							s = lines[8:20]
						abstract = ""
						for a in s:
							abstract = abstract + " " + a

						# find keywords
						hasKeywords = False
						for m in range(0, len(lines)):
							if lines[m].find('Keywords') != -1 or lines[m].find('KEYWORDS') != -1 or lines[m].find('Index Terms') != -1 or lines[m].find('INDEX TERMS') != -1:
								hasKeywords = True
								break;
						if hasKeywords == True:
							keywords = lines[m] + " " + lines[m + 1]
						else:
							keywords = ''
						

						tmp = dict()
						tmp['id'] = sequence 
						tmp['title'] = lines[0]
						tmp['abstract'] = abstract 
						tmp['keywords'] = keywords 
						pattern = re.compile('\w')
						match = re.match(pattern, tmp['title'])
						if match != None:
							papers.append(tmp)
							tmpPaperPdf = paperDir + "/" + str(sequence) + ".pdf"
							subprocess.Popen(["cp", pdf, tmpPaperPdf])
							tmpPaperFile = paperDir + "/" + str(sequence) + ".txt"
							with open(tmpPaperFile, 'w') as f:
								f.write(text)
							tmpJsonFile = paperDir + "/" + str(sequence) + ".json"
							with open(tmpJsonFile, 'w') as f:
								f.write(json.dumps(tmp))
							sequence = sequence + 1
					except:
						# no pdf file for this paper, try next one
						continue
			except:
				break
		info['papers'] = papers

		infoFile = name + '/paper.json'
		with open(infoFile, 'w') as f:
			f.write(json.dumps(info))

		paperFile = name + '/papers.json'
		with open(paperFile, 'w') as f:
			f.write(json.dumps(papers))

		print str(j) + ' ' + name


if __name__ == "__main__":
	usage = 'Usage: %prog [options]' 
	parser = optparse.OptionParser(usage)
	parser.add_option("-f", "--inputfile", dest = "inputfile", help = "a JSON file which contain a list of names")
	(options, args) = parser.parse_args()
	faculty = options.inputfile
	if faculty == None:
		parser.error("No input file found.\n Use -h or --help to see usage information")
	main(faculty)

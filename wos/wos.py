#!/usr/bin/env python
 
import logging
import optparse

from suds.client import Client

 
class WokmwsSoapClient():
	"""
	main steps you have to do:
		soap = WokmwsSoapClient()
		results = soap.search(...)
	"""
	def __init__(self):
		logging.basicConfig(level=logging.ERROR)
		logging.getLogger('suds.client').setLevel(logging.ERROR)
		logging.disable(logging.ERROR)

		self.url = self.client = {}
		self.SID = ''
 
		self.url['auth'] = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
		self.url['search'] = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
 
		self.prepare()
 
	def __del__(self):
		self.close()
 
	def prepare(self):
		"""does all the initialization we need for a request"""
		self.initAuthClient()
		self.authenticate()
		self.initSearchClient()
 
	def initAuthClient(self):
		self.client['auth'] = Client(self.url['auth']) #Authentication SOAP client
 
	def initSearchClient(self):
		self.client['search'] = Client(self.url['search'], headers = {'cookie' : 'SID=' + self.SID}) #Search SOAP client
		print self.client['search']
 
	def authenticate(self): #Do authentication
		self.SID = self.client['auth'].service.authenticate()
 
	def close(self): #Close the current session
		self.client['auth'].service.closeSession()
 
	def search(self, query):
		qparams = self.client['search'].factory.create('queryParameters')
		qparams.databaseId = 'WOK' #search all the databases
		qparams.userQuery = query 
		qparams.queryLanguage = 'en'

		rparams = self.client['search'].factory.create('retrieveParameters')
		rparams.firstRecord = 1
		rparams.count = 100
		rparams.sortField = [{
			'name' : 'PY',
			'sort' : 'D',
			}]
		#rparams.viewField = [{
		#	'collectionName' : 'WOK',
		#	'fieldName' : 'names',
		#	}]	
 
		return self.client['search'].service.search(qparams, rparams)


if __name__ == "__main__":
	usage = 'Usage: %prog [options]' 
	parser = optparse.OptionParser(usage)
	parser.add_option("-a", "--author", dest='author', help="The authors' name that you want to search for")
	parser.add_option("-s", "--search_area", dest='searchArea', default='all', type='string', help="The search area that you want to search [default: %default]")
	(options, args) = parser.parse_args()
	# run query
	if options.author:
		author = 'AU=' + options.author
	else:
		print 'No parameter, use -h for help'
		exit(1)
	if options.searchArea == 'all':
		userQuery = author
	else:
		userQuery = author + ' AND ' + 'SU=' + options.searchArea
	
	soap = WokmwsSoapClient()
	results = soap.search(userQuery)
	print results
	

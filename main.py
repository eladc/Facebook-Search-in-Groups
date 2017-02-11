#!/usr/bin/env python

from facepy import GraphAPI, utils
from sys import argv,exit
import facepy.exceptions
import datetime
import csv
import os
import ConfigParser
import json
import io
import re

class Main:
	def __init__(self, *args):	

		##
		for arg in args:
			if arg is None:
				search_since = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
			else:
				search_since = arg
			
		## return a list from a Config Parser option.
		def getlist(set_list, sep=','):
			return [ item.strip() for item in set_list.split(sep)]
		
		## Read settings
		settings = ConfigParser.ConfigParser()
		settings.read('settings.ini')
	
		## Variables
		app_ID = int(settings.get('App', 'app_ID'))
		app_key = settings.get('App', 'app_key')
		user_access_token = settings.get('App', 'ua_token')
		## search terms as a list of strings
		search_terms = getlist(settings.get('Search', 'term'))
	
		## A token to search within groups
		access_token = utils.get_application_access_token(app_ID, app_key)
	
		## API object
		graph = GraphAPI(access_token)
		u_graph = GraphAPI(user_access_token)

	    ## Load group ID's
		ids_list = 'ids.csv'

		## Create ID list from urls if not exist
		if not os.path.isfile(ids_list):
			group_ids = csv.writer(open(ids_list, 'a'))
			## original group urls 
			with open('urls') as f:
				urls_src = f.readlines()
		## convert group name into group id, user access token is needed.
			for line in urls_src:
				group_name = str(line.split('/')[4]).strip('/').strip('\n')
				try:
					grp_data_name = u_graph.search(group_name, 'group')
				except facepy.exceptions.OAuthError as e:
					print e
					print "Verify your user access token"
					os.remove(ids_list)
					exit(1)	
				try:
					if type(grp_data_name['data'][0]) is dict and grp_data_name['data'][0]['privacy'] == 'OPEN':
						gid = grp_data_name['data'][0]['id']
						group_ids.writerow([group_name, gid])
					else:
						pass
				except IndexError:
					group_ids.writerow([group_name, group_name])
			f.close()
			exit(0)
		else:
			group_ids = csv.reader(open(ids_list, 'r'))

		## compile a list of search terms with ignoring case flag.
		comp_searcht = re.compile(r"(?=("+'|'.join(search_terms)+r"))", re.IGNORECASE)
		
		## Create a new html file
		self.htmlout = open(search_since, 'w+')
		self.htmlout.write(self.htmlHeader(search_since).encode('utf8'))
		
		## iterate through groups
		for id_line in group_ids:
			self.htmlout.write(self.htmlGroupTitle(id_line).encode('utf8'))
			groupData = graph.get(id_line[1]+'/feed', page=True, since=search_since)
			self.getJobs(groupData, comp_searcht)
			
		self.htmlout.write(self.htmlCloseTags().encode('utf8'))
		self.htmlout.close()
		
	def getJobs(self, groupData, comp_searcht):
		try:
			for data in groupData:
				json_data = json.loads(json.dumps(data))	 	
				for item in json_data['data']:
					try:
						msg = item['message']
						if comp_searcht.search(msg):
							msg = msg.replace('\n', '<br />')
							self.htmlout.write(self.htmlOpenParagraph().encode('utf8'))
							self.htmlout.write(msg.encode('utf8'))
							self.htmlout.write(self.htmlCloseParagraph().encode('utf8'))
							continue
					except (KeyError):
						pass
		except facepy.exceptions.FacebookError as e:
			print e
			print "consider removing this group"
	
	## HTML tags 	
	def htmlHeader(self, text):
		html = """\
		<html>
			<head><h3>Jobs since {text}</h3></head>
			<body>
		""".format(text=text)
		return unicode(html)
		
	def htmlGroupTitle(self, text):
		html = """\
		<br></br>
		<p>
		#####################
		<h3>{text}</h3>
		</p>
		""".format(text=text)
		return unicode(html)

	def htmlOpenParagraph(self):
		html = """\
		<br></br>
		<p>
		<h3>-----------------</h3>
		"""
		return unicode(html)
		
	def htmlCloseParagraph(self):
		html = """\
		</p>
		"""
		return unicode(html)
		
	def htmlCloseTags(self):
		html = """\
		</body>
		</html>
		"""
		return unicode(html)
							
if __name__ == '__main__':
	## Check if date is in valid format
	def validate(date_text):
		try:
			if datetime.datetime.strptime(date_text, '%Y-%m-%d'):
				return True
		except ValueError:
			print "Incorrect date format, should be YYYY-MM-DD"
			exit(1)
        	
	## CL arguments
	def parseArgs(): 
		if len(argv) > 2:
			print "Too many arguments"
			exit(1)
		elif len(argv) == 1:
			pass
		else:
  			validate(argv[1])
			return argv[1]
			
	args = parseArgs()
	app = Main(args)
	exit(0)


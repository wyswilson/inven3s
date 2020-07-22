import datetime
import flask

import functools
import mysql.connector
import hashlib
import urllib
import logging
import simplejson as json
import requests
import random
import bs4
import re
import configparser
import werkzeug.security
import jwt

config = configparser.ConfigParser()
config.read('conf.ini')

apisecretkey	= config['auth']['secretkey']
logfile 		= config['path']['log']
mysqlhost 		= config['mysql']['host']
mysqlport 		= config['mysql']['port']
mysqluser 		= config['mysql']['user']
mysqlpassword 	= config['mysql']['password']
mysqldb 		= config['mysql']['db']
defaultbrandid 		= config['default']['brandid']
defaultbrandname 	= config['default']['brandname']
defaultretailercity = config['default']['retailercity']
defaultdateexpiry 	= config['default']['dateexpiry']
useragents 		= json.loads(config['scraper']['useragents'].replace('\n',''))

db = mysql.connector.connect(
	host = mysqlhost,
	port = mysqlport,
	user = mysqluser, passwd = mysqlpassword, database=mysqldb)
cursor = db.cursor()

logging.basicConfig(filename=logfile,level=logging.DEBUG)

def savelisting(listinglink,listingdate,listingtitle,listinghtml,userlink,sourcename,sourcelink):
	query1 = "REPLACE INTO deals_listings (listingurl,listingdate,listingtitle,listinghtml,userurl,sourcename,sourceurl) VALUES (%s,%s,%s,%s,%s,%s,%s)"
	cursor.execute(query1,(listinglink,listingdate,listingtitle,listinghtml,userlink,sourcename,sourcelink))
	db.commit()

#def saveproductpage(producturl,producthtml,sourcelink):
#	query1 = "REPLACE INTO deals_listingorigins (productpageurl,productpagehtml,sourceurl) VALUES (%s,%s,%s)"
#	cursor.execute(query1,(producturl,producthtml,sourcelink))
#	db.commit()

def downloadhtml(url):
	urlresolved = ''
	html = ''
	try:
		randagent = random.choice(useragents)
		headers = {'User-Agent': randagent}
		r = requests.get(url, headers=headers, timeout=10)
		urlresolved = r.url
		html = r.content
	except requests.ConnectionError as e:
		print("[%s] -> internet connection error [%s]" % (url,str(e)))
	except requests.Timeout as e:
	    print("[%s] -> timeout error [%s]" % (url,str(e)))
	except requests.RequestException as e:
	    print("[%s] -> general error [%s]" % (url,str(e)))

	return urlresolved, html

def fetchmostrecent():

	query2 = "SELECT max(listingdate) FROM deals_listings"
	cursor.execute(query2)
	records = cursor.fetchall()
	mostrecentlistingdate = records[0][0]

	return mostrecentlistingdate

def extractandsavemetadata(listingurl,listinghtml):
	matches = re.findall(r'"(\/(?:product|brand|tag|cat)\/.+?)"',listinghtml.decode('utf-8'))
	for matchuri in matches:
		typeobj = re.search(r'^\/(.+?)\/', matchuri, re.IGNORECASE)
		metadatatype = typeobj.group(1).strip()
		metadatauri = rooturl + matchuri

		metadatauriresolved, metadatahtml = downloadhtml(metadatauri)

		if metadatahtml != '' and metadatahtml is not None:
			metadataname = extractmetadataname(metadatatype,metadatahtml.decode('utf-8'))
			print("\t[%s][%s][%s]" % (metadatatype,metadataname,metadatauri))
			addmetadata(listingurl,metadatauri,metadataname,metadatatype,metadatahtml)

def addmetadata(listingurl,metadatauri,metadataname,metadatatype,metadatahtml):
	query1 = "REPLACE INTO deals_metadata (metadatauri,metadataname,metadatatype,metadatahtml) VALUES (%s,%s,%s,%s)"
	cursor.execute(query1,(metadatauri,metadataname,metadatatype,metadatahtml))
	db.commit()

	query2 = "REPLACE INTO deals_listingmetadata (listingurl,metadatauri) VALUES (%s,%s)"
	cursor.execute(query2,(listingurl,metadatauri))
	db.commit()

def extractmetadataname(metadatatype,metadatahtml):
	matches = ()
	pattern = ''
	if metadatatype == 'tag':
	    pattern = "<title>(.+?)(?: Deals &amp; Coupons|: Deals, Coupons and Vouchers) \- OzBargain<\/title>"
	elif metadatatype == 'brand':
	    pattern = "<title>(.+?) Products \- Deals, Coupons &amp; Reviews \- OzBargain<\/title>"
	elif metadatatype == 'product':
	    pattern = "<title>(.+?) Deals &amp; Reviews \- OzBargain<\/title>"
	elif metadatatype == 'cat':
	    pattern = "<title>(.+?)\:  Deals and Coupons \- OzBargain<\/title>"

	metadataname = ''
	if pattern != '':
		matches = re.findall(r'%s' % pattern, metadatahtml)
		if matches is not None and len(matches) > 0:
			metadataname = matches[0]
		else:
			matches2 = re.findall(r'<title>(.+?)\- OzBargain<\/title>', metadatahtml)
			metadataname = matches2[0] 

		metadataname = metadataname.strip()
		metadataname = re.sub(r'&amp;',r'&',metadataname).strip()
		metadataname = re.sub(r'&#039;',r"'",metadataname).strip()

	return metadataname

rooturl = "https://www.ozbargain.com.au"
pageno = 0

mostrecentlistingdate = fetchmostrecent()

continuescrape = 1
while continuescrape == 1:
	searchurl = rooturl + "/deals?page=" + str(pageno)
	randagent = random.choice(useragents)
	headers = {'User-Agent': randagent}
	searchpage = requests.get(searchurl, headers=headers, timeout=10)
	if searchpage.status_code != 404:
		soup = bs4.BeautifulSoup(searchpage.text, 'html.parser')
		content = soup.find('div',{'id':'main','class':'main'})
		items = content.find_all_next('div',{'class':'n-right'})

		for item in items:
			titleandlistingraw = item.find('h2')
			listingtitle = titleandlistingraw.get('data-title', '')
			listingraw = titleandlistingraw.find('a')

			if listingraw is not None:
				listinglink = listingraw.get('href', '')
				listinglink = rooturl + listinglink
				listingurlresolved, listinghtml = downloadhtml(listinglink)

				if listinghtml != '':

					userraw = item.find('div',{'class':'submitted'})
					userlinkraw = userraw.find('a',{'title':'View user profile.'})
					if userlinkraw is not None:
						userlink = userlinkraw.get('href', '')
						userlink = rooturl + userlink

						sourceraw = userraw.find('span',{'class':'via'}).find('a',{'rel':'noopener nofollow'})
						sourcelink = sourceraw.get('href', '')
						sourcename = sourceraw.getText()
						sourcelink = rooturl + sourcelink

						userraw.find('strong').decompose()
						for span in userraw.findAll("span"):
							span.decompose()
						
						producturl, producthtml = downloadhtml(sourcelink)
						if producturl != '':
							listingdate = re.sub(' on ','', userraw.getText()).strip()
							listingdate = re.sub(' - ',' ', listingdate).strip()
							listingdate = re.sub(r'(\:\d\d)+?', r"\1", listingdate)
							listingdate = re.sub(r'(\d\d)\/(\d\d)\/(\d\d\d\d) (\d\d)\:(\d\d)', r"\3-\2-\1 \4:\5", listingdate)
							listingdate += ':00'

							print("listingdate: %s" % listingdate)
							print("listingtitle: %s" % listingtitle)
							print("listinglink: %s" % listinglink)
							print("userlink: %s" % userlink)
							print("sourcename: %s" % sourcename)
							print("sourcelink: %s" % sourcelink)
							print("productlink: %s" % producturl)

							savelisting(listinglink,listingdate,listingtitle,listinghtml,userlink,sourcename,sourcelink)

							status = 'IS-NEW'
							listingdateobj = datetime.datetime.strptime(listingdate, '%Y-%m-%d %H:%M:%S')
							#if listingdateobj < mostrecentlistingdate:
							#	status = "ALREADY-EXISTS"
							#	continuescrape = 0
							#else:
							extractandsavemetadata(listinglink,listinghtml)
								#saveproductpage(producturl,producthtml,sourcelink)

							print("status: %s" % status)						
						else:
							print("error - unable to locate productpage for [%s]" % (listinglink))	
					else:
						print("error - unable to locate user for [%s]" % (listinglink))
				else:
					print("error - unable to fetch listing html for [%s]" % (listinglink))

				print('-------------------------------------------------')
				
		pageno = pageno + 1
	else:
		continuescrape = 0

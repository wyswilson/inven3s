from flask import Flask, render_template, json, request, jsonify
import simplejson as json
import requests
import mysql.connector as mysql
import re
from bs4 import BeautifulSoup
from datetime import datetime
import random
import Levenshtein as lev
import os
import urllib
import hashlib
import logging

logging.basicConfig(filename='inven3s.log',level=logging.DEBUG)

db = mysql.connect(
	host = "inven3sdb.ciphd8suvvza.ap-southeast-1.rds.amazonaws.com",
	port = '3363',
	user = "inven3suser", passwd = "P?a&N$3!s", database='inven3s')
cursor = db.cursor()

useragents = [
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

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
		soup = BeautifulSoup(searchpage.text, 'html.parser')
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

							print("listingdate: %s" % listingdate)
							print("listingtitle: %s" % listingtitle)
							print("listinglink: %s" % listinglink)
							print("userlink: %s" % userlink)
							print("sourcename: %s" % sourcename)
							print("sourcelink: %s" % sourcelink)
							print("productlink: %s" % producturl)

							savelisting(listinglink,listingdate,listingtitle,listinghtml,userlink,sourcename,sourcelink)

							status = 'IS-NEW'
							listingdateobj = datetime.strptime(listingdate, '%Y-%m-%d %H:%M')
							if listingdateobj < mostrecentlistingdate:
								status = "ALREADY-EXISTS"
								continuescrape = 0
							else:
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

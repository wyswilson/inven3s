import datetime
import flask

import func
import time
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
import string
import math
from PIL import Image

config = configparser.ConfigParser()
config.read('conf.ini')

apisecretkey	= config['auth']['secretkey']
logfile 		= config['path']['log']
productdir 		= config['path']['products']
imagepath 		= config['path']['images']
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
	user = mysqluser, passwd = mysqlpassword, database=mysqldb,
    pool_name='sqlpool',
    pool_size = 6, pool_reset_session = True
   	)

cursor = db.cursor()

engine = "google"
type = "productprice"

query1 = """
	SELECT 
		p.gtin,
		p.productname,
		pc.candidateurl,
		pc.candidaterank,
		COUNT(*) 
	FROM products AS p
	LEFT JOIN inventories AS i
	ON p.gtin = i.gtin
	LEFT JOIN productscandidate AS pc
	ON p.gtin = pc.gtin AND pc.`type` = 'productprice'
	WHERE pc.candidateurl IS NULL 
	GROUP BY 1,2,3,4
	ORDER BY 5 DESC
"""
cursor.execute(query1)
records = cursor.fetchall()
for record in records:
	gtin = record[0]
	productname = record[1]

	url = "https://www.google.com/search?q=%s" % productname
	html,urlresolved = func.fetchhtml(url)
	soup = bs4.BeautifulSoup(html, 'html.parser')
	results = soup.find_all('div',{'class':'g'})#previously class="r"

	i = 1
	for result in results:
		listhead = result.find('h3')
		if listhead:
			resulttitle = listhead.text
		resultlink  = result.find('a').get('href', '')
				
		print('[%s] [%s] [%s]' % (gtin,productname,resultlink))
		func.addproductcandidate(type,engine,gtin,resulttitle,resultlink,i)
		i += 1

	time.sleep(5)
import datetime
import flask

import func
import time
import functools
import mysql.connector
import hashlib
import urllib
import urllib.parse
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
	user = mysqluser, passwd = mysqlpassword, database=mysqldb
   	)

query1 = """
SELECT
	*
FROM(
	SELECT
		p.gtin,
		p.productname,
		DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','+10:00'), "%Y-%m-%d") AS todaydate,
		MAX(pp.date) AS mostrecentpricedate,
		COUNT(DISTINCT(pp.retailer)) AS retailerswithpricecnt,
		GROUP_CONCAT(distinct pp.retailer SEPARATOR '; ') as retailerswithprice,	
		GROUP_CONCAT(distinct pc.candidateurl ORDER BY pc.candidaterank ASC SEPARATOR '; ') as retailerpricepages,
		AVG(pp.price) AS avgprice,		
		COUNT(DISTINCT(case when pp.date < DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','+10:00'), "%Y-%m-%d") then pp.date ELSE null END)) AS previousprices,
		COUNT(DISTINCT(case when pp.date = DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','+10:00'), "%Y-%m-%d") then pp.date ELSE null END)) AS todayprice,
		COUNT(distinct(i.entryid)) AS inventoryentries
	FROM products AS p
	LEFT JOIN inventories AS i
	ON p.gtin = i.gtin
	LEFT JOIN productsprice AS pp
	ON p.gtin = pp.gtin
	LEFT JOIN productscandidate AS pc
	ON p.gtin = pc.gtin AND pc.`type` = 'productprice'
	GROUP BY 1,2,3
	ORDER BY 11 DESC
) AS tmp
WHERE todayprice = 0
ORDER BY inventoryentries DESC
"""
cursor = func._execute(db,query1,None)
records = cursor.fetchall()
cursor.close()

for record in records:
	gtin 				= record[0]
	productname			= record[1]
	sourceurls     		= record[6]

	print("[%s][%s]" % (gtin,productname))

	if not sourceurls:
		sourceurls = ''		
	elif not ";" in sourceurls: 
		sourceurls = sourceurls + "; "
	
	for url in sourceurls.split("; "):
		matchobj = re.findall('([^\.\/]+)\.(?:com|net)', url, re.IGNORECASE)
		if matchobj:
			retailer = matchobj[0]

			price = func.pricescrape(url,retailer)
			print("\t[%s][%s]" % (retailer,price))
			if price > 0:
				timestamp 	= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
				date 		= datetime.datetime.today().strftime('%Y-%m-%d')
				query1 = "REPLACE INTO productsprice (gtin,price,timestamp,date,retailer) VALUES (%s,%s,%s,%s,%s)"
				cursor = func._execute(db,query1,(gtin,price,timestamp,date,retailer))
				db.commit()			
				cursor.close()

	time.sleep(5)

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

def pricescraper_coles(gtin,productname):
	price = 0
	source = "Coles"
	status = ""

	url = "https://api.coles.com.au/customer/v1/coles/products/search?limit=3&q=%s&storeId=7716&type=SKU" % (productname)
	header = {
	'Accept-Encoding': 'gzip'
	,'Connection': 'keep-alive'
	,'Accept': '*/*' 
	,'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
	,'X-Coles-API-Key': '046bc0d4-3854-481f-80dc-85f9e846503d'
	,'X-Coles-API-Secret': 'e6ab96ff-453b-45ba-a2be-ae8d7c12cadf'
	,'Accept-Language': 'en-AU;q=1'
	}#FROM https://github.com/adambadge/coles-scraper/blob/master/coles.ipynb

	response = requests.get(url, headers=header)
	status = response.status_code

	if status == 200:
		json = response.json()
		results = json['Results']
		if results:
			promo = results[0]['Promotions']
			if promo:
				price = promo[0]['Price']
			else:
				status = 204
		else:
			status = 204
	else:
		errstr = "coles error: [%s] [%s]" % (status,response.reason)
		print(errstr)
		logging.debug(errstr)	

	return price,source,status

def pricescraper_bigw(gtin,productname):
	price = 0
	source = "Big W"
	status = ""

	searchurl = "https://www.bigw.com.au/search/?text=" + gtin
	randagent = random.choice(useragents)
	headers = {'User-Agent': randagent}
	response = requests.get(searchurl, headers=headers)
	status = response.status_code

	if status == 200:
		html = response.content.decode('utf-8')	
		datamatch = re.findall('products_storage = (\[.+\]);', html, re.IGNORECASE)
		for data in datamatch:
			if data:
				dataobj = json.loads(data)
				price = dataobj[0]['price']
			else:
				status = 204
	else:
		errstr = "bigw error: [%s] [%s]" % (status,response.reason)
		print(errstr)
		logging.debug(errstr)

	return price,source,status

def pricescraper_woolworths(gtin,productname):
	price = 0
	source = "Woolworths"
	status = ""

	searchurl = "https://www.woolworths.com.au/apis/ui/Search/products"
	randagent = random.choice(useragents)
	headers = {'User-Agent': randagent}
	payload = {
		'Location': "/shop/search/products?searchTerm=" + productname,
		'PageNumber': 1, 
		'PageSize': 24, 
		'SearchTerm': productname,
		'SortType': "TraderRelevance"
	}
	response = requests.post(searchurl, headers=headers, data=payload)
	status = response.status_code

	if status == 200:
		respjson 	= json.loads(response.text)
		items 		= respjson['Products']
		if items:
			for item in items:
				itemobj = item['Products'][0]
				price_ 	= itemobj['Price']
				barcode = itemobj['Barcode']
				
				if gtin == barcode:
					price = price_
					status = 200
					break
				else:
					status = 204
		else:
			status = 204
	else:
		errstr = "woolworths error: [%s] [%s]" % (status,response.reason)
		print(errstr)
		logging.debug(errstr)

	return price,source,status

#url = "https://shop.coles.com.au/a/national/product/uncle-tobys-golden-syrup-quick-sachet-oats"
#url = "https://www.uncletobys.com.au/products/oats/uncle-tobys-quick-sachets/quick-sachets-golden-syrup"
#url = "https://www.woolworths.com.au/shop/productdetails/368716/uncle-tobys-oats-quick-sachets-classics-variety-porridge"
#url = "https://www.woolworths.com.au/shop/productdetails/724514/cocobella-cocobella-straight-up-coconut-water"

query1 = """
	SELECT 
		p.gtin,
		p.productname,
		DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','+10:00'), "%Y-%m-%d"),
		GROUP_CONCAT(distinct CONCAT(pp.retailer,':',pp.price) SEPARATOR ';') AS retailers,		
		COUNT(*) 
	FROM products AS p
	LEFT JOIN inventories AS i
	ON p.gtin = i.gtin
	LEFT JOIN productsprice AS pp
	ON p.gtin = pp.gtin AND pp.date = DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','+10:00'), "%Y-%m-%d")
	GROUP BY 1,2,3
	ORDER BY 5 DESC
"""
cursor.execute(query1)
records = cursor.fetchall()
for record in records:
	gtin 		= record[0]
	productname	= record[1]
	retailers    = record[3]
	if not retailers:
		retailers = ""
	timestamp 	= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
	date 		= datetime.datetime.today().strftime('%Y-%m-%d')

	print("[%s] [%s] [%s] [%s]" % (date,gtin,productname,retailers))
	
	if not re.search(r'Woolworths',retailers): 
		price,source,status = pricescraper_woolworths(gtin,productname)
		print("\t[%s] [%s] [%s]" % (source,str(price),status))
		if float(price) > 0:
			query1 = "REPLACE INTO productsprice (gtin,price,timestamp,date,retailer) VALUES (%s,%s,%s,%s,%s)"
			cursor.execute(query1,(gtin,price,timestamp,date,source))
			db.commit()	

	if not re.search(r'Big W',retailers): 
		price,source,status = pricescraper_bigw(gtin,productname)
		print("\t[%s] [%s] [%s]" % (source,str(price),status))
		if float(price) > 0:
			query1 = "REPLACE INTO productsprice (gtin,price,timestamp,date,retailer) VALUES (%s,%s,%s,%s,%s)"
			cursor.execute(query1,(gtin,price,timestamp,date,source))
			db.commit()	

	if not re.search(r'Coles',retailers): 
		price,source,status = pricescraper_coles(gtin,productname)
		print("\t[%s] [%s] [%s]" % (source,str(price),status))
		if float(price) > 0:
			query1 = "REPLACE INTO productsprice (gtin,price,timestamp,date,retailer) VALUES (%s,%s,%s,%s,%s)"
			cursor.execute(query1,(gtin,price,timestamp,date,source))
			db.commit()	

	time.sleep(5)
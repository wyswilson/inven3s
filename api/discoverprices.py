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


def pricescrape(url,retailer):
	price = '0.0'
	matchobj = ""

	html,urlresolved = func.fetchhtml(url)
	soup = bs4.BeautifulSoup(html, 'html.parser')

	if retailer == 'amcal': 
		matchobj = soup.find_all('span',{'class':'price'})

	elif retailer == 'discountchemist': 
		matchobj = soup.find_all('span',{'class':'woocommerce-Price-amount amount'})

	elif retailer == 'igashop': 
		matchobj = soup.find_all('span',{'class':'woocommerce-Price-amount amount'})

	elif retailer == 'bigw': 
		matchobj = soup.find_all('span',{'id':'product_online_price'})

	elif retailer == 'woolworths': 
		matchobj = soup.find_all('div',{'class':'price price--large'})
	
	elif retailer == 'coles': 
		matchobj = soup.find_all('span',{'class':'price-container'})

	elif retailer == 'asiangrocerystore': 
		matchobj = soup.find_all('span',{'id':'line_discounted_price_126'})

	elif retailer == 'drakes': 
		matchobj = soup.find_all('strong',{'class':'MoreInfo__Price'})

	elif retailer == 'mysweeties': 
		matchobj = soup.find_all('span',{'id':'productPrice'})

	elif retailer == 'allysbasket': 
		matchobj = soup.find_all('span',{'itemprop':'price'})

	elif retailer == 'buyasianfood': 
		matchobj = soup.find_all('span',{'class':'price'})

	elif retailer == 'chemistwarehouse': 
		matchobj = soup.find_all('span',{'class':'product__price'})

	elif retailer == 'goodpricepharmacy': 
		matchobj = soup.find_all('span',{'class':'price'})
		
	elif retailer == 'indoasiangroceries': 
		matchobj = soup.find_all('p',{'class':'price'})

	elif retailer == 'myasiangrocer': 
		matchobj = soup.find_all('span',{'class':'price'})

	elif retailer == 'pharmacydirect': 
		matchobj = soup.find_all('span',{'id':'price-display'})

	elif retailer == 'officeworks': 
		matchobj = re.findall('"edlpPrice":"(.+?)"', html, re.IGNORECASE)
	else:
		retailer = 'not-supported'

	if matchobj and retailer != 'not-supported':
		for match in matchobj:
			if type(match) == str:
				price = match
			else:
				price = match.text

			price = price.replace('\n' , '') 
			price = price.replace('Price:' , '') 
			price = price.replace('$' , '') 
			try:
				test = float(price)
			except:
				price = "0.0"
			break
	elif retailer == 'not-supported':
		errstr = "no rules defined for retailer: [%s] [%s]" % (retailer,url)
		print(errstr)
	else:
		errstr = "unknown errors [%s] [%s]" % (retailer,url)
		print(errstr)
		logging.debug(errstr)

	return float(price)

#url = "https://shop.coles.com.au/a/richmond-south/product/claratyne-childrens-grape-chew-5mg-tabs-10pk"

#url = "https://igashop.com.au/product/leggos-pesto-traditional-basil-190g/"
#url = "https://www.amcal.com.au/soov-bite-25g-p-93327381"
#url = "https://www.bigw.com.au/product/oral-b-stages-2-mickey-2-4-years-toothbrush-extra-soft/p/169614/"
#url = "https://discountchemist.com.au/product/ego-pinetarsol-solution-100ml/"
#url = "https://www.woolworths.com.au/shop/productdetails/94375/leggo-s-pesto-traditional-basil"
#url = "http://www.asiangrocerystore.com.au/lee-kum-kee-char-siu-sauce-397g.html"
#url = "https://062.drakes.com.au/lines/obento-seasoning-sushi-250ml"
#url = "https://mysweeties.com.au/products/doritos-salsa-dip-mild-300g-1-unit"
#url = "https://www.allysbasket.com/biscuits-crackers/10608-arnott-s-premier-cookies-chocolate-chip-310g.html"
#url = "https://www.buyasianfood.com.au/_products/NoodlesPasta/JapaneseKoreanNoodles/HakubakuOrganicUdonNoodles270G-25-35-.aspx"
#url = "https://www.chemistwarehouse.com.au/buy/89956/grants-of-australia-toothpaste-propolis-with-mint-110g-online-only"
#url = "https://www.goodpricepharmacy.com.au/palmolive-foam-hand-wash-antibacterial-lime-250ml"
#url = "https://www.indoasiangroceries.com.au/lee-kum-kee-premium-dark-soy-sauce-500-ml"
#url = "https://www.myasiangrocer.com.au/ajishima-nori-komi-furikake-rice-seasoning-50g/"
#url = "https://www.officeworks.com.au/shop/officeworks/p/glen-20-disinfectant-300g-lavender-le0357053"
#url = "https://www.pharmacydirect.com.au/dermeze-treatment-cream-500g"

query1 = """
	SELECT 
		p.gtin,
		p.productname,
		DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','+10:00'), "%Y-%m-%d"),
		GROUP_CONCAT(distinct pc.candidateurl ORDER BY pc.candidaterank ASC SEPARATOR '; ') as pricesourceurls,
		GROUP_CONCAT(distinct pp.retailer SEPARATOR '; ') as priceretailers,		
		COUNT(*) 
	FROM products AS p
	LEFT JOIN inventories AS i
	ON p.gtin = i.gtin
	LEFT JOIN productsprice AS pp
	ON p.gtin = pp.gtin AND pp.date = DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','+10:00'), "%Y-%m-%d")
	LEFT JOIN productscandidate AS pc
	ON p.gtin = pc.gtin AND pc.`type` = 'productprice'
	GROUP BY 1,2,3
	ORDER BY 6 DESC, 1 ASC
"""
cursor.execute(query1)
records = cursor.fetchall()

for record in records:
	gtin 			= record[0]
	productname		= record[1]
	date         	= record[2]
	sourceurls     	= record[3]
	retailerswithprice = record[4]
	if not retailerswithprice:
		retailerswithprice = ''
	if not ";" in sourceurls and sourceurls != '':
		sourceurls = sourceurls + "; "


	processedretailers = {}
	if ";" in retailerswithprice:
		for retailer in retailerswithprice.split("; "):
			processedretailers[retailer] = ''
	elif retailerswithprice != '':
		processedretailers[retailerswithprice] = ''

	for url in sourceurls.split("; "):
		matchobj = re.findall('([^\.\/]+)\.com', url, re.IGNORECASE)
		if matchobj:
			retailer = matchobj[0]

			if not any(retailer in key for key in processedretailers):
				price = pricescrape(url,retailer)
				print("[%s][%s]" % (retailer,price))
				if float(price) > 0:
					timestamp 	= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
					date 		= datetime.datetime.today().strftime('%Y-%m-%d')
					query1 = "REPLACE INTO productsprice (gtin,price,timestamp,date,retailer) VALUES (%s,%s,%s,%s,%s)"
					cursor.execute(query1,(gtin,price,timestamp,date,retailer))
					db.commit()	
				else:
					print("no price detected [%s][%s]" % (retailer,price))		
			else:
				print("price from retailer already exists [%s]" % (retailer))		

			processedretailers[retailer] = ''
		
	time.sleep(5)

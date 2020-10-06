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


def pricescrape(url):
	price = '0.0'
	retailer = ''
	matchobj = ""

	html,urlresolved = func.fetchhtml(url)
	soup = bs4.BeautifulSoup(html, 'html.parser')

	if re.search(r'amcal\.com\.au',url): 
		retailer = 'amcal'
		matchobj = soup.find_all('span',{'class':'price'})

	elif re.search(r'discountchemist\.com\.au',url): 
		retailer = 'discountchemist'
		matchobj = soup.find_all('span',{'class':'woocommerce-Price-amount amount'})

	elif re.search(r'igashop\.com\.au',url): 
		retailer = 'iga'
		matchobj = soup.find_all('span',{'class':'woocommerce-Price-amount amount'})

	elif re.search(r'bigw\.com\.au',url): 
		retailer = 'bigw'
		matchobj = soup.find_all('span',{'id':'product_online_price'})

	elif re.search(r'woolworths\.com\.au',url): 
		retailer = 'woolworths'
		matchobj = soup.find_all('div',{'class':'price price--large'})
	
	elif re.search(r'coles\.com\.au',url): 
		retailer = 'coles'
		matchobj = soup.find_all('span',{'class':'price-container'})

	elif re.search(r'asiangrocerystore\.com\.au',url): 
		retailer = 'asiangrocerystore'
		matchobj = soup.find_all('span',{'id':'line_discounted_price_126'})

	elif re.search(r'drakes\.com\.au',url): 
		retailer = 'drakes'
		matchobj = soup.find_all('strong',{'class':'MoreInfo__Price'})

	elif re.search(r'mysweeties\.com\.au',url): 
		retailer = 'mysweeties'
		matchobj = soup.find_all('span',{'id':'productPrice'})

	elif re.search(r'allysbasket\.com',url): 
		retailer = 'allysbasket'
		matchobj = soup.find_all('span',{'itemprop':'price'})

	elif re.search(r'buyasianfood\.com\.au',url): 
		retailer = 'buyasianfood'
		matchobj = soup.find_all('span',{'class':'price'})

	elif re.search(r'chemistwarehouse\.com\.au',url): 
		retailer = 'chemistwarehouse'
		matchobj = soup.find_all('span',{'class':'product__price'})

	elif re.search(r'goodpricepharmacy\.com\.au',url): 
		retailer = 'goodpricepharmacy'
		matchobj = soup.find_all('span',{'class':'price'})
		
	elif re.search(r'indoasiangroceries\.com\.au',url): 
		retailer = 'indoasiangroceries'
		matchobj = soup.find_all('p',{'class':'price'})

	elif re.search(r'myasiangrocer\.com\.au',url): 
		retailer = 'myasiangrocer'
		matchobj = soup.find_all('span',{'class':'price'})

	elif re.search(r'pharmacydirect\.com\.au',url): 
		retailer = 'pharmacydirect'
		matchobj = soup.find_all('span',{'id':'price-display'})

	elif re.search(r'officeworks\.com\.au',url): 
		retailer = 'officeworks'
		matchobj = re.findall('"edlpPrice":"(.+?)"', html, re.IGNORECASE)


	if matchobj and retailer != '':
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
	elif retailer == '':
		retailer = 'not-supported'
		errstr = "price-scraper-norules: [%s] [%s]" % (retailer,url)
		print(errstr)
	else:
		errstr = "price-scraper-err: [%s] [%s]" % (retailer,url)
		print(errstr)
		logging.debug(errstr)

	return float(price),retailer

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
		GROUP_CONCAT(distinct pc.candidateurl ORDER BY pc.candidaterank ASC SEPARATOR '; ') as priceurls,
		COUNT(*) 
	FROM products AS p
	LEFT JOIN inventories AS i
	ON p.gtin = i.gtin
	LEFT JOIN productsprice AS pp
	ON p.gtin = pp.gtin AND pp.date = DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','+10:00'), "%Y-%m-%d")
	LEFT JOIN productscandidate AS pc
	ON p.gtin = pc.gtin AND pc.`type` = 'productprice'
	GROUP BY 1,2,3
	ORDER BY 5 DESC, 1 ASC
"""
cursor.execute(query1)
records = cursor.fetchall()

for record in records:
	gtin 			= record[0]
	productname		= record[1]
	date         	= record[2]
	urls         	= record[3]

	processedretailers = {}
	for url in urls.split("; "):
		price,retailer = pricescrape(url)
		print("[%s][%s]" % (retailer,price))
		if float(price) > 0 and not any(retailer in key for key in processedretailers):
			timestamp 	= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
			date 		= datetime.datetime.today().strftime('%Y-%m-%d')
			query1 = "REPLACE INTO productsprice (gtin,price,timestamp,date,retailer) VALUES (%s,%s,%s,%s,%s)"
			cursor.execute(query1,(gtin,price,timestamp,date,retailer))
			db.commit()	
		elif float(price) == 0:
			print("no price detected [%s][%s]" % (retailer,price))		
		else:
			print("price from retailer already exists [%s][%s]" % (retailer,price))		

		processedretailers[retailer] = ''

	time.sleep(5)

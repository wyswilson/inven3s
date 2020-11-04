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
	user = mysqluser, passwd = mysqlpassword, database=mysqldb,
    pool_name='sqlpool',
    pool_size = 6, pool_reset_session = True
   	)

cursor = db.cursor()

#url = "https://shop.coles.com.au/a/richmond-south/product/claratyne-childrens-grape-chew-5mg-tabs-10pk"
#url = "https://www.priceline.com.au/dermeze-moisturising-soap-free-wash-1-litre"

#url = "https://igashop.com.au/product/leggos-pesto-traditional-basil-190g/"
#url = "https://www.amcal.com.au/soov-bite-25g-p-93327381"
#url = "https://www.bigw.com.au/product/oral-b-stages-2-mickey-2-4-years-toothbrush-extra-soft/p/169614/"
#url = "https://discountchemist.com.au/product/ego-pinetarsol-solution-100ml/"
url = "https://www.woolworths.com.au/shop/productdetails/94375/leggo-s-pesto-traditional-basil"
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
#url = "http://www.cincottachemist.com.au/optifast-vlcd-bars-chocolate-70g-x-6-pack"
#url = "http://yahwehasiangrocery.com.au/hakubaku-organic-somen-noodle-270g/"
#url = "https://asianpantry.com.au/products/snazk-bites-salted-egg-golden-cube-100g"
#url = "https://g2.net.au/products/copy-of-oreo-wafer-bites-chocolate-47g?variant=31583684821041"
#url = "https://groceryasia.com.au/product/action-one-a1-instant-curry-paste-for-indian-seafood-curry-230g/"
#url = "https://hongyi.com.au/products/hai-di-lao-seasoning-for-fish-sauce-with-sauerkraut-360g"
#url = "https://iganathalia.com.au/lines/huggies-toddlr-boy-jmbo-u-d72s"
#url = "https://yinyam.com.au/products/snazk-bites-salted-egg-spicy-golden-cube-100g"
#url = "https://www.yourdiscountchemist.com.au/macleans-little-teeth-4-6-years-toothbrush.html"
#url = "https://www.winc.com.au/main-catalogue-productdetail/moccona-classic-medium-roast-instant-coffee-400g-jar/86877597"
#url = "https://www.theiconic.com.au/peptide-anti-ageing-elixir-787773.html"
#url = "https://www.tastefuldelights.com.au/au/sauces-and-condiments/735972-masterfoods-dijonnaise-mustard-squeezy-250gm.html"
#url = "https://www.superpharmacy.com.au/products/panadol-optizorb-100-tablets"
#url = "https://www.savourofasia.com.au/products/royal-family-mochi-bubble-tea-milk-120g"
#url = "https://www.pharmacyonline.com.au/lucas-papaw-ointment-25g"
#url = "https://maizo.com.au/product/3:15pm-brown-sugar-jelly-bubble-milk-tea-3-x-80g"
#url = "https://shop.lynwood.igamarket.com.au/lines/5c9c6b90e1272f5b45039276"
#url = "https://www.harrisfarm.com.au/products/nutella-hazelnut-spread-with-cocoa-400g"
#url = "https://www.chempro.com.au/Libra-Extra-Regular-Wings-14-Pack"
#url = "https://epharmacy.com.au/buy/86991/huggies-ultra-dry-nappy-pants-size-5-12-17kg-boy-26-pack"
#url = " https://ilovehealth.com.au/products/comvita-propolis-extract-alcohol-free-25ml"
#url = "https://natonic.com.au/en/comvita-propolis-extract-alcohol-free-25ml"
#url = "https://www.fgb.com.au/product/bosistos-native-breathe-oil"
#url = " https://www.davidjonespharmacy.com.au/voost-vitamin-c-1000mg-effervescent-20-tablets"
#url = "https://www.aircart.com.au/product-page/sanitarium-weet-bix-bites-apricot-breakfast-cereal-500g"
#url = " https://www.intradco.com.au/product/chan-kong-thye-bulldog-black-vinegargongtaijiangyuan-gouzi-zhengnuomitianheicu/"
#url = "https://www.myer.com.au/p/cleansing-facial-scrub-472720150-472723210"

def showmainretailers():
	retailers = {}
	query1 = """
	SELECT
		candidateurl
	FROM productscandidate
	WHERE type = 'productprice'
	"""
	cursor.execute(query1)
	records = cursor.fetchall()
	for record in records:
		candidateurl = record[0]
		matchobj = re.findall('([^\.\/]+)\.(?:com|net)', candidateurl, re.IGNORECASE)
		if matchobj:
			retailer = matchobj[0]

			if retailer in retailers:
				retailers[retailer] += 1
			else:
				retailers[retailer] = 1

	data_sorted = {k: v for k, v in sorted(retailers.items(), key=lambda x: x[1])}

	for retailer in data_sorted:
		count = retailers[retailer]
		print("[%s][%s]" % (retailer,count))


def scrapeproductprice():
	matchobj = re.findall('([^\.\/]+)\.(?:com|net)', url, re.IGNORECASE)
	if matchobj:
		retailer = matchobj[0]
		price = func.pricescrape(url,retailer)
		print("[%s][%s]" % (retailer,price))

showmainretailers()
#scrapeproductprice()
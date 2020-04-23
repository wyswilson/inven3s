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
	user = "inven3suser", passwd = "pan3spwd", database='inven3s')
cursor = db.cursor(buffered=True)

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

imageroot = "http://127.0.0.1:5000/products"

template_dir = os.path.abspath('c:/dev/templates')
app = Flask(__name__,static_url_path='',static_folder=template_dir,template_folder=template_dir)

def addproductcandidate(source,gtin,title,url,rank):
    id = hashlib.md5(title.encode('utf-8')).hexdigest()
    query1 = "REPLACE INTO productcandidates (gtin,source,candidateid,candidatetitle,candidateurl,candidaterank) VALUES (%s,%s,%s,%s,%s,%s)"
    #cursor.execute(query1,(gtin,source,id,title,url,rank))
    #db.commit()
    
def discoverproductnamebygtin(gtin):
	engine  = "google"
	url     = ""
	if engine == 'google':
		url = "https://www.google.com/search?q=%s" % gtin
	elif engine == 'bing':
		url = "https://www.bing.com/search?q=%s" % gtin

	productnamesuggest = ''
	try:
		randagent = random.choice(useragents)
		headers = {'User-Agent': randagent}
		r = requests.get(url, headers=headers, timeout=10)
		urlresolved = r.url
		html = r.content

		soup = BeautifulSoup(html, 'html.parser')
		if engine == 'google':
			results = soup.find_all('div',{'class':'r'})
		elif engine == 'bing':
			results = soup.find_all('li',{'class':'b_algo'})
		i = 1
		for result in results:
			resulttitle = ""
			resultlink = ""
			if engine == 'google':
				resulttitle = result.find('h3').text
				resultlink  = result.find('a').get('href', '')
			elif engine == 'bing':
				resulttitle = result.find('a').text
				resultlink  = result.find('a').get('href', '')

			if i == 1 and resulttitle != '':
				productnamesuggest = resulttitle

			addproductcandidate(engine,gtin,resulttitle,resultlink,i)
			i += 1
	except requests.ConnectionError as e:
		logging.debug("internet connection error for [%s] [%s]" % (url,str(e)))
	except requests.Timeout as e:
		logging.debug("timeout error for [%s] [%s]" % (url,str(e)))
	except requests.RequestException as e:
		logging.debug("general error for [%s] [%s]" % (url,str(e)))

	return productnamesuggest

def lookupproductbygtin(gtin):
	query = """
		SELECT
			p.gtin,p.productname,b.brandname,p.perishable,p.edible,count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		WHERE p.gtin = %s
		GROUP by 1,2,3,4,5
	"""
	cursor.execute(query,(gtin,))
	records = cursor.fetchall()

	return records

def jsonifybrands(records):
	brands = []
	for record in records:
		brandid	  		= record[0]
		brandname  		= record[1]
		brandowner   	= record[2]
		productcount	= record[3]

		brand = {}
		brand['brandid'] 		= brandid
		brand['brandname']		= brandname
		brand['brandowner'] 	= brandowner
		brand['productcount'] 	= productcount

		brands.append(brand)

	return brands

def jsonifyproducts(records):
	products = []
	for record in records:
		gtin	  		= record[0]
		productname  	= record[1]
		brandname   	= record[2]
		isperishable   	= record[3]
		isedible	   	= record[4]
		productimage 	= imageroot + '/' + gtin + '.jpg'

		product = {}
		product['gtin'] 			= gtin
		product['productname']		= productname
		product['productimage'] 	= productimage
		product['brandname'] 		= brandname
		product['isperishable'] 	= isperishable
		product['isedible'] 		= isedible

		products.append(product)

	return products

def jsonifyinventory(records):
	inventory = []
	for record in records:
		gtin	  		= record[0]
		productname  	= record[1]
		brandname   	= record[2]
		dateexpiry   	= record[3]
		itemcount		= record[4]
		productimage 	= imageroot + '/' + gtin + '.jpg'

		itemgroup = {}
		itemgroup['gtin'] 			= gtin
		itemgroup['productname']	= productname
		itemgroup['productimage'] 	= productimage
		itemgroup['brandname'] 		= brandname
		itemgroup['dateexpiry'] 	= dateexpiry
		itemgroup['itemcount'] 		= itemcount

		inventory.append(itemgroup)

	return inventory

def jsonifymessage(messagetext):
	messages = []
	message = {}
	message['message'] = messagetext
	messages.append(message)

	return messages

@app.route("/")
def main():
	return jsonify(jsonifymessage("error, provide a valid endpoint")), '200'

@app.route('/product', methods=['POST'])
def product_add():
	gtin = request.args.get("gtin")
	productname = request.args.get("productname")

	if gtin is None or gtin == '':
		return jsonify(jsonifymessage("error, provide a gtin")), '200'
	else:
		query1 = """
	    	SELECT
	        *
	    	FROM products
	    	WHERE gtin = %s
		"""
		cursor.execute(query1,(gtin,))
		if cursor.rowcount > 0:
			productname = productname.strip()
			if productname != '':
				query2 = "UPDATE products SET productname = %s WHERE gtin = %s"
				cursor.execute(query2,(productname,gtin))
				db.commit()
			else:
				return jsonify(jsonifymessage("error, empty product name detected")), '200'

			records = lookupproductbygtin(gtin)
			return jsonify(jsonifyproducts(records)), '200'
		else:
			productnamesuggest = discoverproductnamebygtin(gtin)
			return jsonify(jsonifymessage("product name suggestion [%s]" % productnamesuggest)), '200'

@app.route('/product/<gtin>', methods=['GET'])
@app.route('/product/', methods=['GET'])
@app.route('/product', methods=['GET'])
def product_fetch(gtin=None):
	records = []
	if gtin is None:
		query = """
			SELECT
				p.gtin,p.productname,b.brandname,p.perishable,p.edible,count(*)
			FROM products AS p
			JOIN brands AS b
			ON p.brandid = b.brandid
			GROUP BY 1,2,3,4,5
		"""
		cursor.execute(query)
		records = cursor.fetchall()
	else:
		records = lookupproductbygtin(gtin)

		if not records:
			query1 = """
				SELECT
					p.gtin,p.productname,b.brandname,p.perishable,p.edible,count(*)
				FROM products AS p
				JOIN brands AS b
				ON p.brandid = b.brandid
				WHERE p.productname LIKE %s
				GROUP BY 1,2,3,4,5
			"""
			cursor.execute(query1,("%" + gtin + "%",))
			records = cursor.fetchall()
	if records:
		return jsonify(jsonifyproducts(records)), '200'
	else:
		return jsonify(jsonifymessage("error, product does not exists")), '200'

@app.route('/brand/<brandid>', methods=['GET'])
@app.route('/brand/', methods=['GET'])
@app.route('/brand', methods=['GET'])
def brand_fetch(brandid=None):
	records = []
	if brandid is None:
		query = """
			SELECT
				b.brandid, b.brandname, b.brandowner, count(distinct(p.gtin))
			FROM brands AS b
			LEFT JOIN products as p
			ON b.brandid = p.brandid
			GROUP BY 1,2,3
		"""
		cursor.execute(query)
		records = cursor.fetchall()
	else:
		query = """
			SELECT
				b.brandid, b.brandname, b.brandowner, count(distinct(p.gtin))
			FROM brands AS b
			LEFT JOIN products as p
			ON b.brandid = p.brandid
			WHERE b.brandid = %s
			GROUP BY 1,2,3
		"""
		cursor.execute(query,(brandid,))
		records = cursor.fetchall()
		if not records:
			query1 = """
				SELECT
					b.brandid, b.brandname, b.brandowner, count(distinct(p.gtin))
				FROM brands AS b
				LEFT JOIN products as p
				ON b.brandid = p.brandid
				WHERE b.brandname LIKE %s
				GROUP BY 1,2,3
			"""
			cursor.execute(query1,("%" + brandid + "%",))
			records = cursor.fetchall()

	if records:
		return jsonify(jsonifybrands(records)), '200'
	else:
		return jsonify(jsonifymessage("error, brand does not exists")), '200'

@app.route('/inventory/<uid>', methods=['GET'])
@app.route("/inventory/", methods=['GET'])
@app.route("/inventory", methods=['GET'])
def inventory_fetch(uid=None):
	if uid is None:
		return jsonify(jsonifymessage("error, provide a user id")), '200'
	else:
		query = """
			SELECT
				i.gtin,p.productname,b.brandname,i.dateexpiry,sum(i.quantity) AS itemcount
			FROM inventory AS i
			JOIN products AS p
			ON i.gtin = p.gtin
			JOIN brands AS b
			ON p.brandid = b.brandid
			WHERE i.userid = %s
			GROUP BY 1,2,3,4
		"""
		cursor.execute(query,(uid,))
		records = cursor.fetchall()

		if records:
			return jsonify(jsonifyinventory(records)), '200'
		else:
			return jsonify(jsonifymessage("error, user does not exists")), '200'

if __name__ == "__main__":
	app.run(debug=True)

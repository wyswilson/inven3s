from flask import Flask, render_template, json, request, jsonify
import simplejson as json
import requests
import mysql.connector as mysql
import re
from bs4 import BeautifulSoup
from datetime import datetime
import random
import os
import urllib
import hashlib
import logging
from functools import wraps

mysqlhost = "inven3sdb.ciphd8suvvza.ap-southeast-1.rds.amazonaws.com"
mysqlport = "3363"
mysqluser = "inven3suser"
mysqlpwrd = "P?a&N$3!s"
mysqldb = "inven3s"
apiuser = "inven3sapiuser"
apipwrd = "N0tS3cUr3!"
flasktemplatedir = "c:/dev/templates"
logfile = "inven3s.log"
emptybrandid = "N_000000"
emptybrandname = "Unavailable"

logging.basicConfig(filename=logfile,level=logging.DEBUG)
db = mysql.connect(
	host = mysqlhost,
	port = mysqlport,
	user = mysqluser, passwd = mysqlpwrd, database=mysqldb)
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

imageroot = "http://127.0.0.1:5000/products"

template_dir = os.path.abspath(flasktemplatedir)
app = Flask(__name__,static_url_path='',static_folder=template_dir,template_folder=template_dir)
app.config['JSON_SORT_KEYS'] = False

def check_auth(username, password):
    return username == apiuser and password == apipwrd

def authenticate():
    message = {'message': "authentication required"}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth: 
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

def addproductcandidate(source,gtin,title,url,rank):
    id = hashlib.md5(title.encode('utf-8')).hexdigest()
    query1 = "REPLACE INTO productcandidates (gtin,source,candidateid,candidatetitle,candidateurl,candidaterank) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(query1,(gtin,source,id,title,url,rank))
    db.commit()

def addnewbrand(brandid,brandname,brandowner,brandimage,brandurl):
	query2 = "REPLACE INTO brands (brandid,brandname,brandowner,brandimage,brandurl) VALUES (%s,%s,%s,%s,%s)"
	cursor.execute(query2,(brandid,brandname.title(),brandowner.title(),brandimage,brandurl))
	db.commit()

	return brandid

def addnewproduct(gtin,productname,productimage,brandid,isperishable,isedible):
	if productname != "":#and brandid != ""
		query2 = "INSERT INTO products (gtin,productname,productimage,brandid,isperishable,isedible) VALUES (%s,%s,%s,%s,%s,%s)"
		cursor.execute(query2,(gtin,productname.title(),productimage,brandid,isperishable,isedible))
		db.commit()

	return gtin

def downloadproductpages(gtin,engine,preferredsources):
	if engine == 'google':
		url = "https://www.google.com/search?q=%s" % gtin
	elif engine == 'bing':
		url = "https://www.bing.com/search?q=%s" % gtin

	try:
		selectedhtml = ""
		selectedurl = ""
		selectedtitle = ""
		firsturl = ""
		firsttitle = ""

		randagent = random.choice(useragents)
		headers = {'User-Agent': randagent}
		r = requests.get(url, headers=headers, timeout=10)
		urlresolved = r.url
		html = r.content
		logging.debug("webcrawl: [%s] [%s] [%s]" % (gtin,engine,urlresolved))

		soup = BeautifulSoup(html, 'html.parser')
		results = []
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

			logging.debug("webcrawl: found [%s] [%s]" % (resulttitle,resultlink))

			for preferredsrc in preferredsources:
				if preferredsrc in resultlink:
					selectedurl = resultlink
					selectedtitle = resulttitle

			if i == 1:
				firsturl = resultlink
				firsttitle = resulttitle

			addproductcandidate(engine,gtin,resulttitle,resultlink,i)
			i += 1

		if selectedurl == "":
			selectedurl = firsturl
			selectedtitle = firsttitle

		return selectedurl,selectedtitle

	except requests.ConnectionError as e:
		logging.debug("error: internet connection for [%s] [%s]" % (url,str(e)))
	except requests.Timeout as e:
		logging.debug("error: timeout for [%s] [%s]" % (url,str(e)))
	except requests.RequestException as e:
		logging.debug("error: [%s] [%s]" % (url,str(e)))

	return "ERR",""

def resolvebrand(brandname):
	query1 = """
    	SELECT
        	brandid, brandname, brandowner
    	FROM brands
    	WHERE lower(brandname) = %s
	"""
	cursor.execute(query1,(brandname.lower(),))
	records = cursor.fetchall()
	if records:
		brandid = records[0][0]
		brandname = records[0][1]
		return "EXIST",brandid,brandname
	elif brandname != "":
		brandidlong = hashlib.md5(brandname.encode('utf-8')).hexdigest()
		brandid = "N_" + brandidlong[:6].upper()
		return "NEW",brandid,brandname
	else:
		return "INVALID",emptybrandid,emptybrandname

def discoverproductnamebygtin(gtin,attempt):
	preferredsources = ["buycott.com","openfoodfacts.org","ebay.co","campbells.com.au"]

	attempt += 1
	selectedurl,selectedtitle = downloadproductpages(gtin,"google",preferredsources)
	if selectedurl != "ERROR" and selectedurl != "":
		randagent = random.choice(useragents)
		headers = {'User-Agent': randagent}
		r = requests.get(selectedurl, headers=headers, timeout=10)
		selectedhtml = r.content

		soup = BeautifulSoup(selectedhtml, 'html.parser')
		
		brandid = ""
		productname = ""
		brandname = ""
		brandowner = ""
		if "buycott.com" in selectedurl:
			productname = soup.find('h2').text.strip()

			brandcell = soup.find('td', text = re.compile('Brand'))
			brandname = brandcell.find_next_sibling('td').find('a').text.strip()
			manufacturercell = soup.find('td', text = re.compile('Manufacturer'))
			brandowner = manufacturercell.find_next_sibling('td').find('a').text.strip()
		elif "ebay.co" in selectedurl:
			productname = soup.find('title').text
			productname = re.sub(r"\|.+$", "", productname).strip()
			#print("[%s][%s]" % (selectedurl,productname))
			brandcell = soup.find('td', text = re.compile('Brand:'))
			if brandcell is not None:
				brandname = brandcell.find_next_sibling('td').text.strip()
				#<td class="attrLabels">Brand:</td><td width="50.0%"><span>Campbell Soups</span></td>
				#<td class="attrLabels">Brand:</td><td width="50.0%"><h2 itemprop="brand" itemscope="itemscope" itemtype="http://schema.org/Brand"><span itemprop="name">Sirena</span></h2></td>
			else:
				brandcell = soup.find('div', text = re.compile('BRAND'))
				brandname = brandcell.find_next_sibling('div').text.strip()
				#<div class="s-name">BRAND</div><div class="s-value">Heinz</div>
		elif "openfoodfacts.org" in selectedurl:
			productname = soup.find('title').text
			productname = re.sub(r"\|.+$", "", productname).strip()
			#print("[%s][%s]" % (selectedurl,productname))
			brandcell = soup.find('span', text = re.compile('Brands:'))
			if brandcell is not None:
				brandname = brandcell.find_next_sibling('a').text.strip()
				#<span class="field">Brands:</span> <a itemprop="brand" href="/brand/nestle">Nestlé</a>
		elif "campbells.com.au" in selectedurl:
			productname = soup.find('title').text
			productname = re.sub(r"\|.+$", "", productname).strip()
			#productname = soup.find('div', {'class':'productName'}).text
			brandname = soup.find('div', {'class':'productBrand'}).text.strip()
			#<div class="productBrand">ARNOTTS</div>
			#<div class="productName"><h1>BISCUITS CUSTARD CREAM 250GM</h1></div>
		else:
			productname = selectedtitle

		outcome,brandid,brandname = resolvebrand(brandname)
		if outcome == 'NEW':
			brandid = addnewbrand(brandid,brandname,brandowner,"","")
		gtin = addnewproduct(gtin,productname,"",brandid,0,1)

		return productname,brandid
	elif selectedurl == "" and attempt == 2:
		productname,brandid = discoverproductnamebygtin(gtin,attempt)
		return productname,brandid
	elif selectedurl == "":
		return "WARN",""
	else:
		return "ERR",""

def lookupproductbygtin(gtin):
	query = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,p.isperishable,p.isedible,count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		WHERE p.gtin = %s
		GROUP by 1,2,3,4,5,6
	"""
	cursor.execute(query,(gtin,))
	records = cursor.fetchall()

	return records

def lookupbrandbyid(brandid):
	query = """
		SELECT
			b.brandid, b.brandname, b.brandimage, b.brandurl, b.brandowner, count(distinct(p.gtin))
		FROM brands AS b
		LEFT JOIN products as p
		ON b.brandid = p.brandid
		WHERE b.brandid = %s
		GROUP BY 1,2,3,4,5
	"""
	cursor.execute(query,(brandid,))
	records = cursor.fetchall()

	return records

def jsonifybrands(records):
	brands = []
	for record in records:
		brandid	  		= record[0]
		brandname  		= record[1]
		brandimage  	= record[2]
		brandurl  		= record[3]
		brandowner   	= record[4]
		productcount	= record[5]

		brand = {}
		brand['brandid'] 		= brandid
		brand['brandname']		= brandname
		brand['brandimage']		= brandimage
		brand['brandurl']		= brandurl
		brand['brandowner'] 	= brandowner
		brand['productcount'] 	= productcount

		brands.append(brand)

	return brands

def jsonifyproducts(records):
	products = []
	for record in records:
		gtin	  		= record[0]
		productname  	= record[1]
		productimage	= record[2]
		brandname   	= record[3]
		isperishable   	= record[4]
		isedible	   	= record[5]

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

def jsonifyoutput(statuscode,status,records):
	messages = []
	message = {}
	message['status'] = status
	message['results'] = records
	messages.append(message)

	return jsonify(messages),statuscode

@app.route("/")
@requires_auth
def main():
	status = "invalid endpoint"
	statuscode = 500

	return jsonifyoutput(statuscode,status,[])

@app.route('/products', methods=['DELETE'])
@requires_auth
def productdelete():
	status = "product deleted"
	statuscode = 200

	gtin = request.args.get("gtin").strip()

	try:
		query1 = "DELETE FROM products WHERE gtin = %s"
		cursor.execute(query1,(gtin,))
		db.commit()
	except:
		status = "products attached to inventory - unable to delete"
		statuscode = 403#forbidden

	records = lookupproductbygtin(gtin)
	return jsonifyoutput(statuscode,status,jsonifyproducts(records))

@app.route('/products', methods=['POST'])
@requires_auth
def productupsert():
	status = ""
	statuscode = 200

	gtin = request.args.get("gtin")
	productname 	= request.args.get("productname").strip()
	productimage	= request.args.get("productimage").strip()
	brandname		= request.args.get("brandname").strip()
	isperishable 	= request.args.get("isperishable").strip()
	isedible 		= request.args.get("isedible").strip()
		
	query1 = """
    	SELECT
        	gtin
    	FROM products
    	WHERE gtin = %s
	"""
	cursor.execute(query1,(gtin,))
	records = cursor.fetchall()
	if records:
		gtin = records[0][0]
		if productname != '':
			query2 = "UPDATE products SET productname = %s WHERE gtin = %s"
			cursor.execute(query2,(productname,gtin))
			db.commit()

			status = status + "productname "
		if isperishable != '':
			query2 = "UPDATE products SET isperishable = %s WHERE gtin = %s"
			cursor.execute(query2,(isperishable,gtin))
			db.commit()

			status = status + "isperishable "
		if isedible != '':
			query2 = "UPDATE products SET isedible = %s WHERE gtin = %s"
			cursor.execute(query2,(isedible,gtin))
			db.commit()

			status = status + "isedible "
		if productimage != '':
			query2 = "UPDATE products SET productimage = %s WHERE gtin = %s"
			cursor.execute(query2,(productimage,gtin))
			db.commit()

			status = status + "productimage "
		if brandname != '':
			outcome,brandid,brandname = resolvebrand(brandname)

			query2 = "UPDATE products SET brandid = %s WHERE gtin = %s"
			cursor.execute(query2,(brandid,gtin))
			db.commit()

			status = status + "brandname "
		if status != "":
			status = status + "updated"
		else:
			status = "no updates"

		records = lookupproductbygtin(gtin)
	elif gtin != '' and productname != '':
		outcome,brandid,brandname = resolvebrand(brandname)
		if outcome == 'NEW':
			brandid = addnewbrand(brandid,brandname,"","","")
		gtin = addnewproduct(gtin,productname,productimage,brandid,0,1)	

		records = lookupproductbygtin(gtin)
		status = "new product (and branded) added"
	elif gtin == "":
		status = "no gtin provided"
		statuscode = 412
	else:
		productname,brandid = discoverproductnamebygtin(gtin,1)
		if productname != "ERR" and productname != "WARN":
			if productname != "" and brandid != '':
				status = status + "new product and brand discovered and added"
			elif productname != "":
				status = status + "new product discovered and added without brand"

			records = lookupproductbygtin(gtin)
		elif productname == "ERR":
			status = "public search for product errored - try again later"
			statuscode = 503#service unavailable
		elif productname == "WARN":
			status = "public search for product returned no data - manual entry required"
			statuscode = 404#not found

	return jsonifyoutput(statuscode,status,jsonifyproducts(records))

@app.route('/products/<gtin>', methods=['GET'])
@requires_auth
def productselect(gtin):
	status = ""
	statuscode = 200

	records = lookupproductbygtin(gtin)
	if not records:
		query1 = """
			SELECT
				p.gtin,p.productname,p.productimage,b.brandname,p.isperishable,p.isedible,count(*)
			FROM products AS p
			JOIN brands AS b
			ON p.brandid = b.brandid
			WHERE p.productname LIKE %s
			GROUP BY 1,2,3,4,5,6
		"""
		cursor.execute(query1,("%" + gtin + "%",))
		records = cursor.fetchall()

		status = "products searched by keyword"
	else:
		status = "product looked up by id"

	if not records:
		status = "product does not exists"
		statuscode = 404#404 Not FoundThe requested resource could not be found but may be available in the future. Subsequent requests by the client are 

	return jsonifyoutput(statuscode,status,jsonifyproducts(records))

@app.route('/products', methods=['GET'])
@requires_auth
def productselectall():
	status = "all products returned"
	statuscode = 200

	query1 = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,p.isperishable,p.isedible,count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		GROUP BY 1,2,3,4,5,6
	"""
	cursor.execute(query1)
	records = cursor.fetchall()

	return jsonifyoutput(statuscode,status,jsonifyproducts(records))

@app.route('/brands', methods=['DELETE'])
@requires_auth
def branddelete():
	status = "brand deleted"
	statuscode = 200

	brandid = request.args.get("brandid").strip()

	try:
		query1 = "DELETE FROM brands WHERE brandid = %s"
		cursor.execute(query1,(brandid,))
		db.commit()
	except:
		status = "products attached to brand - unable to delete"
		statuscode = 403#forbidden

	records = lookupbrandbyid(brandid)
	return jsonifyoutput(statuscode,status,jsonifybrands(records))

@app.route('/brands', methods=['POST'])
@requires_auth
def brandupsert():
	status = ""
	statuscode = 200

	brandid 	= request.args.get("brandid").strip()
	brandname 	= request.args.get("brandname").strip()
	brandimage 	= request.args.get("brandimage").strip()
	brandurl 	= request.args.get("brandurl").strip()
	brandowner 	= request.args.get("brandowner").strip()

	query1 = """
    	SELECT
        	brandid, brandname
    	FROM brands
    	WHERE brandid = %s OR brandname = %s
	"""
	cursor.execute(query1,(brandid,brandname))
	records = cursor.fetchall()
	if records:
		brandid = records[0][0]
		if brandname != "":
			query2 = "UPDATE brands SET brandname = %s WHERE brandid = %s"
			cursor.execute(query2,(brandname,brandid))
			db.commit()
			status = status + "brandname "
		if brandowner != "":
			query2 = "UPDATE brands SET brandowner = %s WHERE brandid = %s"
			cursor.execute(query2,(brandowner,brandid))
			db.commit()
			status = status + "brandowner "
		if brandimage != "":
			query2 = "UPDATE brands SET brandimage = %s WHERE brandid = %s"
			cursor.execute(query2,(brandimage,brandid))
			db.commit()
			status = status + "brandimage "
		if brandurl != "":
			query2 = "UPDATE brands SET brandurl = %s WHERE brandid = %s"
			cursor.execute(query2,(brandurl,brandid))
			db.commit()
			status = status + "brandurl "

		if status != "":
			status = status + "updated"
		else:
			status = "no updates"

		records = lookupbrandbyid(brandid)
	elif brandname != '':
		outcome,brandid,brandname = resolvebrand(brandname)
		if outcome == 'NEW':
			brandid = addnewbrand(brandid,brandname,brandowner,brandimage,brandurl)
		records = lookupbrandbyid(brandid)

		status = "new brand added"
	else:
		status = "no brand id or name provided"
		statuscode = 412#412 Precondition Failed (RFC 7232) The server does not meet one of the preconditions that the requester put on the request header fields

	return jsonifyoutput(statuscode,status,jsonifybrands(records))

@app.route('/brands/<brandid>', methods=['GET'])
@requires_auth
def brandselect(brandid):
	status = ""
	statuscode = 200

	records = lookupbrandbyid(brandid)
	if not records:
		query1 = """
			SELECT
				b.brandid, b.brandname, b.brandimage, b.brandurl, b.brandowner, count(distinct(p.gtin))
			FROM brands AS b
			LEFT JOIN products as p
			ON b.brandid = p.brandid
			WHERE b.brandname LIKE %s
			GROUP BY 1,2,3,4,5
		"""
		cursor.execute(query1,("%" + brandid + "%",))
		records = cursor.fetchall()

		status = "brands found with keyword search"
	else:
		status = "brand found with id lookup"

	if not records:
		status = "brand does not exists"
		statuscode = 404#404 Not FoundThe requested resource could not be found but may be available in the future. Subsequent requests by the client are 

	return jsonifyoutput(statuscode,status,jsonifybrands(records))

@app.route('/brands', methods=['GET'])
@requires_auth
def brandselectall():
	status = "all brands returned"
	statuscode = 200

	query1 = """
		SELECT
			b.brandid, b.brandname, b.brandimage, b.brandurl, b.brandowner, count(distinct(p.gtin))
		FROM brands AS b
		LEFT JOIN products as p
		ON b.brandid = p.brandid
		GROUP BY 1,2,3,4,5
	"""
	cursor.execute(query1)
	records = cursor.fetchall()

	return jsonifyoutput(statuscode,status,jsonifybrands(records))

@app.route('/inventories', methods=['POST'])
@requires_auth
def inventoryadd():
	status = ""
	statuscode = 200

	brandid = request.args.get("brandid").strip()

@app.route("/inventories", methods=['GET'])
@requires_auth
def inventoryselectall():
	status = "no user id provided"
	statuscode = 412#412 Precondition Failed (RFC 7232) The server does not meet one of the preconditions that the requester put on the request header fields.

	return jsonifyoutput(statuscode,status,[])

@app.route('/inventories/<uid>', methods=['GET'])
@requires_auth
def inventoryselect(uid):
	status = ""
	statuscode = 200

	query1 = """
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
	cursor.execute(query1,(uid,))
	records = cursor.fetchall()

	status = "all inventory items for the user returned"

	if not records:
		status = "user id is either invalid or does not have an inventory"
		statuscode = 404#404 Not Found The requested resource could not be found but may be available in the future. Subsequent requests by the client are 

	return jsonifyoutput(statuscode,status,jsonifyinventory(records))
	
if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0',port=8989)

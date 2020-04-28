import flask
import simplejson as json
import requests
import mysql.connector
import re
import bs4
import datetime
import random
import os
import urllib
import hashlib
import logging
import functools

mysqlhost = "inven3sdb.ciphd8suvvza.ap-southeast-1.rds.amazonaws.com"
mysqlport = "3363"
mysqluser = "inven3suser"
mysqlpwrd = "P?a&N$3!s"
mysqldb = "inven3s"
apiuser = "inven3sapiuser"
apipwrd = "N0tS3cUr3!"
logfile = "inven3s.log"
defaultbrandid = "N_000000"
defaultbrandname = "Unavailable"
defaultretailercity = "4084"
defaultdateexpiry = "0000-00-00"

logging.basicConfig(filename=logfile,level=logging.DEBUG)
db = mysql.connector.connect(
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

app = flask.Flask(__name__)#template_dir = os.path.abspath(flasktemplatedir) <=> static_url_path='',static_folder=template_dir,template_folder=template_dir
app.config['JSON_SORT_KEYS'] = False

def check_auth(username, password):
    return username == apiuser and password == apipwrd

def authenticate():
    message = {'message': "authentication required"}
    resp = flask.jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp

def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = flask.request.authorization
        if not auth: 
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

def formatisedible(isedible):
	try:
		isedible = str(isedible)
		if isedible is None or isedible == "":
			return "0,1"
		elif isedible == "0" or isedible == "1":
			return str(isedible)
		else:
			return "1"
	except:
		return "1"

def formatispartiallyconsumed(ispartiallyconsumed):
	try:
		if int(ispartiallyconsumed) == 1 or int(ispartiallyconsumed) == 0:
			return int(ispartiallyconsumed)
		else:
			return 0
	except:
		return 0

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
		productimage	= record[2]
		brandname   	= record[3]
		dateexpiry   	= record[4]
		itemcount		= record[5]

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
	message['message'] = status
	message['count'] = len(records)
	message['results'] = records
	messages.append(message)

	return flask.jsonify(messages),statuscode

def addproductcandidate(source,gtin,title,url,rank):
    id = hashlib.md5(title.encode('utf-8')).hexdigest()
    query1 = "REPLACE INTO productcandidates (gtin,source,candidateid,candidatetitle,candidateurl,candidaterank) VALUES (%s,%s,%s,%s,%s,%s)"
    cursor.execute(query1,(gtin,source,id,title,url,rank))
    db.commit()

def removebrand(brandid):
	query1 = "DELETE FROM brands WHERE brandid = %s"
	cursor.execute(query1,(brandid,))
	db.commit()

def addnewbrand(brandid,brandname,brandowner,brandimage,brandurl):
	if brandname != "":
		query2 = "REPLACE INTO brands (brandid,brandname,brandowner,brandimage,brandurl) VALUES (%s,%s,%s,%s,%s)"
		cursor.execute(query2,(brandid,brandname.title(),brandowner.title(),brandimage,brandurl))
		db.commit()

		return brandid
	else:
		return ""

def addinventoryitem(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno):
	if uid != "" and gtin != "" and retailerid != "" and dateentry != "":
		query1 = "INSERT INTO inventories (userid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
		cursor.execute(query1,(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno))
		db.commit()

def removeproduct(gtin):
	query1 = "DELETE FROM products WHERE gtin = %s"
	cursor.execute(query1,(gtin,))
	db.commit()

def addnewproduct(gtin,productname,productimage,brandid,isperishable,isedible):
	if productname != "":#and brandid != ""
		query2 = "INSERT INTO products (gtin,productname,productimage,brandid,isperishable,isedible) VALUES (%s,%s,%s,%s,%s,%s)"
		cursor.execute(query2,(gtin,productname.title(),productimage,brandid,isperishable,isedible))
		db.commit()
	
		return gtin
	else:
		return ""

def addnewretailer(retailername,retailercity):
	if retailercity == "":
		retailercity = defaultretailercity

	if retailername != "":
		retailermash = retailername + "&&" + retailercity

		retailerid = hashlib.md5(retailermash.encode('utf-8')).hexdigest()
		query2 = "INSERT INTO retailers (retailerid,retailername,retailercity) VALUES (%s,%s,%s)"
		cursor.execute(query2,(retailerid,retailername.title(),retailercity))
		db.commit()

		return retailerid
	else:
		return ""

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

		soup = bs4.BeautifulSoup(html, 'html.parser')
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
				if re.match(r"^%s" % preferredsrc,resultlink):
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
	except:
		logging.debug("error: unknown [%s]" % url)

	return "ERR",""

def discovernewproduct(gtin,attempt):
	preferredsources = ["https:\/\/(?:world|world\-fr|au|fr\-en|ssl\-api)\.openfoodfacts\.org","https:\/\/www\.campbells\.com\.au","https:\/\/www\.ebay\.com"]

	attempt += 1
	selectedurl,selectedtitle = downloadproductpages(gtin,"google",preferredsources)
	if selectedurl != "ERROR" and selectedurl != "":
		selectedhtml = ""
		try:
			randagent1 = random.choice(useragents)
			headers1 = {'User-Agent': randagent1}
			r1 = requests.get(selectedurl, headers=headers1, timeout=10)
			selectedhtml = r1.content
		except:
			logging.debug("scraper-error: [%s]" % selectedurl)
			selectedurl,selectedtitle = downloadproductpages(gtin,"bing",preferredsources)
			if selectedurl != "ERROR" and selectedurl != "":
				randagent2 = random.choice(useragents)
				headers2 = {'User-Agent': randagent2}
				r2 = requests.get(selectedurl, headers=headers2, timeout=10)
				selectedhtml = r2.content

		if selectedhtml != "":
			soup = bs4.BeautifulSoup(selectedhtml, 'html.parser')
			
			logging.debug("crawler: selectedurl [%s]" % (selectedurl))

			brandid = ""
			productname = ""
			brandname = ""
			brandowner = ""
			if re.match(r'^https:\/\/www\.buycott\.com',selectedurl):
				productname = soup.find('h2').text.strip()

				brandcell = soup.find('td', text = re.compile('Brand'))
				brandname = brandcell.find_next_sibling('td').find('a').text.strip()
				manufacturercell = soup.find('td', text = re.compile('Manufacturer'))
				brandowner = manufacturercell.find_next_sibling('td').find('a').text.strip()
			elif re.match(r'^https:\/\/www\.ebay\.com',selectedurl):
				productname = soup.find('title').text
				productname = re.sub(r"\|.+$", "", productname).strip()
				brandcell = soup.find('td', text = re.compile('Brand:'))
				if brandcell is not None:
					brandname = brandcell.find_next_sibling('td').text.strip()
					#<td class="attrLabels">Brand:</td><td width="50.0%"><span>Campbell Soups</span></td>
					#<td class="attrLabels">Brand:</td><td width="50.0%"><h2 itemprop="brand" itemscope="itemscope" itemtype="http://schema.org/Brand"><span itemprop="name">Sirena</span></h2></td>
				else:
					brandcell = soup.find('div', text = re.compile('BRAND'))
					brandname = brandcell.find_next_sibling('div').text.strip()
					#<div class="s-name">BRAND</div><div class="s-value">Heinz</div>
			elif re.match(r'^https:\/\/(?:world|world\-fr|au|fr\-en|ssl\-api)\.openfoodfacts\.org',selectedurl):
				productname = soup.find('title').text
				productname = re.sub(r"\|.+$", "", productname).strip()
				brandcell = soup.find('span', text = re.compile('Brands:'))
				if brandcell is not None:
					brandname = brandcell.find_next_sibling('a').text.strip()
					#<span class="field">Brands:</span> <a itemprop="brand" href="/brand/nestle">Nestlé</a>
			elif re.match(r'^https:\/\/www\.campbells\.com\.au',selectedurl):
				productname = soup.find('title').text
				productname = re.sub(r"\|.+$", "", productname).strip()
				#productname = soup.find('div', {'class':'productName'}).text
				brandname = soup.find('div', {'class':'productBrand'}).text.strip()
				#<div class="productBrand">ARNOTTS</div>
				#<div class="productName"><h1>BISCUITS CUSTARD CREAM 250GM</h1></div>
			else:
				productname = selectedtitle

			brandid,brandname,brandstatus = isbrandvalid("",brandname)
			if brandstatus == 'NEW':
				brandid = addnewbrand(brandid,brandname,brandowner,"","")
			gtin = addnewproduct(gtin,productname,"",brandid,0,1)

			return productname,brandid
		else:
			return "ERR",""

	elif selectedurl == "" and attempt == 2:
		productname,brandid = discovernewproduct(gtin,attempt)
		return productname,brandid
	elif selectedurl == "":
		return "WARN",""
	else:
		return "ERR",""

def findallproducts(isedible):
	query1 = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,p.isperishable,p.isedible,count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		WHERE isedible IN (%s)
		GROUP BY 1,2,3,4,5,6
	""" % formatisedible(isedible)
	cursor.execute(query1)
	records = cursor.fetchall()

	return records

def findproductbykeyword(gtin,isedible):
	query1 = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,p.isperishable,p.isedible,count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		WHERE p.productname LIKE %s AND p.isedible IN (%s)
		GROUP BY 1,2,3,4,5,6
	""" % ("'%" + gtin + "%'",formatisedible(isedible))
	cursor.execute(query1)
	records = cursor.fetchall()

	return records

def findproductbygtin(gtin):
	query = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,p.isperishable,p.isedible,count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		WHERE p.gtin = %s
		GROUP by 1,2,3,4,5,6
		ORDER BY 2
	"""
	cursor.execute(query,(gtin,))
	records = cursor.fetchall()

	return records

def findinventorybyuser(uid,isedible,ispartiallyconsumed):
	query1 = """
		SELECT * FROM (
			SELECT
				i.gtin,p.productname,p.productimage,b.brandname,i.dateexpiry,
				SUM(case when i.itemstatus = 'IN' then i.quantity else i.quantity*-1 END) AS itemsremaining
			FROM inventories AS i
			JOIN products AS p
			ON i.gtin = p.gtin
			JOIN brands AS b
			ON p.brandid = b.brandid
			WHERE i.userid = %s AND p.isedible IN (%s)
			GROUP BY 1,2,3,4,5
			ORDER BY 2
		) as items
		WHERE itemsremaining > 0
	""" % (uid,formatisedible(isedible))
	if formatispartiallyconsumed(ispartiallyconsumed) == 1:
		query1 += " AND MOD(itemsremaining*2,2) != 0"
	elif formatispartiallyconsumed(ispartiallyconsumed) == 0:
		query1 += " AND MOD(itemsremaining*2,2) = 0"
	cursor.execute(query1)
	records = cursor.fetchall()

	itemsremainingtotal = sum(row[5] for row in records)

	return records, itemsremainingtotal

def findproductexpiry(uid,gtin):
	query1 = """
		SELECT
			i.retailerid,i.dateexpiry
		FROM inventories AS i
		JOIN products AS p
		ON i.gtin = p.gtin
		JOIN brands AS b
		ON p.brandid = b.brandid
		WHERE i.userid = %s AND p.gtin = %s
		ORDER BY i.dateexpiry asc
		LIMIT 1
	""" % (uid,gtin)
	cursor.execute(query1)
	records = cursor.fetchall()
	if records:
		retailerid = records[0][0]
		dateexpiry = records[0][1]
		if dateexpiry is None:
			dateexpiry = defaultdateexpiry
		return retailerid,dateexpiry
	else:
		return "",defaultdateexpiry

def countinventoryitems(uid,gtin):
	query1 = """
		SELECT
			SUM(case when i.itemstatus = 'IN' then i.quantity else i.quantity*-1 END) AS itemcount
		FROM inventories AS i
		JOIN products AS p
		ON i.gtin = p.gtin
		JOIN brands AS b
		ON p.brandid = b.brandid
		WHERE i.userid = %s AND p.gtin = %s
	""" % (uid,gtin)
	cursor.execute(query1)
	records = cursor.fetchall()
	count = records[0][0]
	if count:
		return float(count)
	else:
		return float(0) 

def findallbrands():
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

	return records

def findbrandbykeyword(brandid):
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

	return records

def findbrandbyid(brandid):
	query = """
		SELECT
			b.brandid, b.brandname, b.brandimage, b.brandurl, b.brandowner, count(distinct(p.gtin))
		FROM brands AS b
		LEFT JOIN products as p
		ON b.brandid = p.brandid
		WHERE b.brandid = %s
		GROUP BY 1,2,3,4,5
		ORDER BY 2
	"""
	cursor.execute(query,(brandid,))
	records = cursor.fetchall()

	return records

def resolveretailer(retailername):
	query1 = """
    	SELECT
        	retailerid,retailername
    	FROM retailers
    	WHERE lower(retailername) = %s
	"""
	cursor.execute(query1,(retailername.lower(),))
	records = cursor.fetchall()
	if records:
		retailerid = records[0][0]
		retailername = records[0][1]

		return retailerid,retailername
	else:
		return "",retailername

def isbrandvalid(brandid,brandname):
	query1 = """
    	SELECT
        	brandid, brandname
    	FROM brands
    	WHERE brandid = %s OR lower(brandname) = %s
	"""
	cursor.execute(query1,(brandid,brandname.lower()))
	records = cursor.fetchall()
	if records:
		brandid = records[0][0]
		brandname = records[0][1]
		return brandid,brandname,"EXISTS"
	elif brandname != "":
		brandidlong = hashlib.md5(brandname.encode('utf-8')).hexdigest()
		brandid = "N_" + brandidlong[:6].upper()
		return brandid,brandname,"NEW"
	else:
		return defaultbrandid,defaultbrandname,"INVALID"

def isuservalid(uid):
	if uid is not None and uid != "":
		return True
	else:
		return False

def isgtinvalid(gtin):
	if gtin is not None and gtin != "" and len(gtin) == 13:
		query1 = """
	    	SELECT
	        	gtin,productname
	    	FROM products
	    	WHERE gtin = %s
		"""
		cursor.execute(query1,(gtin,))
		records = cursor.fetchall()
		if records:
			gtin = records[0][0]
			productname = records[0][1]
			return gtin,productname,"EXISTS"
		else:
			return gtin,"","NEW"
	else:
		return gtin,"","INVALID"

def isitemstatusvalid(itemstatus):
	if itemstatus == "IN" or itemstatus == "OUT":
		return True
	else:
		return False

def isfloat(quantity):
    try:
        float(quantity)
        return True
    except ValueError:
        return False

@app.route("/")
@requires_auth
def main():
	status = "invalid endpoint"
	statuscode = 501#Not Implemented

	return jsonifyoutput(statuscode,status,[])

@app.route('/products/<gtin>', methods=['DELETE'])
@requires_auth
def productdelete(gtin):
	status = ""
	statuscode = 200
	records = []

	gtin,productname,gtinstatus = isgtinvalid(gtin)
	if gtinstatus == "EXISTS":
		try:
			removeproduct(gtin)
			status = "product deleted"
		except:
			status = "products attached to inventory - unable to delete"
			statuscode = 403#Forbidden
	else:
		status = "invalid gtin"
		statuscode = 412#Precondition Failed

	records = findproductbygtin(gtin)
	return jsonifyoutput(statuscode,status,jsonifyproducts(records))

@app.route('/products', methods=['POST'])
@requires_auth
def productupsert():
	status = ""
	statuscode = 200
	records = []

	gtin 			= flask.request.args.get("gtin")
	productname 	= flask.request.args.get("productname")
	productimage	= flask.request.args.get("productimage")
	brandname		= flask.request.args.get("brandname")
	isperishable 	= flask.request.args.get("isperishable")#DEFAULT '0'
	isedible 		= flask.request.args.get("isedible")#DEFAULT '1'
	
	gtin,productname_old,gtinstatus = isgtinvalid(gtin)
	if gtinstatus == "EXISTS":
		if productname != '':
			query2 = "UPDATE products SET productname = %s WHERE gtin = %s"
			cursor.execute(query2,(productname.strip().title(),gtin))
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
			brandid,brandname,brandstatus = isbrandvalid("",brandname.strip())
			if brandstatus == 'NEW':
				brandid = addnewbrand(brandid,brandname,"","","")
			query2 = "UPDATE products SET brandid = %s WHERE gtin = %s"
			cursor.execute(query2,(brandid,gtin))
			db.commit()

			status = status + "brandname "
		if status != "":
			status = status + "updated"
		else:
			status = "no updates"

		records = findproductbygtin(gtin)
	elif gtinstatus == "NEW" and productname != "":
		brandid,brandname,brandstatus = isbrandvalid("",brandname)
		if brandstatus == 'NEW':
			brandid = addnewbrand(brandid,brandname,"","","")
		gtin = addnewproduct(gtin,productname,productimage,brandid,0,1)	

		records = findproductbygtin(gtin)
		status = "new product (and branded) added"
	elif gtinstatus == "NEW" and productname == "":
		productname,brandid = discovernewproduct(gtin,1)
		if productname != "ERR" and productname != "WARN":
			if productname != "" and brandid != '':
				status = status + "new product and brand discovered and added"
			elif productname != "":
				status = status + "new product discovered and added without brand"

			records = findproductbygtin(gtin)
		elif productname == "ERR":
			status = "public search for product errored - try again later"
			statuscode = 503#Service Unavailable
		elif productname == "WARN":
			status = "public search for product returned no data - manual entry required"
			statuscode = 404#Not Found
	else:
		status = "invalid gtin"
		statuscode = 412#Precondition Failed

	return jsonifyoutput(statuscode,status,jsonifyproducts(records))

@app.route('/products/<gtin>', methods=['GET'])
@requires_auth
def productselect(gtin):
	status = ""
	statuscode = 200
	records = []

	isedible = flask.request.args.get("isedible")

	gtin,productname,gtinstatus = isgtinvalid(gtin)
	if gtinstatus == "EXISTS":
		records = findproductbygtin(gtin)
	elif gtinstatus == "NEW":
		status = "product does not exists"
		statuscode = 404#Not Found
	else:
		records = findproductbykeyword(gtin,isedible)
		if records:
			status = "products searched by keyword"
		elif gtinstatus == "INVALID":
			status = "invalid gtin"
			statuscode = 412#Precondition Failed
		else:
			status = "product does not exists"
			statuscode = 404#Not Found

	return jsonifyoutput(statuscode,status,jsonifyproducts(records))

@app.route('/products', methods=['GET'])
@requires_auth
def productselectall():
	status = "all products returned"
	statuscode = 200

	isedible = flask.request.args.get("isedible")
	
	records = findallproducts(isedible)

	return jsonifyoutput(statuscode,status,jsonifyproducts(records))

@app.route('/brands/<brandid>', methods=['DELETE'])
@requires_auth
def branddelete(brandid):
	status = "brand deleted"
	statuscode = 200
	records = []

	brandid,brandname,brandstatus = isbrandvalid(brandid,"")
	if brandstatus == "EXISTS":
		try:
			removebrand(brandid)
		except:
			status = "products attached to brand - unable to delete"
			statuscode = 403#Forbidden

		records = findbrandbyid(brandid)
	else:
		status = "invalid brandid"
		statuscode = 412#Precondition Failed

	return jsonifyoutput(statuscode,status,jsonifybrands(records))

@app.route('/brands', methods=['POST'])
@requires_auth
def brandupsert():
	status = ""
	statuscode = 200
	records = []

	brandid 	= flask.request.args.get("brandid").strip()
	brandname 	= flask.request.args.get("brandname").strip()
	brandimage 	= flask.request.args.get("brandimage").strip()
	brandurl 	= flask.request.args.get("brandurl").strip()
	brandowner 	= flask.request.args.get("brandowner").strip()

	brandid, brandname, brandstatus = isbrandvalid(brandid,brandname)
	if brandstatus == "EXISTS":
		if brandname != "":
			query2 = "UPDATE brands SET brandname = %s WHERE brandid = %s"
			cursor.execute(query2,(brandname.title(),brandid))
			db.commit()
			status += "brandname "
		if brandowner != "":
			query2 = "UPDATE brands SET brandowner = %s WHERE brandid = %s"
			cursor.execute(query2,(brandowner.title(),brandid))
			db.commit()
			status += "brandowner "
		if brandimage != "":
			query2 = "UPDATE brands SET brandimage = %s WHERE brandid = %s"
			cursor.execute(query2,(brandimage,brandid))
			db.commit()
			status += "brandimage "
		if brandurl != "":
			query2 = "UPDATE brands SET brandurl = %s WHERE brandid = %s"
			cursor.execute(query2,(brandurl,brandid))
			db.commit()
			status += "brandurl "

		if status != "":
			status += "updated"
		else:
			status = "no updates"

		records = findbrandbyid(brandid)
	elif brandstatus == "NEW":
		brandid = addnewbrand(brandid,brandname,brandowner,brandimage,brandurl)
		records = findbrandbyid(brandid)

		status = "new brand added"
	else:
		status = "invalid brandid or brandname"
		statuscode = 412#Precondition Failed

	return jsonifyoutput(statuscode,status,jsonifybrands(records))

@app.route('/brands/<brandid>', methods=['GET'])
@requires_auth
def brandselect(brandid):
	status = ""
	statuscode = 200

	records = findbrandbyid(brandid)
	if not records:
		records = findbrandbykeyword(brandid)

		status = "brands found with keyword search"
	else:
		status = "brand found with id lookup"

	if not records:
		status = "brand does not exists"
		statuscode = 404#Not Found

	return jsonifyoutput(statuscode,status,jsonifybrands(records))

@app.route('/brands', methods=['GET'])
@requires_auth
def brandselectall():
	status = "all brands returned"
	statuscode = 200

	records = findallbrands()

	return jsonifyoutput(statuscode,status,jsonifybrands(records))

@app.route('/inventories/<uid>', methods=['POST'])
@requires_auth
def inventoryupsert(uid):
	status = ""
	statuscode = 200
	records = []

	gtin 		= flask.request.args.get("gtin")
	retailername= flask.request.args.get("retailername")
	dateexpiry	= flask.request.args.get("dateexpiry")#DEFAULT '0000-00-00'
	quantity	= flask.request.args.get("quantity")#DEFAULT '1'
	itemstatus	= flask.request.args.get("itemstatus")#DEFAULT 'IN'
	receiptno	= flask.request.args.get("receiptno")

	gtin,productname,gtinstatus = isgtinvalid(gtin)
	if gtinstatus != "INVALID" and isuservalid(uid) and isfloat(quantity) and isitemstatusvalid(itemstatus):
		if productname == "":
			productname,brandid = discovernewproduct(gtin,1)
			if productname == "ERR":
				status = "public search for product errored - try again later"
				statuscode = 503#Service Unavailable
			elif productname == "WARN":
				status = "public search for product returned no data - manual entry required"
				statuscode = 404#Not found

			if productname == "ERR" or productname == "WARN":
				productname = ""

		retailerid,retailername = resolveretailer(retailername)
		if retailerid == "" and retailername != "":
			retailerid = addnewretailer(retailername,"")
		elif retailername == "" and itemstatus == "IN":
			status = "invalid retailername"
			statuscode = 412#Precondition Failed

		if productname != "" and ((itemstatus == "IN" and retailerid != "") or itemstatus == "OUT"):
			inventorycount = countinventoryitems(uid,gtin)
			if itemstatus == "OUT" and inventorycount-float(quantity) < 0:
				status = "unable to register items consumed - inadequate stock in inventory"
				statuscode = 403#Forbidden
			else:
				if itemstatus == "OUT" and (dateexpiry is None or dateexpiry == ""):
					retailerid,dateexpiry = findproductexpiry(uid,gtin)
				dateentry = datetime.datetime.today().strftime('%Y-%m-%d')
				addinventoryitem(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno)
				if itemstatus == "IN":
					status = "product item added to inventory"
				else:
					status = "product item removed (or marked as being consumed) in inventory"

			records,inventorycount = findinventorybyuser(uid,"0,1",0)
			status += " - %s" % inventorycount

	elif not isuservalid(uid):
		status = "invalid uid"
		statuscode = 412#Precondition Failed
	elif not isfloat(quantity):
		status = "invalid quantity"
		statuscode = 412#Precondition Failed
	elif not isitemstatusvalid(itemstatus):
		status = "invalid itemstatus"
		statuscode = 412#Precondition Failed		
	else:
		status = "invalid gtin"
		statuscode = 412#Precondition Failed

	return jsonifyoutput(statuscode,status,jsonifyinventory(records))

@app.route("/inventories/", methods=['GET','POST'])
@app.route("/inventories", methods=['GET','POST'])
@requires_auth
def inventoryselectall():
	status = "invalid uid"
	statuscode = 412#Precondition Failed

	return jsonifyoutput(statuscode,status,[])

@app.route('/inventories/<uid>', methods=['GET'])
@requires_auth
def inventoryselect(uid):
	status = ""
	statuscode = 200
	records = []

	if isuservalid(uid):
		isedible = flask.request.args.get("isedible")
		ispartiallyconsumed = flask.request.args.get("ispartiallyconsumed")

		records,inventorycount = findinventorybyuser(uid,isedible,ispartiallyconsumed)

		status = "all inventory items for the user returned - %s" % inventorycount

		if not records:
			status = "uid does not have an inventory"
			statuscode = 404#Not Found
	else:
		status = "invalid uid"
		statuscode = 412#Precondition Failed

	return jsonifyoutput(statuscode,status,jsonifyinventory(records))

if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0',port=8989)

#403#Forbidden
#404#Not Found
#412#Precondition Failed
#503#Service Unavailable
#501#Not Implemented
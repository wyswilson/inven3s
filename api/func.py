import datetime
import flask

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

config = configparser.ConfigParser()
config.read('conf.ini')

apisecretkey	= config['auth']['secretkey']
logfile 		= config['log']['file']
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
    pool_size = 5, pool_reset_session = True
   	)

cursor = db.cursor()

logging.basicConfig(filename=logfile,level=logging.DEBUG)

def generatehash(password):
	return werkzeug.security.generate_password_hash(password, method='sha256')

def checkpassword(passwordhashed,passwordfromauth):
	return werkzeug.security.check_password_hash(passwordhashed, passwordfromauth)

def generatejwt(userid,username):
	params = {'userid': userid,
				'username': username,
			'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)}
	token = jwt.encode(params, apisecretkey, algorithm='HS256')
	return token

def validatetoken(token):
	userid = None
	username = None
	try:
		data = jwt.decode(token, apisecretkey)
		userid = data['userid']
		username = data['username']
		return True,userid,username
	except:
		return False,userid,username

def requiretoken(f):
	@functools.wraps(f)
	def decorator(*args, **kwargs):
		headers = flask.request.headers
		if 'access-token' in headers:
			token = headers['access-token']
			valid,userid,username = validatetoken(token)
			if valid:
				return f(userid, *args, **kwargs)
			else:
				return jsonifyoutput(401,"unauthorised access - invalid token",[])
		else:
			return jsonifyoutput(401,"unauthorised access - missing token",[])

	return decorator

def basicauth():
    message = {'message': "authentication required"}
    resp = flask.jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp

def requiresbasicauth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = flask.request.authorization
        if not auth: 
            return basicauth()

        elif auth.username != apiuser and auth.password != apipassword:
            return basicauth()

        return f(*args, **kwargs)
    return decorated

def validateemail(email):
	if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email) != None:
		return True
	else:
		return False

def registeruserinterest(email, clientip, browser,platform,language,referrer):
	query1 = """
    	SELECT
        	email
    	FROM usersinterest
    	WHERE email = %s
	"""
	cursor.execute(query1,(email,))
	records = cursor.fetchall()
	if records:	
		return False
	else:
		eventdate = datetime.datetime.today().strftime('%Y-%m-%d')

		query1 = "INSERT INTO usersinterest (email,clientip,browser,platform,language,eventdate,referrer) VALUES (%s,%s,%s,%s,%s,%s,%s)"
		cursor.execute(query1,(email,clientip,browser,platform,language,eventdate,referrer))
		db.commit()

		return True

def addnewuser(email,passwordhashed):
	userid = hashlib.md5(email.encode('utf-8')).hexdigest()
	query1 = "INSERT INTO users (userid,email,passwordhashed) VALUES (%s,%s,%s)"
	cursor.execute(query1,(userid,email,passwordhashed))
	db.commit()

def updatebrandurl(brandid,brandurl):
	query2 = "UPDATE brands SET brandurl = %s WHERE brandid = %s"
	cursor.execute(query2,(brandurl,brandid))
	db.commit()

def updatebrandimage(brandid,brandimage):
	query2 = "UPDATE brands SET brandimage = %s WHERE brandid = %s"
	cursor.execute(query2,(brandimage,brandid))
	db.commit()

def updatebrandowner(brandid,brandowner):
	#string.capwords(brandowner.strip())
	query2 = "UPDATE brands SET brandowner = %s WHERE brandid = %s"
	cursor.execute(query2,(brandowner.strip(),brandid))
	db.commit()

def updatebrandname(brandid,brandname):
	#string.capwords(brandname.strip())
	query2 = "UPDATE brands SET brandname = %s WHERE brandid = %s"
	cursor.execute(query2,(brandname.strip(),brandid))
	db.commit()

def updateproductbrand(gtin,brandid):
	query2 = "UPDATE products SET brandid = %s WHERE gtin = %s"
	cursor.execute(query2,(brandid,gtin))
	db.commit()

def updateproductimage(gtin,productimage):
	query2 = "UPDATE products SET productimage = %s WHERE gtin = %s"
	cursor.execute(query2,(productimage,gtin))
	db.commit()

def updateisfavourite(gtin,userid,isfavourite):
	query1 = "REPLACE INTO productsfavourite (gtin,userid) VALUES (%s,%s)"
	cursor.execute(query1,(gtin,userid))
	db.commit()

	query2 = "UPDATE productsfavourite SET favourite = %s WHERE gtin = %s AND userid = %s"
	cursor.execute(query2,(isfavourite,gtin,userid))
	db.commit()

def updateisedible(gtin,isedible):
	query2 = "UPDATE products SET isedible = %s WHERE gtin = %s"
	cursor.execute(query2,(isedible,gtin))
	db.commit()

def updateisperishable(gtin,isperishable):
	query2 = "UPDATE products SET isperishable = %s WHERE gtin = %s"
	cursor.execute(query2,(isperishable,gtin))
	db.commit()

def updateproductname(gtin,productname):
	#string.capwords(productname.strip())
	query2 = "UPDATE products SET productname = %s WHERE gtin = %s"
	cursor.execute(query2,(productname.strip(),gtin))
	db.commit()

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

def jsonifyretailers(records):
	retailers = []
	for record in records:
		retailerid	  	= record[0]
		retailername  	= record[1]

		retailer = {}
		retailer['retailerid'] 		= retailerid
		retailer['retailername']	= retailername
		retailers.append(retailer)

	return retailers

def jsonifyproducts(records):
	products = []
	for record in records:
		gtin	  		= record[0]
		productname  	= record[1]
		productimage	= record[2]
		brandname   	= record[3]
		isperishable   	= record[4]
		isedible	   	= record[5]
		isfavourite	   	= record[6]

		product = {}
		product['gtin'] 			= gtin
		product['productname']		= productname
		product['productimage'] 	= productimage
		product['brandname'] 		= brandname
		product['isperishable'] 	= isperishable
		product['isedible'] 		= isedible
		product['isfavourite'] 		= isfavourite

		products.append(product)

	return products

def jsonifyinventory(records):
	inventory = []
	for record in records:
		gtin	  		= record[0]
		productname  	= record[1]
		productimage	= record[2]
		brandname   	= record[3]
		isedible		= record[4]
		isfavourite		= record[5]
		itemcount		= record[6]
		dateexpiry		= record[7]
		retailers		= record[8]

		if dateexpiry:
			dateexpiry = dateexpiry.strftime('%Y-%m-%d')

		itemgroup = {}
		itemgroup['gtin'] 			= gtin
		itemgroup['productname']	= productname
		itemgroup['productimage'] 	= productimage
		itemgroup['brandname'] 		= brandname
		itemgroup['dateexpiry'] 	= dateexpiry
		itemgroup['retailers'] 		= retailers
		itemgroup['itemcount'] 		= itemcount
		itemgroup['isedible'] 		= isedible
		itemgroup['isfavourite'] 		= isfavourite

		inventory.append(itemgroup)

	return inventory

def jsonifyoutput(statuscode,status,records,special=None):
	messages = []
	message = {}
	message['message'] = status
	if len(records) > 0:
		if isinstance(special, float) or isinstance(special, int):
			message['count'] = special
		else:
			message['count'] = len(records)
		message['results'] = records
	messages.append(message)

	if isinstance(special, dict):
		response = flask.jsonify(messages),statuscode,special
		return response
	else:
		response = flask.jsonify(messages),statuscode
		return response

def addproductcandidate(source,gtin,title,url,rank):
    id = hashlib.md5(title.encode('utf-8')).hexdigest()
    type = "productname"
    query1 = "REPLACE INTO productscandidate (gtin,source,type,candidateid,candidatetitle,candidateurl,candidaterank) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query1,(gtin,source,type,id,title,url,rank))
    db.commit()

def addnewbrand(brandid,brandname,brandowner,brandimage,brandurl):
	#string.capwords(brandname)
	if brandname != "":
		query2 = "REPLACE INTO brands (brandid,brandname,brandowner,brandimage,brandurl) VALUES (%s,%s,%s,%s,%s)"
		cursor.execute(query2,(brandid,brandname.strip(),brandowner.strip(),brandimage,brandurl))
		db.commit()

		return brandid
	else:
		return ""

def addinventoryitem(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno):
	if uid != "" and gtin != "" and retailerid != "" and dateentry != "":
		quantity = float(quantity)
		if quantity >= 1.0:
			i = 0
			while i < quantity:
				query1 = "INSERT INTO inventories (userid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno) VALUES (%s,%s,%s,%s,%s,%s,1,%s)"
				cursor.execute(query1,(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,receiptno))
				db.commit()
				i += 1#VERY IMPORTANT
		else:#IF quantity = 0.5 (FOR CONSUMPTION ITEMSTATUS=OUT)
			query1 = "INSERT INTO inventories (userid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
			cursor.execute(query1,(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno))
			db.commit()

def addnewproduct(gtin,productname,productimage,brandid,isperishable,isedible):
	if productname != "":#and brandid != ""
		query2 = "INSERT INTO products (gtin,productname,productimage,brandid,isperishable,isedible) VALUES (%s,%s,%s,%s,%s,%s)"
		cursor.execute(query2,(gtin,productname.strip(),productimage,brandid,isperishable,isedible))
		db.commit()
	
		return gtin
	else:
		return ""

def addnewretailer(retailername,retailercity=None):
	if retailercity == "" or retailercity is None:
		retailercity = defaultretailercity

	if retailername != "":
		retailermash = retailername + "&&" + retailercity

		retailerid = hashlib.md5(retailermash.encode('utf-8')).hexdigest()
		query2 = "INSERT INTO retailers (retailerid,retailername,retailercity) VALUES (%s,%s,%s)"
		cursor.execute(query2,(retailerid,retailername.strip(),retailercity))
		db.commit()

		return retailerid
	else:
		return ""

def removebrand(brandid):
	query1 = "DELETE FROM brands WHERE brandid = %s"
	cursor.execute(query1,(brandid,))
	db.commit()
	
def removeproduct(gtin):
	query1 = "DELETE FROM products WHERE gtin = %s"
	cursor.execute(query1,(gtin,))
	db.commit()

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

		selectedtitle = string.capwords(selectedtitle.strip())
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
			if selectedurl != "ERR" and selectedurl != "":
				randagent2 = random.choice(useragents)
				headers2 = {'User-Agent': randagent2}
				r2 = requests.get(selectedurl, headers=headers2, timeout=10)
				selectedhtml = r2.content

		if selectedhtml != "":
			soup = bs4.BeautifulSoup(selectedhtml, 'html.parser')
			
			logging.debug("crawler: selectedurl [%s]" % (selectedurl))

			brandid = ""
			productname = ""
			productimage = ""
			brandname = ""
			brandowner = ""
			if re.match(r'^https:\/\/www\.buycott\.com',selectedurl):
				productcell = soup.find('h2')
				if productcell:
					productname = productcell.text.strip()
					brandcell = soup.find('td', text = re.compile('Brand'))
					if brandcell:
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
					if brandcell is not None:
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

			brandid,brandname,brandstatus = validatebrand("",brandname)
			if brandstatus == 'NEW':
				brandid = addnewbrand(brandid,brandname,brandowner,"","")
			if productname != "":
				productimage = findproductimage(gtin,productname)

			gtin = addnewproduct(gtin,productname,productimage,brandid,0,1)

			if productname != "" and brandid != "":
				return productname,brandid,brandname
			else:
				return "WARN","",""
		else:
			return "ERR","",""

	elif selectedurl == "" and attempt == 2:
		productname,brandid,brandname = discovernewproduct(gtin,attempt)
		return productname,brandid,brandname
	elif selectedurl == "":
		return "WARN","",""
	else:
		return "ERR","",""

def findallproducts(userid,isedible):
	query1 = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,
			p.isperishable,p.isedible,
			case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		LEFT JOIN productsfavourite AS pf
		ON p.gtin = pf.gtin AND pf.userid = %s
	"""
	if validateisedible(isedible) == "2":
		query1 += "WHERE p.isedible != %s"
	else:
		query1 += "WHERE p.isedible = %s"
	query1 += " GROUP BY 1,2,3,4,5,6,7"
	cursor.execute(query1,(userid,validateisedible(isedible)))
	records = cursor.fetchall()

	return records

def generateshoppinglist(userid):
	query1 = """
		SELECT
			gtin, productname, productimage, brandname, isedible,isfavourite,
			itemstotal, dateexpiry, retailers
		FROM (
			SELECT
			  i.gtin,p.productname,p.productimage,b.brandname,p.isedible,
			  	case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			  max(i.dateexpiry) as dateexpiry,
			  max(i.dateentry) AS recentpurchasedate,
	  		  GROUP_CONCAT(DISTINCT r.retailername ORDER BY r.retailername SEPARATOR ', ') AS retailers,
			  SUM(case when i.itemstatus = 'IN' then i.quantity ELSE 0 END) AS historicaltotal,
			  SUM(case when i.itemstatus = 'IN' then i.quantity else i.quantity*-1 END) AS itemstotal
			FROM inventories AS i
			JOIN products AS p
			ON i.gtin = p.gtin
			JOIN brands AS b
			ON p.brandid = b.brandid
			JOIN retailers AS r
			ON i.retailerid = r.retailerid
			LEFT JOIN productsfavourite AS pf
			ON i.gtin = pf.gtin AND i.userid = pf.userid
			WHERE i.userid = %s AND p.isedible IN (0,1)
			GROUP BY 1,2,3,4,5,6
			ORDER BY 6 DESC, 10 DESC, 8 DESC
		) AS tmp
		WHERE (isfavourite = 0 and itemstotal < 1 and historicaltotal >= 2) OR (isfavourite = 1 and itemstotal < 2 and historicaltotal >= 1)
	"""
	cursor.execute(query1,(userid,))
	records = cursor.fetchall()	

	return records

def findproductbykeyword(gtin,userid,isedible):
	gtinfuzzy = "%" + gtin + "%"
	query1 = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,
			p.isperishable,p.isedible,
			case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		LEFT JOIN productsfavourite AS pf
		ON p.gtin = pf.gtin AND pf.userid = %s
		WHERE (p.productname LIKE %s OR
			p.gtin LIKE %s)
	"""
	if validateisedible(isedible) == "2":
		query1 += " AND p.isedible != %s"
	else:
		query1 += " AND p.isedible = %s"
	query1 += """
		GROUP BY 1,2,3,4,5,6,7
		LIMIT 10
	"""
	cursor.execute(query1,(userid,gtinfuzzy,gtinfuzzy,validateisedible(isedible)))
	records = cursor.fetchall()

	return records

def findproductbygtin(gtin,userid):
	query = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,
			p.isperishable,p.isedible,
			case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		LEFT JOIN productsfavourite as pf
		ON p.gtin = pf.gtin AND pf.userid = %s
		WHERE p.gtin = %s 
		GROUP by 1,2,3,4,5,6,7
		ORDER BY 2
	"""
	cursor.execute(query,(userid,gtin))
	records = cursor.fetchall()

	return records

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
		ORDER BY i.dateexpiry ASC
		LIMIT 1
	"""
	cursor.execute(query1,(uid,gtin))
	records = cursor.fetchall()
	if records:
		retailerid = records[0][0]
		dateexpiry = records[0][1]
		if dateexpiry is None:
			dateexpiry = defaultdateexpiry
		return retailerid,dateexpiry
	else:
		return "",defaultdateexpiry

def determineproductcat(productname):
	query1 = """
		SELECT
			metadataname,
			COUNT(*) AS freq
		FROM (
			SELECT
				dl.listingurl,
				dl.listingtitle,
				dm.metadataname,
				dm.metadatatype,
				MATCH(listingtitle) AGAINST (%s IN BOOLEAN MODE) AS score
			FROM deals_listings AS dl
			JOIN deals_listingmetadata AS dlm
			ON dl.listingurl = dlm.listingurl
			JOIN deals_metadata AS dm
			ON dlm.metadatauri = dm.metadatauri
			WHERE
				dm.metadatatype IN ('tag','cat') AND
				MATCH(listingtitle) AGAINST (%s IN BOOLEAN MODE)
			ORDER BY score DESC
			LIMIT 50
		) AS tmp
		GROUP BY 1
		ORDER BY 2 DESC
		LIMIT 1
	"""
	cursor.execute(query1,(productname,productname))
	records = cursor.fetchall()
	category = ""
	for record in records:
		category = record[0]

	return category

def fetchinventoryexpireditems(uid):
	query1 = """
		SELECT
			gtin, productname, productimage, brandname, isedible, isfavourite,
			itemstotal, dateexpiry, retailers,
			itemgoodness
		FROM
		(
			SELECT
			  i.gtin,p.productname,p.productimage,b.brandname,p.isedible,
			  case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			  i.dateexpiry,
			  case
					when dateexpiry <= NOW() then 'expired'
					when NOW() < dateexpiry AND dateexpiry <= NOW() + INTERVAL 30 DAY then 'expiring'
					ELSE 'can-keep'
				END AS itemgoodness,
			  GROUP_CONCAT(distinct(r.retailername)) AS retailers,
			  SUM(case when i.itemstatus = 'IN' then i.quantity else i.quantity*-1 END) AS itemstotal
			FROM inventories AS i
			JOIN products AS p
			ON i.gtin = p.gtin
			JOIN brands AS b
			ON p.brandid = b.brandid
			JOIN retailers AS r
			ON i.retailerid = r.retailerid
			LEFT JOIN productsfavourite as pf
			ON i.gtin = pf.gtin AND i.userid = pf.userid
			WHERE
				i.userid = %s AND p.isedible = '1'
				AND dateexpiry IS NOT NULL AND dateexpiry != '0000-00-00'
			GROUP BY 1,2,3,4,5,6,7,8
		) AS tmp
		WHERE itemstotal > 0 AND itemgoodness IN ('expired','expiring')
		ORDER BY 7 asc
	"""
	cursor.execute(query1,(uid,))
	records = cursor.fetchall()
	expiringcnt 	= 0
	expiredcnt 		= 0
	expiringrecords = []
	expiredrecords 	= []
	for record in records:
		goodness 	= record[9]
		itemstotal 	= record[6]
		if goodness == 'expiring':
			expiringrecords.append(record)
			expiringcnt += math.ceil(itemstotal)
		elif goodness == 'expired':
			expiredrecords.append(record)
			expiredcnt += math.ceil(itemstotal)

	data = {}
	data['expiring'] = {'count': math.ceil(expiringcnt), 'results': expiringrecords}
	data['expired'] = {'count': math.ceil(expiredcnt), 'results': expiredrecords}		
	return data

def findproductimage(gtin,productname):

	productimage = ""
	try:
		source = "google"
		url = "https://www.google.com/search?q=%s&tbm=isch" % productname 
		randagent = random.choice(useragents)
		headers = {'User-Agent': randagent}
		r = requests.get(url, headers=headers, timeout=10)
		html = r.content.decode('utf-8')

		type = "productimage"
		regex = r"\[\"(http.+?\.(?:jpg|jpeg|png))\","
		images = re.findall(regex, html)
		rank = 1
		for imageurl in images:
			id = hashlib.md5(imageurl.encode('utf-8')).hexdigest()
			query1 = "REPLACE INTO productscandidate (gtin,source,type,candidateid,candidatetitle,candidateurl,candidaterank) VALUES (%s,%s,%s,%s,%s,%s,%s)"
			cursor.execute(query1,(gtin,source,type,id,productname,imageurl,rank))
			db.commit()

			rank += 1

			if productimage == "":
				productimage = imageurl

	except requests.ConnectionError as e:
		logging.debug("error: internet connection for [%s] [%s]" % (url,str(e)))
	except requests.Timeout as e:
		logging.debug("error: timeout for [%s] [%s]" % (url,str(e)))
	except requests.RequestException as e:
		logging.debug("error: [%s] [%s]" % (url,str(e)))
	except:
		logging.debug("error: unknown [%s]" % url)	

	return productimage

def fetchinventorybyuser(uid,isedible,isopened):
	query1 = """
		SELECT 
			gtin, productname, productimage, brandname, isedible, isfavourite,
			itemstotal, dateexpiry, retailers,
			CASE
				when MOD(itemstotal*2,2) != 0 AND itemstotal = 0.5 then 'OPENED'
				when MOD(itemstotal*2,2) != 0 AND itemstotal > 0.5 then 'OPENED+NEW'
				when MOD(itemstotal*2,2) = 0 then 'NEW'
			END AS itemstatus
		FROM (
			SELECT
			  i.gtin,p.productname,p.productimage,b.brandname,p.isedible,
			  case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			  max(i.dateexpiry) as dateexpiry,
			  GROUP_CONCAT(distinct(r.retailername)) AS retailers,
			  SUM(case when i.itemstatus = 'IN' then i.quantity else i.quantity*-1 END) AS itemstotal
			FROM inventories AS i
			JOIN products AS p
			ON i.gtin = p.gtin
			JOIN brands AS b
			ON p.brandid = b.brandid
			JOIN retailers AS r
			ON i.retailerid = r.retailerid
			LEFT JOIN productsfavourite as pf
			ON i.gtin = pf.gtin AND i.userid = pf.userid
			WHERE i.userid = %s
		"""
	if validateisedible(isedible) == "2":
		query1 += " AND p.isedible != %s"
	else:
		query1 += " AND p.isedible = %s"	
	query1 += """
			GROUP BY 1,2,3,4,5,6
			ORDER BY 2 ASC
		) AS X
		WHERE itemstotal > 0
	"""
	cursor.execute(query1,(uid,isedible))
	records = cursor.fetchall()

	ediblenewcnt = 0
	edibleopenedcnt = 0 
	inediblenewcnt = 0
	inedibleopenedcnt = 0
	ediblenewrecords = []
	edibleopenedrecords = []
	inediblenewrecords = []
	inedibleopenedrecords = []
	for record in records:
		gtin 			= record[0]
		productname 	= record[1]
		productimage 	= record[2]
		brandname 		= record[3]
		isedible 		= record[4]
		isfavourite		= record[5]
		itemstotal 		= record[6]
		dateexpiry		= record[7]
		retailers		= record[8]
		itemstatus 		= record[9]

		if(isedible == 1 and itemstatus == "NEW"):
			ediblenewcnt += itemstotal
			ediblenewrecords.append(record)
		elif(isedible == 1 and itemstatus == "OPENED"):
			edibleopenedcnt += 1
			edibleopenedrecords.append(record)
		elif(isedible == 0 and itemstatus == "NEW"):
			inediblenewcnt += itemstotal
			inediblenewrecords.append(record)
		elif(isedible == 0 and itemstatus == "OPENED"):
			inedibleopenedcnt += 1
			inedibleopenedrecords.append(record)
		elif(isedible == 1):
			itemstotal -= 0.5
			ediblenewcnt += itemstotal
			edibleopenedcnt +=1
			ediblenewrecords.append(record)
			edibleopenedrecords.append(record)
		elif(isedible == 0):
			itemstotal -= 0.5
			inediblenewcnt += itemstotal
			inedibleopenedcnt +=1
			inediblenewrecords.append(record)
			inedibleopenedrecords.append(record)

	edible = {}
	edible['opened'] = {'count': int(edibleopenedcnt), 'results': edibleopenedrecords}
	edible['new'] = {'count': int(ediblenewcnt), 'results': ediblenewrecords}
	inedible = {}
	inedible['opened'] = {'count': int(inedibleopenedcnt), 'results': inedibleopenedrecords}
	inedible['new'] = {'count': int(inediblenewcnt), 'results': inediblenewrecords}
	
	data = {}
	data['edible'] = edible
	data['inedible'] = inedible

	if validateisopened(isopened) == 0:
		data['all'] = {'count': int(ediblenewcnt) + int(inediblenewcnt), 'results': ediblenewrecords + inediblenewrecords }
	elif validateisopened(isopened) == 1:
		data['all'] = {'count': int(edibleopenedcnt) + int(inedibleopenedcnt), 'results': edibleopenedrecords + inedibleopenedrecords }
	else:
		data['all'] = {'count': int(edibleopenedcnt) + int(ediblenewcnt) + int(inedibleopenedcnt) + int(inediblenewcnt), 'results': records }

	return data

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
	"""
	cursor.execute(query1,(uid,gtin))
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
		ORDER BY b.brandname
	"""
	cursor.execute(query1)
	records = cursor.fetchall()

	return records


def findretailerbykeyword(retailer):
	retailerfuzzy = "%" + retailer + "%"
	query1 = """
		SELECT
			retailerid, retailername
		FROM retailers
		WHERE retailername LIKE %s
	"""
	cursor.execute(query1,(retailerfuzzy,))
	records = cursor.fetchall()

	return records

def findbrandbykeyword(brandid):
	brandfuzzy = "%" + brandid + "%"
	query1 = """
		SELECT
			b.brandid, b.brandname, b.brandimage,
			b.brandurl, b.brandowner,
			count(distinct(p.gtin))
		FROM brands AS b
		LEFT JOIN products as p
		ON b.brandid = p.brandid
		WHERE b.brandname LIKE %s
		GROUP BY 1,2,3,4,5
	"""
	cursor.execute(query1,(brandfuzzy,))
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
		ORDER BY b.brandname
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

def validatebrand(brandid,brandname):
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
		if brandname == "":#DO NOT OVERRIDE IF NAME IS PROVIDED
			brandname = records[0][1]
		return brandid,brandname,"EXISTS"
	elif brandname != "":
		brandidlong = hashlib.md5(brandname.encode('utf-8')).hexdigest()
		brandid = "N_" + brandidlong[:6].upper()
		return brandid,brandname,"NEW"
	else:
		return defaultbrandid,defaultbrandname,"INVALID"

def validatesortby(sortby):
	if sortby == "itemstotal" or sortby == "productname":
		return sortby
	else:
		return "productname"

def finduserbyid(email):
	query1 = """
    	SELECT
        	userid,fullname,passwordhashed
    	FROM users
    	WHERE email = %s
	"""
	cursor.execute(query1,(email,))
	records = cursor.fetchall()
	if records:
		userid = records[0][0]
		fullname = records[0][1]
		passwordhashed = records[0][2]
		return userid,fullname, passwordhashed
	else:
		return "","",""

def validateuser(userid):
	query1 = """
    	SELECT
        	email
    	FROM users
    	WHERE userid = %s
	"""
	cursor.execute(query1,(userid,))
	records = cursor.fetchall()
	if records:
		email = records[0][0]
		return True
	else:
		return False

def validategtin(gtin):
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

def validateitemstatus(itemstatus):
	if itemstatus == "IN" or itemstatus == "OUT":
		return True
	else:
		return False

def validateisedible(isedible):
	try:
		isedible = str(isedible)
		if isedible is None or isedible == "":
			return "2"
		elif isedible == "0" or isedible == "1":
			return str(isedible)
		else:
			return "2"
	except:
		return "2"

def validateisopened(isopened):
	try:
		if int(isopened) == 1 or int(isopened) == 0 or int(isopened) == 2:
			return int(isopened)
		else:
			return 0
	except:
		return 0

def isfloat(quantity):
	if quantity:
	    try:
	        float(quantity)
	        return True
	    except ValueError:
	        return False
	else:
		return False
import datetime
import flask

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
	user = mysqluser, passwd = mysqlpassword, database=mysqldb#,
    #pool_name='sqlpool',
    #pool_size = 6, pool_reset_session = True
   	)
#cursor = db.cursor()

logging.basicConfig(filename=logfile,level=logging.DEBUG)

def _execute(db,query,params):
	cursor_ = None
	try:
		cursor_ = db.cursor()
		if type(params) is tuple:
			cursor_.execute(query,params)
		else:
			cursor_.execute(query)
	except mysql.connector.Error as e:
		db.reconnect(attempts=3, delay=0)
		cursor_ = db.cursor()
		if type(params) is tuple:
			cursor_.execute(query,params)
		else:
			cursor_.execute(query)

	return cursor_

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

def registerapilogs(endpoint, email, flaskreq):
	clientip = flaskreq.access_route[0]
	browser = flaskreq.user_agent.browser
	platform = flaskreq.user_agent.platform
	language = flaskreq.user_agent.language
	referrer = flaskreq.referrer

	eventdate = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	query1 = "INSERT INTO logsapi (endpoint,email,clientip,browser,platform,language,eventdate,referrer) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
	cursor = _execute(db,query1,(endpoint,email,clientip,browser,platform,language,eventdate,referrer))
	db.commit()
	cursor.close()

	return True

def addnewuser(email,fullname,passwordhashed):
	userid = hashlib.md5(email.encode('utf-8')).hexdigest()
	query1 = "INSERT INTO users (userid,fullname,email,passwordhashed) VALUES (%s,%s,%s,%s)"
	cursor = _execute(db,query1,(userid,fullname,email,passwordhashed))
	db.commit()
	cursor.close()

def updatebrandurl(brandid,brandurl):
	query2 = "UPDATE brands SET brandurl = %s WHERE brandid = %s"
	cursor = _execute(db,query2,(brandurl,brandid))
	db.commit()
	cursor.close()

def updatebrandimage(brandid,brandimage):
	query2 = "UPDATE brands SET brandimage = %s WHERE brandid = %s"
	cursor = _execute(db,query2,(brandimage,brandid))
	db.commit()
	cursor.close()

def updatebrandowner(brandid,brandowner):
	#string.capwords(brandowner.strip())
	query2 = "UPDATE brands SET brandowner = %s WHERE brandid = %s"
	cursor = _execute(db,query2,(brandowner.strip(),brandid))
	db.commit()
	cursor.close()

def updatebrandname(brandid,brandname):
	#string.capwords(brandname.strip())
	query2 = "UPDATE brands SET brandname = %s WHERE brandid = %s"
	cursor = _execute(db,query2,(brandname.strip(),brandid))
	db.commit()
	cursor.close()

def updateproductcategories(gtin,categories):
	query2 = "DELETE FROM productscategory WHERE gtin = %s"
	cursor = _execute(db,query2,(gtin,))
	db.commit()
	cursor.close()

	for cat in categories:
		cat = cat.strip()
		query2 = "REPLACE INTO productscategory (gtin,category,status) VALUES (%s,%s,%s)"
		cursor = _execute(db,query2,(gtin,cat,'SELECTED'))
		db.commit()
		cursor.close()

def updateproductbrand(gtin,brandid):
	query2 = "UPDATE products SET brandid = %s WHERE gtin = %s"
	cursor = _execute(db,query2,(brandid,gtin))
	db.commit()
	cursor.close()

def updateproductimage(gtin,productimage):
	query2 = "UPDATE products SET productimage = %s WHERE gtin = %s"
	cursor = _execute(db,query2,(productimage,gtin))
	db.commit()
	cursor.close()

def updateisfavourite(gtin,userid,isfavourite):
	query1 = "REPLACE INTO productsfavourite (gtin,userid) VALUES (%s,%s)"
	cursor = _execute(db,query1,(gtin,userid))
	db.commit()
	cursor.close()

	query2 = "UPDATE productsfavourite SET favourite = %s WHERE gtin = %s AND userid = %s"
	cursor = _execute(db,query2,(isfavourite,gtin,userid))
	db.commit()
	cursor.close()

def updateisedible(gtin,isedible):
	query2 = "UPDATE products SET isedible = %s WHERE gtin = %s"
	cursor = _execute(db,query2,(isedible,gtin))
	db.commit()
	cursor.close()

def updateisperishable(gtin,isperishable):
	query2 = "UPDATE products SET isperishable = %s WHERE gtin = %s"
	cursor = _execute(db,query2,(isperishable,gtin))
	db.commit()
	cursor.close()

def updateproductname(gtin,productname):
	#string.capwords(productname.strip())
	query2 = "UPDATE products SET productname = %s WHERE gtin = %s"
	cursor = _execute(db,query2,(productname.strip(),gtin))
	db.commit()
	cursor.close()

def productalerts_prodnocats(responses):
	###PRODUCT WITHOUT CATEGORIES
	query1 = """
		SELECT 
			p.gtin, p.productname
		FROM products AS p
		LEFT JOIN productscategory AS pc
		ON p.gtin = pc.gtin
		WHERE pc.category IS NULL
	"""
	cursor = _execute(db,query1,None)
	records = cursor.fetchall()
	cursor.close()
	
	response = {}
	response['code'] = 'Non-categorised products' 
	nocatcount = 0
	items = []
	for record in records:
		gtin = record[0]
		productname = record[1]
		nocatcount += 1

		item = {}
		item['gtin'] = gtin
		item['productname'] = productname

		items.append(item)
	response['count'] = nocatcount
	response['items'] = items
	responses.append(response)

	return responses

def productalerts_prodno2ndcat(responses):
	###PRODUCT WITHOUT SECOND CATEGORY
	query1 = """
		SELECT 
			p.gtin, p.productname
		FROM products AS p
		LEFT JOIN productscategory_transpose AS pct
		ON p.gtin = pct.gtin
		WHERE pct.category1 != '' and pct.category2 = ''
	"""
	cursor = _execute(db,query1,None)
	records = cursor.fetchall()
	cursor.close()
	
	response = {}
	response['code'] = 'Products without secondary category' 
	nocatcount = 0
	items = []
	for record in records:
		gtin = record[0]
		productname = record[1]
		nocatcount += 1

		item = {}
		item['gtin'] = gtin
		item['productname'] = productname

		items.append(item)
	response['count'] = nocatcount
	response['items'] = items
	responses.append(response)

	return responses

def productalerts():
	responses = []

	responses = productalerts_prodnocats(responses)
	responses = productalerts_prodno2ndcat(responses)

	return responses

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

def jsonifyfeed(records):
	feed = []
	for record in records:
		gtin 			= record[0]
		productname	  	= record[1]
		productimage  	= record[2]
		brandname	  	= record[3]
		isedible		= record[4]
		isfavourite		= record[5]
		if record[6] is None:
			categories = ''
		else:
			categories = record[6]
		dateentry		= record[7]
		itemstatus      = record[8]
		itemcount		= record[9]

		activity = {}
		activity['gtin'] 			= gtin
		activity['productname'] 	= productname
		activity['productimage']	= productimage
		activity['productimagelocal'] 	= productdir + '/' + gtin + '.jpg'
		activity['brandname']		= brandname
		activity['isedible']		= isedible
		activity['isfavourite']		= isfavourite
		activity['categories']		= categories
		activity['dateentry']		= dateentry.strftime('%Y-%m-%d')
		activity['itemstatus']		= itemstatus
		activity['itemcount']		= itemcount
		feed.append(activity)

	return feed

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

def jsonifycategories(records):
	categories = []
	for record in records:
		category	 	= record[0]
		productcnt  	= record[1]

		cat = {}
		cat['category'] = category
		cat['count'] 	= productcnt

		categories.append(cat)

	return categories		

def jsonifyinventorycategories(records,cattype):
	topcats = fetchtopcats()

	categories = {}
	categoriescnt = {}
	categoriescnthistorical = {}
	for record in records:
		gtin	  		= record[0]
		productname  	= record[1]
		productimage	= record[2]
		brandname   	= record[3]
		isedible	   	= record[4]
		isfavourite	   	= record[5]
		category	   	= record[6]
		dateexpiry 		= record[7]
		itemstotal		= record[8]

		historicaltotal = 0
		if cattype == 'children':
			historicaltotal = record[9]

		item = {}
		item['gtin'] 			= gtin
		item['productname'] 	= productname
		item['productimage'] 	= productimage
		item['productimagelocal'] 	= productdir + '/' + gtin + '.jpg'
		item['brandname'] 	= brandname
		item['isedible'] 	= isedible
		item['category']	= category
		item['isfavourite'] = isfavourite
		item['dateexpiry'] 	= dateexpiry
		item['itemstotal'] 	= itemstotal

		if category in categories:
			categories[category].append(item)
			categoriescnt[category] += math.ceil(itemstotal)
			categoriescnthistorical[category] += math.ceil(historicaltotal)
		else:
			categories[category] = [item]
			categoriescnt[category] = math.ceil(itemstotal)
			categoriescnthistorical[category] = math.ceil(historicaltotal)

	sortedcats = []
	if cattype == 'children':
		categoriesrestockfactor = {}	
		for cat,itemstotal in categoriescnt.items():
			historicaltotal = categoriescnthistorical[cat]
			wilsonsrestockfactor = round((itemstotal+0.5)/historicaltotal, 2)
			categoriesrestockfactor[cat] = wilsonsrestockfactor

		sortedcats = sorted(categoriesrestockfactor.items(), key=lambda x: x[1], reverse=False)
	else:
		sortedcats = sorted(categoriescnt.items(), key=lambda x: x[1], reverse=True)

	categoriesobjects = []
	for catobj in sortedcats:
		cat 				= catobj[0]
		items 				= categories[cat]
		catcntavailable 	= 0
		catcnthistorical 	= 0
		catrestockfactor 	= 0

		if cattype == 'children':
			catrestockfactor = catobj[1]
			catcnthistorical = categoriescnthistorical[cat]
			catcntavailable  = categoriescnt[cat]
		else:
			catcntavailable = catobj[1]

		catobj = {}
		if cattype == 'children' and cat not in topcats:
			catobj['name'] = cat
			catobj['count'] = catcntavailable
			catobj['counthistorical'] = catcnthistorical
			catobj['wilsonsrestockfactor'] = catrestockfactor
			catobj['items'] = items
		elif cattype == 'parents' and cat in topcats:
			catobj['name'] = cat
			catobj['count'] = catcntavailable
			catobj['items'] = items
		
		if len(catobj) > 0:
			if cattype == 'children' and catrestockfactor < 0.5:
				categoriesobjects.append(catobj)
			elif cattype == 'parents':
				categoriesobjects.append(catobj)

	return categoriesobjects

def jsonifyprices(records,retailernames):
	dates = []
	retailercnt = len(retailernames)
	memory = {}
	for name in retailernames:
		memory[name] = 0

	for record in records:
		gtin	  		= record[0]
		productname  	= record[1]
		pricedate		= str(record[2])
		i = 3
		j = 0
		prices = []

		while i < (3 + retailercnt):
			priceval = record[i]
			priceretailer = retailernames[j]

			if priceval == 0 and memory[priceretailer] > 0:
				priceval = memory[priceretailer]

			memory[priceretailer] = priceval
			i += 1
			j += 1

			price = {}	
			price['price'] = priceval
			price['source'] = priceretailer
			prices.append(price)

		datewithprice = {}
		datewithprice['date'] = pricedate
		datewithprice['prices'] =  prices
		dates.append(datewithprice)
		
	return dates	

def jsonifyproducts(records):
	products = []
	for record in records:
		gtin	  		= record[0]
		productname  	= record[1]
		productimage	= record[2]
		brandname   	= record[3]
		isedible	   	= record[4]
		isfavourite	   	= record[5]
		if record[6] is None:
			categories = ''
		else:
			categories = record[6]

		product = {}
		product['gtin'] 			= gtin
		product['productname']		= productname
		product['productimage'] 	= productimage
		product['productimagelocal']= productdir + '/' + gtin + '.jpg'
		product['brandname'] 		= brandname
		product['isedible'] 		= isedible
		product['isfavourite'] 		= isfavourite
		product['categories'] = categories		

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
		if record[6] is None:
			categories = ''
		else:
			categories = record[6]
		itemcount		= record[7]
		dateexpiry		= record[8]
		retailers		= record[9]

		if dateexpiry:
			dateexpiry = dateexpiry.strftime('%Y-%m-%d')

		itemgroup = {}
		itemgroup['gtin'] 			= gtin
		itemgroup['productname']	= productname
		itemgroup['productimage'] 	= productimage
		itemgroup['productimagelocal'] 	= productdir + '/' + gtin + '.jpg'
		itemgroup['brandname'] 		= brandname
		itemgroup['dateexpiry'] 	= dateexpiry
		itemgroup['retailers'] 		= retailers
		itemgroup['itemcount'] 		= itemcount
		itemgroup['isedible'] 		= isedible
		itemgroup['isfavourite'] 	= isfavourite
		itemgroup['categories'] 	= categories

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
	else:
		if isinstance(special, float) or isinstance(special, int):
			message['count'] = special
			message['results'] = None
		else:
			message['count'] = None
			message['results'] = special

	messages.append(message)

	if isinstance(special, dict):
		response = flask.jsonify(messages),statuscode,special
		return response
	else:
		response = flask.jsonify(messages),statuscode
		return response

def pricescrape(url,retailer):
	matchobj = ""

	html,urlresolved = fetchhtml(url)
	soup = bs4.BeautifulSoup(html, 'html.parser')
	rulesdefined = True
	if retailer == 'woolworths': 
		#matchobj = soup.find_all('div',{'class':'price price--large'})
		matchobjtmp = soup.find_all('script',{'type':'application/ld+json'})
		try:
			jsonstr = matchobjtmp[0].text
			jsonobj = json.loads(jsonstr)
			matchobj = str(jsonobj['offers']['price'])
		except:
			matchobj = ""
	elif retailer == 'amazon': 
		matchobj = soup.find_all('span',{'id':'priceblock_ourprice'})		
	elif retailer == 'chemistwarehouse': 
		matchobj = soup.find_all('span',{'class':'product__price'})
	elif retailer == 'drakes': 
		matchobj = soup.find_all('strong',{'class':'MoreInfo__Price'})
	elif retailer == 'bigw': 
		#matchobj = soup.find_all('span',{'id':'product_online_price'})
		matchobj = re.findall('<meta name="twitter:data1" content="(.+?)"', html, re.IGNORECASE)
	elif retailer == 'allysbasket': 
		matchobj = soup.find_all('span',{'itemprop':'price'})
	elif retailer == 'buyasianfood': 
		matchobj = soup.find_all('span',{'class':'price'})
	elif retailer == 'myasiangrocer': 
		matchobj = soup.find_all('span',{'class':'price'})
	elif retailer == 'priceline': 
		matchobj = re.findall('<meta name="twitter:data1" content="(.+?)"', html, re.IGNORECASE)
	elif retailer == 'igashop': 
		matchobj = soup.find_all('span',{'class':'woocommerce-Price-amount amount'})		
	elif retailer == 'amcal': 
		matchobj = soup.find_all('span',{'class':'price'})
	elif retailer == 'winc': 
		matchobj = soup.find_all('span',{'class':'price_text'})
	elif retailer == 'goodpricepharmacy': 
		matchobj = soup.find_all('span',{'class':'price'})
	elif retailer == 'officeworks': 
		matchobj = re.findall('"edlpPrice":"(.+?)"', html, re.IGNORECASE)
	elif retailer == 'superpharmacy': 
		matchobj = soup.find_all('span',{'class':'price promo-price'})	
	elif retailer == 'harrisfarm': 
		matchobj = soup.find_all('span',{'class':'from_price'})
	elif retailer == 'yourdiscountchemist': 
		matchobj = soup.find_all('span',{'class':'price'})
	elif retailer == 'tastefuldelights': 
		matchobj = soup.find_all('span',{'class':'product-price'})
	elif retailer == 'discountchemist': 
		matchobj = soup.find_all('span',{'class':'woocommerce-Price-amount amount'})
	elif retailer == 'asiangrocerystore': 
		matchobj = soup.find_all('span',{'id':'line_discounted_price_126'})
	elif retailer == 'mysweeties': 
		matchobj = soup.find_all('span',{'id':'productPrice'})
	elif retailer == 'chempro': 
		matchobj = soup.find_all('span',{'itemprop':'price'})
	elif retailer == 'yinyam': 
		matchobj = soup.find_all('div',{'class':'price--main'})		
	elif retailer == 'pharmacydirect': 
		matchobj = soup.find_all('span',{'id':'price-display'})	
	elif retailer == 'savourofasia': 
		matchobj = soup.find_all('span',{'itemprop':'price'})
	elif retailer == 'snackaffair': 
		matchobj = soup.find_all('p',{'class':'price'})		
	elif retailer == 'cincottachemist': 
		matchobj = soup.find_all('span',{'id':'price-display'})
	elif retailer == 'iganathalia': 
		matchobj = soup.find_all('strong',{'class':'MoreInfo__Price'})
	elif retailer == 'hongyi': 
		matchobj = re.findall('<meta property="og:price:amount" content="(.+?)"', html, re.IGNORECASE)
	elif retailer == 'yahwehasiangrocery': 
		matchobj = soup.find_all('span',{'class':'ProductPrice VariationProductPrice'})
	elif retailer == 'pharmacyonline': 
		matchobj = soup.find_all('span',{'class':'price-wrapper price'})
	elif retailer == 'indoasiangroceries': 
		matchobj = soup.find_all('p',{'class':'price'})
	elif retailer == 'davidjonespharmacy': 
		matchobj = soup.find_all('div',{'itemprop':'price'})	
	elif retailer == 'aircart': 
		matchobj = soup.find_all('span',{'data-hook':'formatted-primary-price'})
	elif retailer == 'groceryasia': 
		matchobj = soup.find_all('span',{'class':'woocommerce-Price-amount amount'})
	elif retailer == 'g2': 
		matchobj = soup.find_all('span',{'class':'money'})
	elif retailer == 'myer': 
		matchobj = soup.find_all('p',{'data-automation':'product-price-was'})	
	elif retailer == 'asianpantry': 
		matchobj = soup.find_all('span',{'class':'price price--highlight'})
	elif retailer == 'natonic': 
		matchobj = soup.find_all('span',{'class':'price'})
	elif retailer == 'intradco': 
		matchobj = soup.find_all('p',{'class':'price'})
	elif retailer == 'epharmacy': 
		matchobj = soup.find_all('div',{'class':'product__price'})	
	elif retailer == 'theiconic': 
		matchobj = soup.find_all('span',{'class':'price'})
	elif retailer == 'fgb': 
		matchobj = re.findall('<meta itemprop="price" content="(.+?)"', html, re.IGNORECASE)
	elif retailer == 'maizo': 
		matchobj = re.findall('"price":(.+?),', html, re.IGNORECASE)	
	elif retailer == 'ilovehealth': 
		matchobj = soup.find_all('span',{'class':'amount price-new'})
	else:
		rulesdefined = False

	price = '0.0'
	if rulesdefined and matchobj:
		if type(matchobj) == str:
			price = matchobj
		else:
			for match in matchobj:
				if type(match) == str:
					price = match
				else:
					price = match.text
				break

		price = price.replace('\n' , '') 
		price = price.replace('Price:' , '') 
		price = price.replace('$' , '') 
		try:
			test = float(price)
		except:
			price = "0.0"
	elif not rulesdefined:
		errstr = "pricescrape: [no-rules-defined] [%s] [%s]" % (retailer,url)
		print(errstr)
	else:
		errstr = "pricescrape: [defined-rules-broken] [%s] [%s]" % (retailer,url)
		print(errstr)
		logging.debug(errstr)
		logbrokenpricerule(retailer,url)

	return float(price)

def logbrokenpricerule(retailer,url):

	eventdate = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
	scrapedate = datetime.datetime.today().strftime('%Y-%m-%d')

	query1 = "INSERT INTO logsprice (retailer,url,eventdate,scrapedate) VALUES (%s,%s,%s,%s)"
	cursor = _execute(db,query1,(retailer,url,eventdate,scrapedate))
	db.commit()
	cursor.close()

def addproductcandidate(type,source,gtin,title,url,rank):
	id = hashlib.md5(title.encode('utf-8')).hexdigest()
	eventdate1 = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	query1 = "REPLACE INTO productscandidate (gtin,source,type,candidateid,candidatetitle,candidateurl,candidaterank,timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
	cursor = _execute(db,query1,(gtin,source,type,id,title,url,rank,eventdate1))
	db.commit()
	cursor.close()

def addnewbrand(brandid,brandname,brandowner,brandimage,brandurl):
	#string.capwords(brandname)
	if brandname != "":
		query2 = "REPLACE INTO brands (brandid,brandname,brandowner,brandimage,brandurl) VALUES (%s,%s,%s,%s,%s)"
		cursor = _execute(db,query2,(brandid,brandname.strip(),brandowner.strip(),brandimage,brandurl))
		db.commit()
		cursor.close()

		return brandid
	else:
		return ""

def addinventoryitem(uid,gtin,retailerid,dateexpiry,itemstatus,quantity,receiptno):
	dateentry = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	if uid != "" and gtin != "" and retailerid != "" and dateentry != "":
		quantity = float(quantity)
		if quantity >= 1.0:
			i = 0
			while i < quantity:
				query1 = "INSERT INTO inventories (userid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno) VALUES (%s,%s,%s,%s,%s,%s,1,%s)"
				cursor = _execute(db,query1,(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,receiptno))
				db.commit()
				cursor.close()
				i += 1#VERY IMPORTANT
		else:#IF quantity = 0.5 (FOR CONSUMPTION ITEMSTATUS=OUT)
			query1 = "INSERT INTO inventories (userid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
			cursor = _execute(db,query1,(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno))
			db.commit()
			cursor.close()

def addnewproduct(gtin,productname,productimage,brandid,isperishable,isedible):
	if productname != "":#and brandid != ""
		query2 = "INSERT INTO products (gtin,productname,productimage,brandid,isperishable,isedible) VALUES (%s,%s,%s,%s,%s,%s)"
		cursor = _execute(db,query2,(gtin,productname.strip(),productimage,brandid,isperishable,isedible))
		db.commit()
		cursor.close()
	
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
		cursor = _execute(db,query2,(retailerid,retailername.strip(),retailercity))
		db.commit()
		cursor.close()

		return retailerid
	else:
		return ""

def removebrand(brandid):
	query1 = "DELETE FROM brands WHERE brandid = %s"
	cursor = _execute(db,query1,(brandid,))
	db.commit()
	cursor.close()
	
def removeproduct(gtin):
	query1 = "DELETE FROM products WHERE gtin = %s"
	cursor = _execute(db,query1,(gtin,))
	db.commit()
	cursor.close()

def fetchhtml(url):
	html = ""
	urlresolved = ""
	try:
		session = requests.Session()
		randagent = random.choice(useragents)
		headers = {'User-Agent': randagent}
		r = session.get(url, headers=headers, timeout=10)
		#cookie = dict(r.cookies)
		#print(cookie)
		#r = session.get(url, cookies=cookie)
		
		urlresolved = r.url
		html = r.content.decode('utf-8')
		if html == '':
			errstr = "fetchhtml: [error-empty-page] [%s]" % (url)
			logging.debug(errstr)

	except requests.ConnectionError as e:
		errstr = "fetchhtml: [error-connection] [%s] [%s]" % (url,str(e))
		logging.debug(errstr)
	except requests.Timeout as e:
		errstr = "fetchhtml: [error-timeout] [%s] [%s]" % (url,str(e))
		logging.debug(errstr)
	except requests.RequestException as e:
		errstr = "fetchhtml: [error-request] [%s] [%s]" % (url,str(e))
		logging.debug(errstr)
	except BaseException as e:
		errstr = "fetchhtml: [error-unknown] [%s] [%s]" % (url,str(e))
		logging.debug(errstr)

	return html,urlresolved

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

		html,urlresolved = fetchhtml(url)

		if html == '':
			errstr = "downloadproductpages: [error-searchengine-resultspage] [%s] [%s] [%s]" % (gtin,engine,urlresolved)
			print(errstr)
			logging.debug(errstr)

		soup = bs4.BeautifulSoup(html, 'html.parser')
		results = []
		if engine == 'google':
			results = soup.find_all('div',{'class':'g'})#previously class="r"
		elif engine == 'bing':
			results = soup.find_all('li',{'class':'b_algo'})

		type = "productname"
		i = 1
		for result in results:
			resulttitle = ""
			resultlink = ""
			if engine == 'google':
				listhead = result.find('h3')
				if listhead:
					resulttitle = listhead.text
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

			addproductcandidate(type,engine,gtin,resulttitle,resultlink,i)
			i += 1

		if selectedurl == "":
			selectedurl = firsturl
			selectedtitle = firsttitle

		selectedtitle = string.capwords(selectedtitle.strip())
		return selectedurl,selectedtitle
	except requests.ConnectionError as e:
		errstr = "downloadproductpages: [error-connection] [%s] [%s]" % (url,str(e))
		print(errstr)
		logging.debug(errstr)
	except requests.Timeout as e:
		errstr = "downloadproductpages: [error-timeout] [%s] [%s]" % (url,str(e))
		print(errstr)
		logging.debug(errstr)
	except requests.RequestException as e:
		errstr = "downloadproductpages: [error-request] [%s] [%s]" % (url,str(e))
		print(errstr)
		logging.debug(errstr)
	except BaseException as e:
		errstr = "downloadproductpages: [error-unknown] [%s] [%s]" % (url,str(e))
		print(errstr)
		logging.debug(errstr)

	return "ERR",""

def downloadproductpricepages(gtin,productname):
	engine = "google"
	type = "productprice"

	query2 = "DELETE FROM productscandidate WHERE gtin = %s AND source = %s AND type = %s"
	cursor = _execute(db,query2,(gtin,engine,type))
	db.commit()
	cursor.close()

	url = "https://www.google.com/search?q=%s" % urllib.parse.quote(productname)

	html,urlresolved = fetchhtml(url)
	soup = bs4.BeautifulSoup(html, 'html.parser')
	results = soup.find_all('div',{'class':'g'})#previously class="r"

	i = 1
	for result in results:
		listhead = result.find('h3')
		if listhead:
			resulttitle = listhead.text
			resultlink  = result.find('a').get('href', '')

			if resultlink != '#' and resultlink != '':
				addproductcandidate(type,engine,gtin,resulttitle,resultlink,i)
		i += 1

def downloadproductimage(gtin,productname,productimage):
	imageloc = imagepath + gtin + '.jpg'
	try:
		opener=urllib.request.build_opener()
		opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
		urllib.request.install_opener(opener)
		urllib.request.urlretrieve(productimage, imageloc)

		image = Image.open(imageloc)
		image.thumbnail((300,300), Image.ANTIALIAS)
		image.save(imageloc, "jpeg")

		return True
	except:
		with open(imagepath + "error.log", "a") as errfile:
			errfile.write("[%s][%s]\n\n" % (productname, productimage))
		return False

def discovernewproduct(gtin,attempt):
	preferredsources = ["https:\/\/(?:world|world\-fr|au|fr\-en|ssl\-api)\.openfoodfacts\.org","https:\/\/www\.campbells\.com\.au","https:\/\/www\.ebay\.com"]

	searchengine = "google"
	if attempt == 2:
		searchengine = "bing"

	attempt += 1
	selectedurl,selectedtitle = downloadproductpages(gtin,searchengine,preferredsources)
	if selectedurl != "ERR" and selectedurl != "":
		selectedhtml = ""
		try:
			selectedhtml,urlresolved = fetchhtml(selectedurl)

		except BaseException as e:
			errstr = "discovernewproduct: [error-productpage-notfetched] [%s] [%s]" % (selectedurl,str(e))
			print(errstr)
			logging.debug(errstr)

			selectedurl,selectedtitle = downloadproductpages(gtin,"bing",preferredsources)
			if selectedurl != "ERR" and selectedurl != "":
				selectedhtml,urlresolved = fetchhtml(selectedurl)

		if selectedhtml != "":
			soup = bs4.BeautifulSoup(selectedhtml, 'html.parser')

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
		errstr = "discovernewproduct: [ok-noproductpage-retry] [%s] [%s]" % (gtin,attempt)
		print(errstr)
		logging.debug(errstr)

		productname,brandid,brandname = discovernewproduct(gtin,attempt)
		return productname,brandid,brandname
	elif selectedurl == "":
		errstr = "discovernewproduct: [error-noproductpage-retried-failed] [%s] [%s]" % (gtin,attempt)
		print(errstr)
		logging.debug(errstr)

		return "WARN","",""
	else:
		errstr = "discovernewproduct: [error-productpage-unknown] [%s] [%s]" % (gtin,attempt)
		print(errstr)
		logging.debug(errstr)

		return "ERR","",""

def generateshoppinglistbycat(userid):
	query1 = """
		SELECT
		  i.gtin,p.productname,p.productimage,b.brandname,p.isedible,
		  case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
		  pc.category,
		  max(i.dateexpiry) as dateexpiry,
		  SUM(case when i.itemstatus = 'IN' then i.quantity else i.quantity*-1 END) AS itemstotal,
		  SUM(case when i.itemstatus = 'IN' then i.quantity ELSE 0 END) AS historicaltotal,
		  max(i.dateentry) AS recentpurchasedate,
		  GROUP_CONCAT(DISTINCT r.retailername ORDER BY r.retailername SEPARATOR ', ') AS retailers
		FROM inventories AS i
		JOIN products AS p
		ON i.gtin = p.gtin
		JOIN brands AS b
		ON p.brandid = b.brandid
		JOIN retailers AS r
		ON i.retailerid = r.retailerid
		JOIN (
			SELECT gtin, category
			FROM(
				SELECT
					gtin,
					category1 AS category
				FROM productscategory_transpose
				WHERE category1 NOT IN (SELECT category FROM productscategory_top)
				UNION
				SELECT
					gtin,
					category2 AS category
				FROM productscategory_transpose
				WHERE category2 NOT IN (SELECT category FROM productscategory_top)
			) AS tmp
			WHERE category IS NOT NULL AND category != ''
			ORDER BY 1 ASC
		) as pc
		ON p.gtin = pc.gtin
		LEFT JOIN productsfavourite AS pf
		ON i.gtin = pf.gtin AND i.userid = pf.userid
		WHERE i.userid = %s AND p.isedible IN (0,1)
		GROUP BY 1,2,3,4,5,6,7
		ORDER BY 10 DESC
	"""
	cursor = _execute(db,query1,(userid,))
	records = cursor.fetchall()	
	cursor.close()

	return records

def countallproducts():
	query1 = """
		SELECT count(*)
		FROM products
	"""
	cursor = _execute(db,query1,None)
	records = cursor.fetchall()
	cursor.close()

	count = records[0][0]

	return count

def getallproducts(userid,isedible):
	query1 = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,
			p.isedible,
			0 AS isfavourite,
			CONCAT(pc.category1, ';', pc.category2) AS categories,
			SUM(case when i.itemstatus = 'IN' then i.quantity ELSE i.quantity*-1 END) AS itemtotal
		FROM inventories AS i
		JOIN products AS p
		ON p.gtin = i.gtin
		JOIN brands AS b
		ON p.brandid = b.brandid	
		LEFT JOIN productscategory_transpose as pc
		ON p.gtin = pc.gtin
		WHERE
	"""
	if userid != '':
		 query1 += "i.userid = '%s'" % (userid)
	else:
		query1 += "i.dateentry BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW()" 
	if validateisedible(isedible) == "2":
		query1 += "AND p.isedible != %s"
	else:
		query1 += "AND p.isedible = %s"
	query1 += """
		GROUP BY 1,2,3,4,5,6,7
		ORDER BY 8 DESC
	"""
	if userid == '':
		query1 += "LIMIT 5"

	cursor = _execute(db,query1,(validateisedible(isedible),))
	records = cursor.fetchall()
	cursor.close()

	return records

def findproductprices(gtin):
	query1 = """
		SELECT
			distinct pp.retailer
		FROM productsprice AS pp
		WHERE pp.gtin = %s
		ORDER BY 1 ASC
	"""
	cursor = _execute(db,query1,(gtin,))
	retailers = cursor.fetchall()
	cursor.close()

	records = []
	retailernames = []
	if len(retailers) > 0:
		query2 = """
			SELECT
				p.gtin,p.productname,
				pp.date,
		"""
		tmpstr = ""
		for retailer in retailers:
			retailerstr = retailer[0]
			tmpstr += "SUM(CASE WHEN pp.retailer = '%s' THEN pp.price ELSE 0 END) AS \"%s\",\n" % (retailerstr,retailerstr)
		tmpstr = re.sub(r",\n$", "", tmpstr)
		query2 += tmpstr
		query2 += """
			FROM products AS p
			JOIN productsprice AS pp
			ON p.gtin = pp.gtin
			WHERE p.gtin = %s
			GROUP BY 1,2,3
			ORDER BY 1 ASC, 3 ASC
		"""
		cursor = _execute(db,query2,(gtin,))
		records = cursor.fetchall()
		cursor.close()
		i = 1
		
		for fieldname in cursor.description:
			retailername = fieldname[0]
			if i > 3:
				retailernames.append(retailername)
			i += 1

	return records,retailernames

def findproductbykeyword(gtin,userid,isedible):
	gtinfuzzy = "%" + gtin + "%"
	query1 = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,
			p.isedible,
			case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			GROUP_CONCAT(DISTINCT pc.category SEPARATOR '; ') AS categories,
			count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		LEFT JOIN productscategory as pc
		ON p.gtin = pc.gtin
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
		GROUP BY 1,2,3,4,5,6
		LIMIT 10
	"""
	cursor = _execute(db,query1,(userid,gtinfuzzy,gtinfuzzy,validateisedible(isedible)))
	records = cursor.fetchall()
	cursor.close()

	return records

def findproductbygtin(gtin,userid):
	query = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,
			p.isedible,
			case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			GROUP_CONCAT(DISTINCT pc.category SEPARATOR '; ') AS categories,
			count(*)
		FROM products AS p
		JOIN brands AS b
		ON p.brandid = b.brandid
		LEFT JOIN productscategory as pc
		ON p.gtin = pc.gtin
		LEFT JOIN productsfavourite as pf
		ON p.gtin = pf.gtin AND pf.userid = %s
		WHERE p.gtin = %s 
		GROUP by 1,2,3,4,5,6
		ORDER BY 2
	"""
	cursor = _execute(db,query,(userid,gtin))
	records = cursor.fetchall()
	cursor.close()

	return records

def fetchcategories():
	query1 = """
		SELECT
			category,count(*)
		FROM productscategory
		WHERE status = 'SELECTED'
		GROUP BY 1
		ORDER BY 2 DESC
	"""
	cursor = _execute(db,query1,None)
	records = cursor.fetchall()	
	cursor.close()

	return records

def findproductexpiry(uid,gtin):
	query1 = """
		SELECT retailerid,dateexpiry,itemstotal
		FROM (
			SELECT
				retailerid,dateexpiry,
				SUM(case when itemstatus = 'IN' then quantity else quantity*-1 END) AS itemstotal
			FROM inventories
			WHERE userid = %s AND gtin = %s
			GROUP BY 1,2
		) AS tmp
		WHERE itemstotal > 0
		ORDER BY dateexpiry ASC
	"""
	cursor = _execute(db,query1,(uid,gtin))
	records = cursor.fetchall()
	cursor.close()

	if records:
		retailerid = records[0][0]
		dateexpiry = records[0][1]
		if dateexpiry is None:
			dateexpiry = defaultdateexpiry
		return retailerid,dateexpiry
	else:
		return "",defaultdateexpiry

def fetchtopcats():
	query1 = """
	SELECT category FROM productscategory_top;	
	"""
	cursor = _execute(db,query1,None)
	records = cursor.fetchall()
	cursor.close()

	topcats = []
	for record in records:
		topcats.append(record[0])

	return topcats

def fetchinventorybyuserbycat(uid):
	query1 = """
		SELECT
			gtin,productname,productimage,brandname,isedible,
			isfavourite,
			category,
			dateexpiry,
			itemstotal
		FROM (
			SELECT
				i.gtin,p.productname,p.productimage,b.brandname,p.isedible,
			  	case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			  	case
					when pc.category IS NOT NULL then pc.category
					ELSE 'Not-Categorised'
				END AS category,
			  	max(i.dateexpiry) as dateexpiry,
			  	SUM(case when i.itemstatus = 'IN' then i.quantity else i.quantity*-1 END) AS itemstotal
			FROM inventories AS i
			JOIN products AS p
			ON i.gtin = p.gtin
			JOIN brands AS b
			ON p.brandid = b.brandid
			LEFT JOIN productscategory AS pc
			ON p.gtin = pc.gtin AND pc.status = 'SELECTED'
			LEFT JOIN productsfavourite as pf
			ON i.gtin = pf.gtin AND i.userid = pf.userid
			WHERE i.userid = %s
			GROUP BY 1,2,3,4,5,6,7
		) as tmp
		WHERE itemstotal > 0
		ORDER BY 9 DESC
	"""
	cursor = _execute(db,query1,(uid,))
	records = cursor.fetchall()
	cursor.close()

	return records

def fetchinventoryexpireditems(uid):
	query1 = """
		SELECT
			gtin, productname, productimage, brandname, isedible,
			isfavourite,
			categories,
			itemstotal, dateexpiry, retailers,
			itemgoodness
		FROM
		(
			SELECT
			  i.gtin,p.productname,p.productimage,b.brandname,p.isedible,
			  case when pf.favourite = 1 then 1 ELSE 0 END AS isfavourite,
			  pc.categories,
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
			LEFT JOIN (
				SELECT gtin,GROUP_CONCAT(DISTINCT category SEPARATOR '; ') AS categories
				FROM productscategory
				GROUP BY 1		
			) as pc
			ON p.gtin = pc.gtin
			LEFT JOIN productsfavourite as pf
			ON i.gtin = pf.gtin AND i.userid = pf.userid
			WHERE
				i.userid = %s AND p.isedible = '1'
				AND dateexpiry IS NOT NULL AND dateexpiry != '0000-00-00'
			GROUP BY 1,2,3,4,5,6,7,8,9
		) AS tmp
		WHERE itemstotal > 0 AND itemgoodness IN ('expired','expiring')
		ORDER BY 9 asc
	"""
	cursor = _execute(db,query1,(uid,))
	records = cursor.fetchall()
	cursor.close()

	expiringcnt 	= 0
	expiredcnt 		= 0
	expiringrecords = []
	expiredrecords 	= []
	for record in records:
		goodness 	= record[10]
		itemstotal 	= record[7]
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
	eventdate = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	productimage = ""
	try:
		source = "google"
		url = "https://www.google.com/search?q=%s&tbm=isch" % urllib.parse.quote(productname) 
		html,urlresolved = fetchhtml(url)

		type = "productimage"
		regex = r"\[\"(http.+?\.(?:jpg|jpeg|png))\","
		images = re.findall(regex, html)
		rank = 1
		for imageurl in images:
			addproductcandidate(type,source,gtin,productname,imageurl,rank)
			rank += 1

			if productimage == "":
				productimage = imageurl

	except requests.ConnectionError as e:
		errstr = "findproductimage: [error-connection] [%s] [%s]" % (url,str(e))
		print(errstr)
		logging.debug(errstr)

	except requests.Timeout as e:
		errstr = "findproductimage: [error-timeout] [%s] [%s]" % (url,str(e))
		print(errstr)
		logging.debug(errstr)

	except requests.RequestException as e:
		errstr = "findproductimage: [error-request] [%s] [%s]" % (url,str(e))
		print(errstr)
		logging.debug(errstr)

	except BaseException as e:
		errstr = "findproductimage: [error-unknown] [%s] [%s]" % (url,str(e))
		print(errstr)
		logging.debug(errstr)

	if productimage != '':
		successful = downloadproductimage(gtin,productname,productimage)

	return productimage

def fetchinventoryfeedbyuser(uid):
	query1 = """
		SELECT
			p.gtin,p.productname,p.productimage,b.brandname,p.isedible,
			pf.favourite,
			pc.categories,
			i.dateentry, i.itemstatus, sum(quantity) as itemcount
		FROM inventories AS i
		JOIN products AS p
		ON i.gtin = p.gtin
		JOIN brands AS b
		ON p.brandid = b.brandid
		LEFT JOIN (
			SELECT gtin,GROUP_CONCAT(DISTINCT category SEPARATOR '; ') AS categories
			FROM productscategory
			GROUP BY 1		
		) as pc
		ON i.gtin = pc.gtin
		LEFT JOIN productsfavourite as pf
		ON i.gtin = pf.gtin AND i.userid = pf.userid
		WHERE i.userid = %s
		GROUP BY 1,2,3,4,5,6,7,8,9
		ORDER BY 8 DESC
		LIMIT 20
	"""
	cursor = _execute(db,query1,(uid,))
	records = cursor.fetchall()
	cursor.close()

	return records

def fetchinventorybyuser(uid,isedible,isopened,category):
	query1 = """
		SELECT 
			gtin, productname, productimage, brandname, isedible,
			isfavourite,
			categories,
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
			  pc.categories,
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
			LEFT JOIN (
				SELECT
					gtin,
					GROUP_CONCAT(DISTINCT category SEPARATOR '; ') AS categories
				FROM productscategory
				GROUP BY 1		
			) as pc
			ON i.gtin = pc.gtin
			LEFT JOIN productsfavourite as pf
			ON i.gtin = pf.gtin AND i.userid = pf.userid
			WHERE i.userid = %s
		"""
	if validateisedible(isedible) == "2":
		query1 += " AND p.isedible != %s"
	else:
		query1 += " AND p.isedible = %s"	
	query1 += """
			GROUP BY 1,2,3,4,5,6,7
			ORDER BY 2 ASC
		) AS X
		WHERE itemstotal > 0
	"""
	if category != "all" and category != "Not-Categorised":
		query1 += "AND (categories LIKE '%; " + category + "' OR categories LIKE '" + category + ";%' OR categories = '" + category + "')"
		cursor = _execute(db,query1,(uid,isedible))
	elif category == "Not-Categorised":
		query1 += "AND (categories IS NULL)"
		cursor = _execute(db,query1,(uid,isedible))		
	else:
		cursor = _execute(db,query1,(uid,isedible))
	records = cursor.fetchall()
	cursor.close()

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
		categories		= record[6]
		itemstotal 		= record[7]
		dateexpiry		= record[8]
		retailers		= record[9]
		itemstatus 		= record[10]

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
	cursor = _execute(db,query1,(uid,gtin))
	records = cursor.fetchall()
	cursor.close()

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
	cursor = _execute(db,query1,None)
	records = cursor.fetchall()
	cursor.close()

	return records


def findretailerbykeyword(retailer):
	retailerfuzzy = "%" + retailer + "%"
	query1 = """
		SELECT
			retailerid, retailername
		FROM retailers
		WHERE retailername LIKE %s
	"""
	cursor = _execute(db,query1,(retailerfuzzy,))
	records = cursor.fetchall()
	cursor.close()

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
	cursor = _execute(db,query1,(brandfuzzy,))
	records = cursor.fetchall()
	cursor.close()

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
	cursor = _execute(db,query,(brandid,))
	records = cursor.fetchall()
	cursor.close()

	return records

def resolveretailer(retailername):
	query1 = """
    	SELECT
        	retailerid,retailername
    	FROM retailers
    	WHERE lower(retailername) = %s
	"""
	cursor = _execute(db,query1,(retailername.lower(),))
	records = cursor.fetchall()
	cursor.close()

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
	cursor = _execute(db,query1,(brandid,brandname.lower()))
	records = cursor.fetchall()
	cursor.close()

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
	cursor = _execute(db,query1,(email,))
	records = cursor.fetchall()
	cursor.close()

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
	cursor = _execute(db,query1,(userid,))
	records = cursor.fetchall()
	cursor.close()

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
		cursor = _execute(db,query1,(gtin,))
		records = cursor.fetchall()
		cursor.close()

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
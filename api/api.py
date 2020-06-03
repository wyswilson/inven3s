import datetime
import flask

import func
import validate_email
import flask_cors
import json

app = flask.Flask(__name__)#template_dir = os.path.abspath(flasktemplatedir) <=> static_url_path='',static_folder=template_dir,template_folder=template_dir
app.config['JSON_SORT_KEYS'] = False
flask_cors.CORS(app,
	resources={r"*": {"origins": "*"}},
	expose_headers=['Access-Token','Name'],
	support_credentials=True)

#403#Forbidden
#404#Not Found
#412#Precondition Failed
#503#Service Unavailable
#501#Not Implemented
#401#Unauthorized

@app.route('/user/validate/<token>', methods=['GET'])
def uservalidate(token):
	print('hit [uservalidate] with [%s]' % (token))

	valid, userid, username = func.validatetoken(token)
	if valid:
		return func.jsonifyoutput(200,"login successful",[],{'Access-Token': token, 'Name': username})
	else:
		return func.jsonifyoutput(401,"unable to verify identity",[],{'WWW.Authentication': 'Basic realm: "login required"'})			

@app.route('/user/login', methods=['POST'])
def userlogin():
	print('hit [userlogin]')

	auth = flask.request.authorization
	email = auth.username
	password = auth.password

	if not auth or not email or not password:
		return func.jsonifyoutput(401,"unable to verify identity",[],{'WWW.Authentication': 'Basic realm: "login required"'})	
	userid,username,passwordhashed = func.finduserbyid(email)
	if userid != "" and func.checkpassword(passwordhashed,password):
		token = func.generatejwt(userid,username)
		tokenstr = token.decode('UTF-8')
		return func.jsonifyoutput(200,"login successful",[],{'Access-Token': tokenstr, 'Name': username})
	else:
		return func.jsonifyoutput(401,"unable to verify identity",[],{'WWW.Authentication': 'Basic realm: "login required"'})	
		#return flask.make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

@app.route('/user/register', methods=['POST'])
def usersadd():
	print('hit [usersadd]')

	data 		= json.loads(flask.request.get_data().decode('UTF-8'))
	email 		= data["email"]
	password 	= data["password"]

	#,use_blacklist=True check_mx=True, from_address='wyswilson@live.com', helo_host='my.host.name', smtp_timeout=10, dns_timeout=10, 
	if validate_email.validate_email(email_address=email, check_regex=True):
		try:
			func.addnewuser(email,func.generatehash(password))
			return func.jsonifyoutput(200,"user registered successfully",[])
		except:
			return func.jsonifyoutput(403,"user is already registered",[])
	else:
		return func.jsonifyoutput(412,"invalid user email - try again",[])
	
@app.route("/")
@func.requiretoken
def main():
	print('hit [main]')

	status = "invalid endpoint"
	statuscode = 501#Not Implemented

	return jsonifyoutput(statuscode,status,[])

@app.route('/product/<gtin>', methods=['DELETE'])
@func.requiretoken
def productdelete(userid,gtin):
	print('hit [productdelete] with [%s,%s]' % (userid,gtin))

	status = ""
	statuscode = 200
	records = []

	gtin,productname,gtinstatus = func.validategtin(gtin)
	if gtinstatus == "EXISTS":
		try:
			func.removeproduct(gtin)
			status = "product deleted"
		except:
			status = "products attached to inventory - unable to delete"
			statuscode = 403#Forbidden
	else:
		status = "invalid gtin"
		statuscode = 412#Precondition Failed

	records = func.findproductbygtin(gtin)
	return func.jsonifyoutput(statuscode,status,func.jsonifyproducts(records))

@app.route('/product', methods=['POST'])
@func.requiretoken
def productupsert(userid):
	print('hit [productupsert] with [%s]' % (userid))

	status = ""
	statuscode = 200
	records = []

	data 		= json.loads(flask.request.get_data().decode('UTF-8'))
	gtin 		= data["gtin"]
	productname = data["productname"]
	productimage= data["productimage"]
	brandname	= data["brandname"]
	isperishable= data["isperishable"]
	isedible	= data["isedible"]

	gtin,productname_old,gtinstatus = func.validategtin(gtin)
	if gtinstatus == "EXISTS":

		#TRY TO FETCH IMAGE URL IF PRODUCTNAME EXIsTS BUT NOT PRODUCTIMG
		if productname != '' and productimage == '':
			productimage = func.findproductimage(productname)
			print("NEED WORK HERE - SCRAPE PRODUCT IMG")

		if productname != '':
			func.updateproductname(gtin,productname)
			status = status + "productname "
		if isperishable != '':
			func.updateisperishable(gtin,isperishable)
			status = status + "isperishable "
		if isedible != '':
			func.updateisedible(gtin,isedible)
			status = status + "isedible "
		if productimage != '':
			func.updateproductimage(gtin,productimage)
			status = status + "productimage "
		if brandname != '':
			brandid,brandname,brandstatus = func.validatebrand("",brandname.strip())
			if brandstatus == 'NEW':
				brandid = func.addnewbrand(brandid,brandname,"","","")
			func.updateproductbrand(gtin,brandid)

			status = status + "brandname "
		if status != "":
			status = status + "updated"
		else:
			status = "no updates"

		records = func.findproductbygtin(gtin)
	elif gtinstatus == "NEW" and productname != "":
		brandid,brandname,brandstatus = func.validatebrand("",brandname)
		if brandstatus == 'NEW':
			brandid = func.addnewbrand(brandid,brandname,"","","")
		gtin = func.addnewproduct(gtin,productname,productimage,brandid,0,1)	

		records = func.findproductbygtin(gtin)
		status = "new product (and branded) added"
	elif gtinstatus == "NEW" and productname == "":
		productname,brandid,brandnamenotused = func.discovernewproduct(gtin,1)
		if productname != "ERR" and productname != "WARN":
			if productname != "" and brandid != '':
				status = status + "new product and brand discovered and added"
			elif productname != "":
				status = status + "new product discovered and added without brand"

			records = func.findproductbygtin(gtin)
		elif productname == "ERR":
			status = "public search for product errored - try again later"
			statuscode = 503#Service Unavailable
		elif productname == "WARN":
			status = "public search for product returned no data - manual entry required"
			statuscode = 404#Not Found
	else:
		status = "invalid gtin"
		statuscode = 412#Precondition Failed

	return func.jsonifyoutput(statuscode,status,func.jsonifyproducts(records))

@app.route('/product/discover/<gtin>', methods=['GET'])
@func.requiretoken
def productdiscover(userid,gtin):
	print('hit [productdiscover] with [%s,%s]' % (userid,gtin))

	statuscode = 200
	status = ""
	records = []
	
	gtin,productname_old,gtinstatus = func.validategtin(gtin)
	if gtinstatus == 'NEW':
		productname,brandid,brandname = func.discovernewproduct(gtin,1)
		if productname != "ERR" and productname != "WARN":
			status = 'public search for product is successful'
			records = func.jsonifyproducts(func.findproductbygtin(gtin))
		if productname == "ERR":
			status = "public search for product errored - try again later"
			statuscode = 503#Service Unavailable
		elif productname == "WARN":
			status = "public search for product returned no data - manual entry required"
			statuscode = 404#Not found
	elif gtinstatus == 'INVALID':
		status = 'invalid gtin'
		statuscode = 412#Precondition Failed
	else:
		status = 'product already exists'
		records = func.jsonifyproducts(func.findproductbygtin(gtin))

	messages = {}
	messages['message'] = status
	if len(records) > 0:
		messages['results'] = records

	messagestoplvl = []
	messagestoplvl.append(messages)

	response = flask.jsonify(messagestoplvl),statuscode
	return response

@app.route('/product/<gtin>', methods=['GET'])
@func.requiretoken
def productselect(userid,gtin):
	print('hit [productselect] with [%s,%s]' % (userid,gtin))

	status = ""
	statuscode = 200
	records = []

	isedible = flask.request.args.get("isedible")

	gtin,productname,gtinstatus = func.validategtin(gtin)
	if gtinstatus == "EXISTS":
		records = func.findproductbygtin(gtin)
	elif gtinstatus == "NEW":
		status = "product does not exists"
		statuscode = 404#Not Found
	else:
		records = func.findproductbykeyword(gtin,isedible)
		if records:
			status = "products searched by keyword"
		elif gtinstatus == "INVALID":
			status = "invalid gtin"
			statuscode = 412#Precondition Failed
		else:
			status = "product does not exists"
			statuscode = 404#Not Found

	return func.jsonifyoutput(statuscode,status,func.jsonifyproducts(records))

@app.route('/product', methods=['GET'])
@func.requiretoken
def productselectall(userid):
	print('hit [productselectall] with [%s]' % (userid))

	status = "products returned"
	statuscode = 200

	isedible = flask.request.args.get("isedible")
	
	records = func.findallproducts(isedible)

	return func.jsonifyoutput(statuscode,status,func.jsonifyproducts(records))

@app.route('/brand/<brandid>', methods=['DELETE'])
@func.requiretoken
def branddelete(userid,brandid):
	print('hit [branddelete] with [%s,%s]' % (userid,brandid))

	status = "brand deleted"
	statuscode = 200
	records = []

	brandid,brandname,brandstatus = func.validatebrand(brandid,"")
	if brandstatus == "EXISTS":
		try:
			func.removebrand(brandid)
		except:
			status = "products attached to brand - unable to delete"
			statuscode = 403#Forbidden

		records = func.findbrandbyid(brandid)
	else:
		status = "invalid brandid"
		statuscode = 412#Precondition Failed

	return func.jsonifyoutput(statuscode,status,func.jsonifybrands(records))

@app.route('/brand', methods=['POST'])
@func.requiretoken
def brandupsert(userid):
	print('hit [brandupsert] with [%s]' % (userid))

	status = ""
	statuscode = 200
	records = []

	data 		= json.loads(flask.request.get_data().decode('UTF-8'))
	brandid 	= data["brandid"]
	brandname 	= data["brandname"]
	brandimage	= data["brandimage"]
	brandurl	= data["brandurl"]
	brandowner	= data["brandowner"]

	brandid, brandname, brandstatus = func.validatebrand(brandid,brandname)
	if brandstatus == "EXISTS":
		if brandname != "":
			func.updatebrandname(brandid,brandname)
			status += "brandname "
		if brandowner != "":
			func.updatebrandowner(brandid,brandowner)
			status += "brandowner "
		if brandimage != "":
			func.updatebrandimage(brandid,brandowner)
			status += "brandimage "
		if brandurl != "":
			func.updatebrandurl(brandid,brandurl)
			status += "brandurl "

		if status != "":
			status += "updated"
		else:
			status = "no updates"

		records = func.findbrandbyid(brandid)
	elif brandstatus == "NEW":
		brandid = func.addnewbrand(brandid,brandname,brandowner,brandimage,brandurl)
		records = func.findbrandbyid(brandid)

		status = "new brand added"
	else:
		status = "invalid brandid or brandname"
		statuscode = 412#Precondition Failed

	return func.jsonifyoutput(statuscode,status,func.jsonifybrands(records))

@app.route('/brand/<brandid>', methods=['GET'])
@func.requiretoken
def brandselect(userid,brandid):
	print('hit [brandselect] with [%s,%s]' % (userid,brandid))

	status = ""
	statuscode = 200

	records = func.findbrandbyid(brandid)
	if not records:
		records = func.findbrandbykeyword(brandid)

		status = "brands found with keyword search"
	else:
		status = "brand found with id lookup"

	if not records:
		status = "brand does not exists"
		statuscode = 404#Not Found

	return func.jsonifyoutput(statuscode,status,func.jsonifybrands(records))

@app.route('/brand', methods=['GET'])
@func.requiretoken
def brandselectall(userid):
	print('hit [brandselectall] with [%s]' % (userid))

	status = "brands returned"
	statuscode = 200

	records = func.findallbrands()

	return func.jsonifyoutput(statuscode,status,func.jsonifybrands(records))

@app.route('/inventory', methods=['POST'])
@func.requiretoken
def inventoryupsert(userid):
	print('hit [inventoryupsert] with [%s]' % (userid))

	status = ""
	statuscode = 200
	records = []

	data = json.loads(flask.request.get_data().decode('UTF-8'))
	gtin 		= data["gtin"]
	retailername= data["retailername"]
	dateexpiry	= data["dateexpiry"]#DEFAULT '0000-00-00'
	quantity	= data["quantity"]#DEFAULT '1'
	itemstatus	= data["itemstatus"]#DEFAULT 'IN'
	receiptno	= data["receiptno"]

	inventorycnt = 0
	gtin,productname,gtinstatus = func.validategtin(gtin)
	if gtinstatus != "INVALID" and func.validateuser(userid) and func.isfloat(quantity) and func.validateitemstatus(itemstatus):
		if productname == "":
			productname,brandid,brandnamenotused = func.discovernewproduct(gtin,1)
			if productname == "ERR":
				status = "public search for product errored - try again later"
				statuscode = 503#Service Unavailable
			elif productname == "WARN":
				status = "public search for product returned no data - manual entry required"
				statuscode = 404#Not found

			if productname == "ERR" or productname == "WARN":
				productname = ""

		retailerid,retailername = func.resolveretailer(retailername)
		if retailerid == "" and retailername != "":
			retailerid = func.addnewretailer(retailername,"")
		elif retailername == "" and itemstatus == "IN":
			status = "invalid retailername"
			statuscode = 412#Precondition Failed

		if productname != "" and ((itemstatus == "IN" and retailerid != "") or itemstatus == "OUT"):
			inventorycount = func.countinventoryitems(userid,gtin)
			if itemstatus == "OUT" and inventorycount-float(quantity) < 0:
				status = "unable to register items consumed - inadequate stock in inventory"
				statuscode = 403#Forbidden
			else:
				if itemstatus == "OUT" and (dateexpiry is None or dateexpiry == ""):
					retailerid,dateexpiry = func.findproductexpiry(userid,gtin)
				dateentry = datetime.datetime.today().strftime('%Y-%m-%d')
				func.addinventoryitem(userid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno)
				if itemstatus == "IN":
					status = "product item added to inventory"
				else:
					status = "product item removed (or marked as being consumed) in inventory"

		data = func.fetchinventorybyuser(userid,2,2)
		inventorycnt = data['all']['cnt']
		records = data['all']['records']
	elif gtinstatus == 'INVALID':
		status = "invalid gtin"
		statuscode = 412#Precondition Failed
	elif not func.validateuser(userid):
		status = "invalid user"
		statuscode = 412#Precondition Failed
	elif not func.isfloat(quantity):
		status = "invalid quantity"
		statuscode = 412#Precondition Failed
	elif not func.validateitemstatus(itemstatus):
		status = "invalid itemstatus"
		statuscode = 412#Precondition Failed		
	else:
		status = "unknown error"
		statuscode = 412
		
	if inventorycnt == 0:
		inventorycnt = len(records)

	return func.jsonifyoutput(statuscode,status,func.jsonifyinventory(records),inventorycnt)

@app.route('/inventory', methods=['GET'])
@func.requiretoken
def inventoryselect(userid):
	print('hit [inventoryselect] with [%s]' % (userid))

	status = ""
	statuscode = 200
	records = []

	isedible = flask.request.args.get("isedible")
	isopened = flask.request.args.get("isopened")
	expirystatus = flask.request.args.get("expirystatus")

	inventorycnt = 0
	if func.validateuser(userid) and isedible and isopened:

		if expirystatus == 'expired' or expirystatus == 'expiring':
			data = func.fetchinventoryexpireditems(userid)
			inventorycnt = data[expirystatus]['cnt']
			records = data[expirystatus]['records']			
		else:
			data = func.fetchinventorybyuser(userid,isedible,isopened)
			inventorycnt = data['all']['cnt']
			records = data['all']['records']

		status = "inventory items for the user returned"

		if not records:
			status = "user does not have an inventory"
			statuscode = 404#Not Found
	elif isedible is None or isopened is None:
		status = "require isedible, isopened flags"
		statuscode = 412#Precondition Failed
	else:
		status = "invalid user"
		statuscode = 412#Precondition Failed

	if inventorycnt == 0:
		inventorycnt = len(records)

	return func.jsonifyoutput(statuscode,status,func.jsonifyinventory(records),inventorycnt)

@app.route('/inventory/insights', methods=['GET'])
@func.requiretoken
def inventoryinsights(userid):
	print('hit [inventoryinsights] with [%s]' % (userid))
	statuscode = 200
	
	data1 = func.fetchinventorybyuser(userid,2,2)
	data2 = func.fetchinventoryexpireditems(userid)

	messages = {}
	messages['message'] = 'insights'

	message1 = {}
	message1['expiring'] = data2['expiring']['cnt']
	message1['expired'] = data2['expired']['cnt']
	message1['ediblenew'] = data1['edible']['new']['cnt']
	message1['edibleopened'] = data1['edible']['opened']['cnt']
	message1['inediblenew'] = data1['inedible']['new']['cnt']
	message1['inedibleopened'] = data1['inedible']['opened']['cnt']
	messages['counts'] = message1

	messagestoplvl = []
	messagestoplvl.append(messages)

	response = flask.jsonify(messagestoplvl),statuscode
	return response

@app.route('/retailer/<retailer>', methods=['GET'])
@func.requiretoken
def retailerselect(userid,retailer):
	print('hit [retailerselect] with [%s,%s]' % (userid,retailer))

	status = ""
	statuscode = 200

	records = func.findretailerbykeyword(retailer)
	if not records:
		status = "retailer does not exists"
		statuscode = 404#Not Found
	else:
		status = "retailers found with keyword search"
	
	return func.jsonifyoutput(statuscode,status,func.jsonifyretailers(records))

@app.route('/retailer', methods=['POST'])
@func.requiretoken
def retaileradd(userid):
	print('hit [retaileradd] with [%s]' % (userid))

	status = ""
	statuscode = 200

	data 		= json.loads(flask.request.get_data().decode('UTF-8'))
	newretailer = data["retailername"]

	retailerid, retailername = func.resolveretailer(newretailer)
	if retailerid == '':
		retailerid = func.addnewretailer(retailername)
		records= func.findretailerbykeyword(retailername)
		status = "new retailer added"
	else:
		status = "retailer already exists"

	return func.jsonifyoutput(statuscode,status,func.jsonifyretailers(records))

if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0',port=88)
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=8989)

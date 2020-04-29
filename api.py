import flask
import re
import bs4
import datetime
import urllib
import func

app = flask.Flask(__name__)#template_dir = os.path.abspath(flasktemplatedir) <=> static_url_path='',static_folder=template_dir,template_folder=template_dir
app.config['JSON_SORT_KEYS'] = False

@app.route("/")
@func.requires_auth
def main():
	status = "invalid endpoint"
	statuscode = 501#Not Implemented

	return jsonifyoutput(statuscode,status,[])

@app.route('/products/<gtin>', methods=['DELETE'])
@func.requires_auth
def productdelete(gtin):
	status = ""
	statuscode = 200
	records = []

	gtin,productname,gtinstatus = func.isgtinvalid(gtin)
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

@app.route('/products', methods=['POST'])
@func.requires_auth
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
	
	gtin,productname_old,gtinstatus = func.isgtinvalid(gtin)
	if gtinstatus == "EXISTS":
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
			brandid,brandname,brandstatus = func.isbrandvalid("",brandname.strip())
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
		brandid,brandname,brandstatus = func.isbrandvalid("",brandname)
		if brandstatus == 'NEW':
			brandid = func.addnewbrand(brandid,brandname,"","","")
		gtin = func.addnewproduct(gtin,productname,productimage,brandid,0,1)	

		records = func.findproductbygtin(gtin)
		status = "new product (and branded) added"
	elif gtinstatus == "NEW" and productname == "":
		productname,brandid = func.discovernewproduct(gtin,1)
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

@app.route('/products/<gtin>', methods=['GET'])
@func.requires_auth
def productselect(gtin):
	status = ""
	statuscode = 200
	records = []

	isedible = flask.request.args.get("isedible")

	gtin,productname,gtinstatus = func.isgtinvalid(gtin)
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

@app.route('/products', methods=['GET'])
@func.requires_auth
def productselectall():
	status = "all products returned"
	statuscode = 200

	isedible = flask.request.args.get("isedible")
	
	records = func.findallproducts(isedible)

	return func.jsonifyoutput(statuscode,status,func.jsonifyproducts(records))

@app.route('/brands/<brandid>', methods=['DELETE'])
@func.requires_auth
def branddelete(brandid):
	status = "brand deleted"
	statuscode = 200
	records = []

	brandid,brandname,brandstatus = func.isbrandvalid(brandid,"")
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

@app.route('/brands', methods=['POST'])
@func.requires_auth
def brandupsert():
	status = ""
	statuscode = 200
	records = []

	brandid 	= flask.request.args.get("brandid").strip()
	brandname 	= flask.request.args.get("brandname").strip()
	brandimage 	= flask.request.args.get("brandimage").strip()
	brandurl 	= flask.request.args.get("brandurl").strip()
	brandowner 	= flask.request.args.get("brandowner").strip()

	brandid, brandname, brandstatus = func.isbrandvalid(brandid,brandname)
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

@app.route('/brands/<brandid>', methods=['GET'])
@func.requires_auth
def brandselect(brandid):
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

@app.route('/brands', methods=['GET'])
@func.requires_auth
def brandselectall():
	status = "all brands returned"
	statuscode = 200

	records = func.findallbrands()

	return func.jsonifyoutput(statuscode,status,func.jsonifybrands(records))

@app.route('/inventories/<uid>', methods=['POST'])
@func.requires_auth
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

	gtin,productname,gtinstatus = func.isgtinvalid(gtin)
	if gtinstatus != "INVALID" and func.isuservalid(uid) and func.isfloat(quantity) and func.isitemstatusvalid(itemstatus):
		if productname == "":
			productname,brandid = func.discovernewproduct(gtin,1)
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
			inventorycount = func.countinventoryitems(uid,gtin)
			if itemstatus == "OUT" and inventorycount-float(quantity) < 0:
				status = "unable to register items consumed - inadequate stock in inventory"
				statuscode = 403#Forbidden
			else:
				if itemstatus == "OUT" and (dateexpiry is None or dateexpiry == ""):
					retailerid,dateexpiry = func.findproductexpiry(uid,gtin)
				dateentry = datetime.datetime.today().strftime('%Y-%m-%d')
				func.addinventoryitem(uid,gtin,retailerid,dateentry,dateexpiry,itemstatus,quantity,receiptno)
				if itemstatus == "IN":
					status = "product item added to inventory"
				else:
					status = "product item removed (or marked as being consumed) in inventory"

			records,inventorycount = func.findinventorybyuser(uid,"0,1",0)
			status += " - %s" % inventorycount

	elif not func.isuservalid(uid):
		status = "invalid uid"
		statuscode = 412#Precondition Failed
	elif not func.isfloat(quantity):
		status = "invalid quantity"
		statuscode = 412#Precondition Failed
	elif not func.isitemstatusvalid(itemstatus):
		status = "invalid itemstatus"
		statuscode = 412#Precondition Failed		
	else:
		status = "invalid gtin"
		statuscode = 412#Precondition Failed

	return func.jsonifyoutput(statuscode,status,func.jsonifyinventory(records))

@app.route("/inventories/", methods=['GET','POST'])
@app.route("/inventories", methods=['GET','POST'])
@func.requires_auth
def inventoryselectall():
	status = "invalid uid"
	statuscode = 412#Precondition Failed

	return func.jsonifyoutput(statuscode,status,[])

@app.route('/inventories/<uid>', methods=['GET'])
@func.requires_auth
def inventoryselect(uid):
	status = ""
	statuscode = 200
	records = []

	if func.isuservalid(uid):
		isedible = flask.request.args.get("isedible")
		ispartiallyconsumed = flask.request.args.get("ispartiallyconsumed")

		records,inventorycount = func.findinventorybyuser(uid,isedible,ispartiallyconsumed)

		status = "all inventory items for the user returned - %s" % inventorycount

		if not records:
			status = "uid does not have an inventory"
			statuscode = 404#Not Found
	else:
		status = "invalid uid"
		statuscode = 412#Precondition Failed

	return func.jsonifyoutput(statuscode,status,func.jsonifyinventory(records))

if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0',port=8989)
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=8989)

#403#Forbidden
#404#Not Found
#412#Precondition Failed
#503#Service Unavailable
#501#Not Implemented
import datetime
import flask

import func
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

config = configparser.ConfigParser()
config.read('conf.ini')

apisecretkey	= config['auth']['secretkey']
logfile 		= config['path']['log']
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
	user = mysqluser, passwd = mysqlpassword, database=mysqldb)
cursor = db.cursor()

query1 = """
	SELECT
		gtin,productname
	FROM products
"""
cursor.execute(query1)
records = cursor.fetchall()
category = ""
for record in records:
	gtin 		= record[0]
	productname = record[1]

	query2 = """
		SELECT
			dm.metadataname,
			dm.metadatatype,
			MATCH(listingtitle) AGAINST (%s IN BOOLEAN MODE) AS score,
			COUNT(*)
		FROM deals_listings AS dl
		JOIN deals_listingmetadata AS dlm
		ON dl.listingurl = dlm.listingurl
		JOIN deals_metadata AS dm
		ON dlm.metadatauri = dm.metadatauri
		WHERE
			MATCH(listingtitle) AGAINST (%s IN BOOLEAN MODE)
			AND metadatatype = 'tag'
		GROUP BY 1,2
		ORDER BY 3 DESC, 4 DESC
		limit 10
	"""
	cursor.execute(query2,(productname,productname))
	records2 = cursor.fetchall()
	for record2 in records2:
		metadataname = record2[0]
		metadatatype = record2[1]
		score = record2[2]

		print("[%s][%s][%s][%s]" % (productname,metadataname,metadatatype,score))

		status = 'SUGGESTED'
		query1 = "REPLACE INTO productscategory (gtin,category,confidence,status) VALUES (%s,%s,%s,%s)"
		cursor.execute(query1,(gtin,metadataname,score,status))
		db.commit()
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

query1 = """
	SELECT gtin,productname,productimage FROM products
"""
cursor.execute(query1)
records = cursor.fetchall()
imagepath = "../webapp/public/products/"
for record in records:
	gtin = record[0]
	productname = record[1]
	productimage = record[2]
	if productimage != '':
		opener=urllib.request.build_opener()
		opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
		urllib.request.install_opener(opener)
		imageloc = imagepath + gtin + '.jpg'
		print('downloading [%s][%s]' % (productname,imageloc))
		urllib.request.urlretrieve(productimage, imageloc)

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
import math

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

db1 = mysql.connector.connect(
	host = mysqlhost,
	port = mysqlport,
	user = mysqluser, passwd = mysqlpassword, database=mysqldb,
    pool_name='sqlpool1',
    pool_size = 1, pool_reset_session = True
   	)

cursor9 = db1.cursor()

query1 = """
	SELECT gtin,productname,productimage FROM products
"""
cursor9.execute(query1)
records9 = cursor9.fetchall()
for record in records9:
	gtin = record[0]
	productname = record[1]
	productimage = record[2]
	if productimage != '':
		successful = func.downloadproductimage(gtin,productname,productimage)
		if successful:
			print('downloading [%s][%s]\n' % (productname,productimage))
		else:
			print('error downloading [%s][%s]\n' % (productname,productimage))

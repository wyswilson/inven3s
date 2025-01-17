import datetime
import flask

import func
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
	user = mysqluser, passwd = mysqlpassword, database=mysqldb,
    pool_name='sqlpool',
    pool_size = 6, pool_reset_session = True,
    autocommit=True
   	)

cursor = db.cursor()

query0 = """
	DELETE FROM productscategory_transpose
"""
cursor.execute(query0)
db.commit()

query1 = """
	SET @row_number = 0;
	SET @gtin = '';

	REPLACE INTO 
		productscategory_transpose(gtin,productname,category1,category2)
	SELECT
		gtin,productname,
		GROUP_CONCAT(cat1 SEPARATOR '') AS category1,
		GROUP_CONCAT(cat2 SEPARATOR '') AS category2
	FROM (
		SELECT
			gtin, prodname AS productname,
			CASE
				when rownum = 1 THEN cat
				ELSE ''
			END AS cat1,
			CASE
				when rownum = 2 THEN cat
				ELSE ''
			END AS cat2	
		FROM (
			SELECT
				p.gtin AS gtin,
				p.productname AS prodname,
				pc.category AS cat,
				@row_number:=CASE
				  WHEN @gtin = p.gtin THEN @row_number + 1
				  ELSE 1
				END AS rownum,
				@gtin:=p.gtin AS gtin2
			FROM products AS p
			LEFT JOIN productscategory AS pc
			ON p.gtin = pc.gtin
			GROUP BY 1,2,3
			ORDER BY 3 ASC
		) AS prodswithmultiplecats
	) AS prodswithinlinecats
	GROUP BY 1,2
	ORDER BY 3 ASC;
	COMMIT;
"""
for _ in cursor.execute(query1, multi=True): pass
db.commit()

query0 = """
	SELECT
    	*
	FROM productscategory_transpose
"""
cursor.execute(query0)
records = cursor.fetchall()
print("# of products with categories transposed: %s" % len(records))

query2 = """
	DELETE FROM productscategory_top
"""
cursor.execute(query2)
db.commit()

query3 = """
	REPLACE INTO 
		productscategory_top(category,subcategorycnt)
	SELECT * FROM (
		SELECT category, SUM(catcnt) AS subcatcnt
		FROM(
			SELECT
				category1 AS category,
				COUNT(DISTINCT(category2)) AS catcnt
			FROM productscategory_transpose
			GROUP BY 1
			UNION
			SELECT
				category2 AS category,
				COUNT(DISTINCT(category1)) AS catcnt
			FROM	productscategory_transpose
			GROUP BY 1
		) AS tmp
		GROUP BY 1
		ORDER BY 2 DESC
	) AS topcats
	WHERE subcatcnt > 1 and category != '';
	COMMIT;
"""
for _ in cursor.execute(query3, multi=True): pass
db.commit()

query4 = """
	SELECT
    	category,subcategorycnt
	FROM productscategory_top
"""
cursor.execute(query4)
records = cursor.fetchall()

print("The top parent categories are:")
for record in records:
	category 		= record[0]
	subcategorycnt	= record[1]
	print("[%s] [%s]" % (category,subcategorycnt))
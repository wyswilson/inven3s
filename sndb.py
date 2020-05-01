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
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

mysqlhost = "inven3sdb.ciphd8suvvza.ap-southeast-1.rds.amazonaws.com"
mysqlport = "3363"
mysqluser = "inven3suser"
mysqlpwrd = "P?a&N$3!s"
mysqldb = "inven3s"
apiuser = "inven3sapiuser"
apipwrd = "N0tS3cUr3!"
logfile = "inven3s.log"
emptybrandid = "N_000000"
emptybrandname = "Unavailable"
useragents  = json.loads(config['scraper']['useragents'].replace('\n',''))

print(useragents)
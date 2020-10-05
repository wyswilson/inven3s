import re
import requests
import random
import simplejson as json
import configparser
import func
import bs4

config = configparser.ConfigParser()
config.read('conf.ini')


productname = "Cetaphil Baby Gentle Wash & Shampoo 230ml"
searchurl = "https://www.google.com/search?q=%s" % productname
html,urlresolved = func.fetchhtml(searchurl)
soup = bs4.BeautifulSoup(html, 'html.parser')
results = soup.find_all('div',{'class':'g'})
for result in results:
	print(result)
	resulttitle = result.find('h3').text
	resultlink  = result.find('a').get('href', '')

	print("[%s] [%s]" % (resulttitle,resultlink))
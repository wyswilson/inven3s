import re
import requests
import random
import simplejson as json
import configparser


config = configparser.ConfigParser()
config.read('conf.ini')

useragents 		= json.loads(config['scraper']['useragents'].replace('\n',''))


productname = "Cetaphil Moisturising Cream 550g"
url = "https://www.chemistwarehouse.com.au/searchapi/webapi/search/terms?category=catalog01_chemau&index=0&sort=&term=%s" % (productname)
randagent = random.choice(useragents)
header = {'User-Agent': randagent}
response = requests.get(url, headers=header)
status = response.status_code
print(status)
json = response.json()
obj = json['universes']['universe'][0]['items-section']['items']
print(obj)
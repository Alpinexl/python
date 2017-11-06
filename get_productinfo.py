import sys
import requests
import json
from requests.auth import HTTPBasicAuth
DictProductInfo = {}

b2bi_username='Robert'
b2bi_passwd='Br@mvg2017'

url_productinfo = 'http://l1161o0002.cicapp.nl:6080/api/v1/systemInfo/productInfo'

try:
	response = requests.get(url_productinfo, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
except: 
	print('Unable to execute the REST API to get the productinfo')
else:
	if response.status_code == 200:
        	print('Getting the productInfo')
	else:
        	print('Unable to get productInfo from b2bi. ' + 'Errorcod = ' + str(response.content))
        	sys.exit(1)

resp_payload = json.loads(response.text)

for item in resp_payload:
	if len(item['patches']) == 0:
		print (item['name'] + ' SP' + item['sp'])
	else:
		print (item['name'] + ' SP' + item['sp'] + ' p' + item['patches']) 
		

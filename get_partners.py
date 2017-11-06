import sys
import requests
import json
from requests.auth import HTTPBasicAuth
DictPartner = {}

b2bi_username='Robert'
b2bi_passwd='Br@mvg2017'

url_partners = 'http://l1161o0002.cicapp.nl:6080/api/v1/tradingPartners'

response = requests.get(url_partners, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))

if response.status_code == 200:
        print('Getting the partners')
else:
        print('Unable to get partners from b2bi. ' + 'Errorcod = ' + str(response.content))
        sys.exit(1)
print(response.text)
resp_payload = json.loads(response.text)

for item in resp_payload['results']:
	DictPartner[item['partyName']] = item['@id']
	#print (item['partyName'])
print (DictPartner)

partnerid = DictPartner['Interchange']
response = requests.get(url_partners + '/' + partnerid, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
print (response.text)	


import sys
import csv
import requests
import json
from requests.auth import HTTPBasicAuth

b2bi_username='Robert'
b2bi_passwd='Br@mvg2017'
url_communities = 'http://l1161o0002.cicapp.nl:6080/api/v1/communities'
headers = {'Content-type': 'application/json'}

try:
    response_get = requests.get(url_communities, headers=headers, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
except requests.exceptions.RequestException as e:
    print('Unable to connect to B2Bi: ' + str(e))
    sys.exit(1)

if response_get.status_code == 200:
    resp_payload = json.loads(response_get.text)
    for item in resp_payload['results']:
        response_delete= requests.delete(url_communities + '/' + item['@id'], auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
        if response_delete.status_code in range (200, 206):
            print('Communitie with id ' + item['@id'] + ' removed from B2Bi.')
        else:
            print('Unable to delete communitie with id ' + item['@id'] + '. HTTP code is ' + str(response_delete.status_code))
else:
    print('Unable to get communitie list')
    sys.exit(1)

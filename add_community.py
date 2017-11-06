import sys
import requests
import json
import csv
from requests.auth import HTTPBasicAuth

b2bi_username='Robert'
b2bi_passwd='Br@mvg2017'

headers = {'Content-type': 'application/json'}
url_communities = 'http://l1161o0002.cicapp.nl:6080/api/v1/communities'

def read_csv():

	with open('communities.csv','r') as f:
		reader = csv.reader(f)
		next(reader)
		community_list = list(reader)

	return community_list
		
community_list = read_csv()

for community in community_list:
	name = community[0]
	partyname = community[1]
	email = community[2]
	phone = community[3]
	notes = community[4]
	title = community[5]
	enabled = community[6]
	routingidtype = community[7]
	routingid = community[8]

	data = '{"primaryContact":{"primary": true,"name": "%s","email": "%s","phone": "%s","notes": "%s","title": "%s"},"enabled": %s,"defaultRoutingId":{"type": "%s","routingId": "%s"},"partyName": "%s"}' % (name, email, phone, notes, title, enabled,routingidtype,routingid, partyname)

	print (data)

	response = requests.post(url_communities, data=data, headers=headers, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))

	if response.status_code == 200:
        	print('Communities added to B2Bi!.')
	else:
        	print('Community not added to b2bi. ' + 'Errorcod = ' + str(response.content))
        	sys.exit(1)


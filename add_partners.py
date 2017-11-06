import sys
import csv
import requests
import json
from requests.auth import HTTPBasicAuth

b2bi_username='Robert'
b2bi_passwd='Br@mvg2017'
url_tradingpartner = 'http://l1161o0002.cicapp.nl:6080/api/v1/tradingPartners'
url_communities = 'http://l1161o0002.cicapp.nl:6080/api/v1/communities'
community_ids={}
headers = {'Content-type': 'application/json'}

def set_community_membership(partner_id, community_id):

	url_community_membership = 'http://l1161o0002.cicapp.nl:6080/api/v1/tradingPartners/%s/subscriptions?communityId=%s' % (partner_id, community_id)
	response = requests.post(url_community_membership, headers=headers, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))

	if response.status_code in range (200, 206):
                print('Setting the community membership for partner %s with community %s.' % (partner_id, community_id))
	else:
		print('Unable to set the community membership for partner %s with community %s.' % (partner_id, community_id))
		return False
	
	return True
	
	
def get_community_ids():
	
	response = requests.get(url_communities, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
	
	if response.status_code == 200:
        	print('Getting the communities.')
	else:
        	print('Unable to get community information. ' + 'Errorcod = ' + str(response.error_code))
        	sys.exit(1)
	
	resp_payload = json.loads(response.text)

	for item in resp_payload['results']:
        	community_ids[item['partyName']] = item['@id']
		
	return community_ids

def read_csv():
	# read the csv file and return a list
        with open('partners.csv','r') as f:
                reader = csv.reader(f)
                #skip the header of the csv file
		next(reader)
		partner_list = list(reader)

        return partner_list

partner_list = read_csv()
community_ids_list = get_community_ids()

#loop through the csv file and call the REST API to create a partner and community membership each iteration
for partner in partner_list:

        name = partner[0]
        partyname = partner[1]
        email = partner[2]
        phone = partner[3]
        notes = partner[4]
        title = partner[5]
        enabled = partner[6]
        routingidtype = partner[7]
        routingid = partner[8]
	communitymember = partner[9]

	# set the inout json message
	data = '{"primaryContact":{"primary": true,"name": "%s","email": "%s","phone": "%s","notes": null,"title": null},"enabled": %s,"defaultRoutingId":{"type": "%s","routingId": "%s"},"partyName": "%s"}' % (name, email, phone, enabled, routingidtype, routingid, partyname)

	response = requests.post(url_tradingpartner, headers=headers, data=data, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))

	if response.status_code == 200:
		
		resp_payload = json.loads(response.text)
		print('Partner added to B2Bi. ' + 'Id=' + resp_payload['bean']['@id'])
		
		if community_ids_list.has_key(communitymember):
			
			partner_id = resp_payload['bean']['@id']	
			community_id = community_ids_list.get(communitymember)
			if set_community_membership(partner_id, community_id):
				print('Set the membership for partner %s with community id %s succesfull' % (partner_id, community_id)) 		
			else:
				print('Unable to set membership for partner %s with community id %s' % (partner_id, community_id))	
		else:
			print ('Community member not found in Commmunitylist')

	else:
		print('Partner not added to b2bi. ' + 'Errorcod = ' + str(response.content))
		sys.exit(1)




##################################################################
#
# Author: Robert van Gangelen, Axway BV
# Version: 0.1
# Creation date: 24-10-2017	
# 	
# Run like: python get_productinfo.py
#      example: python get_productinfo.py
# 
# Program is using a ini file. With the same name as 
# the script in the same directory.
# A log file is create with the same name as the program
#
##################################################################

import sys
import requests
import json
from requests.auth import HTTPBasicAuth
from configparser import ConfigParser
from pathlib import Path
import logging

# set the logging
logging.basicConfig(filename='get_productinfo.log',level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')

scriptname = Path(sys.argv[0])
inifilename = scriptname.with_suffix('')
logfilename = scriptname.with_suffix('')
config = ConfigParser()
config.read(str(inifilename) + '.ini')

# read values from a section
try:
    b2bi_server = config['B2Bi']['b2bi_server']
    b2bi_port = config['B2Bi']['b2bi_port']
    b2bi_api_url = config['B2Bi']['b2bi_api_url']
    b2bi_username = config['B2Bi']['b2bi_username']
    b2bi_passwd = config['B2Bi']['b2bi_password']
except KeyError as e:
    logging.error('Unable to find key {} in ini file'.format (str(e)))

# set the url to connect to B2BI
url_productinfo = b2bi_server + ':' + b2bi_port + b2bi_api_url

# if logging is set to DEBUG mode print out the following information for debug purposes
logging.debug('inifilename = {}'.format(inifilename))
logging.debug('logfilename = {}'.format(inifilename))
logging.debug('b2bi_server = {}'.format(b2bi_server))
logging.debug('b2bi_port = {}'.format(b2bi_port))
logging.debug('b2bi_username = {}'.format(b2bi_username))
logging.debug('b2bi_passwd = {}'.format(b2bi_passwd))
logging.debug('url_productinfo = {}'.format(url_productinfo))

try:
	response = requests.get(url_productinfo, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
except requests.exceptions.RequestException as e: 
	logging.error('Unable to execute the REST API to get the B2Bi productinfo. Error: {}'.format (str(e)))
	sys.exit(1)
else:
	if response.status_code == 200:
        	logging.info('Able to get the B2BI productinfo')
	else:
        	logging.error('Unable to get productinfo from B2BI. Error = {}'.format (response.content))
        	sys.exit(1)

resp_payload = json.loads(response.text)

for item in resp_payload:
	if len(item['patches']) == 0:
		logging.info(item['name'] + ' SP' + item['sp'])
		print (item['name'] + ' SP' + item['sp'])
	else:
		logging.info (item['name'] + ' SP' + item['sp'] + ' p' + item['patches'])
		print (item['name'] + ' SP' + item['sp'] + ' p' + item['patches'])
##################################################################
#
# Author: Robert van Gangelen, Axway BV
# Version: 0.1
# Creation date: 24-10-2017 
#   
# Run like: python delete_partners.py
#      example: python delete_partners.py
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
logging.basicConfig(filename='delete_partners.log',level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')

scriptname = Path(sys.argv[0])
inifilename = scriptname.with_suffix('')
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
url_tradingpartner=b2bi_server + ':' + b2bi_port + b2bi_api_url

# if logging is set to DEBUG mode print out the following information for debug purposes
logging.debug('inifilename = {}'.format(inifilename))
logging.debug('b2bi_server = {}'.format(b2bi_server))
logging.debug('b2bi_port = {}'.format(b2bi_port))
logging.debug('b2bi_api_url = {}'.format(b2bi_api_url))
logging.debug('b2bi_username = {}'.format(b2bi_username))
logging.debug('b2bi_passwd = {}'.format(b2bi_passwd))
logging.debug('url_tradingpartner = {}'.format(url_tradingpartner))

# execute the GET request to B2Bi to get the partner information
try:
    response_get = requests.get(url_tradingpartner, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
except requests.exceptions.RequestException as e:
    logging.error('Unable to execute the REST API to delete the B2Bi partners. Error: {}'.format(str(e)))
    sys.exit(1)

# check if the response code is equal to 200 if so read the json file and loop throught the collect the B2Bi partner information 
if response_get.status_code == 200:
    resp_payload = json.loads(response_get.text)
    for item in resp_payload['results']:
        response_delete= requests.delete(url_tradingpartner + '/' + item['@id'], auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
        if response_delete.status_code in range (200, 206):
            logging.info('B2Bi partner with id {} removed from B2Bi.'.format(item['@id']))
        else:
            logging.error('Unable to delete B2Bi partner with id {}. HTTP code is {}'.format(item['@id'], str(response_delete.status_code)))
    else:
        logging.info('No B2Bi partners found to delete')
else:
    logging.error('Unable to get B2Bi partners. HTTP Response code: {}. Please check the user rights'. str(response_delete.status_code))
    sys.exit(1)

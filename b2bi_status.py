####################################################
#
# Author: Robert van Gangelen, Axway BV
# Version: 0.2
# Creation date: 24-10-2017	
# 	
# Run like: python b2bi_status.py
#      example: python b2bi_status.py	
# 
#  When program execution fails it returns exit code 1
#  Program uses ini file for the basic configuration
#  Program uses log file for execution information
#  Log file is located in the same directory as the py file
####################################################

import requests
import smtplib
import sys
from requests.auth import HTTPBasicAuth
import json
from configparser import ConfigParser
from pathlib import Path
import datetime
import logging

# set the logging
logging.basicConfig(filename='b2bi_status.log',level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')

scriptname = Path(sys.argv[0])
inifilename = scriptname.with_suffix('')
config = ConfigParser()
config.read(str(inifilename) + '.ini')
systemnode_status = {}
email = False

# read values from a section
try:
    b2bi_server = config['B2Bi']['b2bi_server']
    b2bi_api_url = config['B2Bi']['b2bi_api_url']
    b2bi_port = config['B2Bi']['b2bi_port']
    b2bi_username = config['B2Bi']['b2bi_username']
    b2bi_passwd = config['B2Bi']['b2bi_password']
    smtp_server = config['Mail']['smtp_server']
    fromaddr = config['Mail']['from_addres']
    toaddr = config['Mail']['to_addres']
except KeyError as e:
    logging.error('Unable to find key {} in ini file'.format (str(e)))
    sys.exit(1)

b2bi_url = b2bi_server + ':' + b2bi_port + b2bi_api_url

# if logging is set to DEBUG mode print out the following information for debug purposes
logging.debug('inifilename = {}'.format(inifilename))
logging.debug('logfilename = {}'.format(inifilename))
logging.debug('b2bi_server = {}'.format(b2bi_server))
logging.debug('b2bi_port = {}'.format(b2bi_port))
logging.debug('b2bi_url = {}'.format(smtp_server))
logging.debug('b2bi_username = {}'.format(b2bi_username))
logging.debug('b2bi_passwd = {}'.format(b2bi_passwd))
logging.debug('smtp_server = {}'.format(smtp_server))
logging.debug('fromaddr = {}'.format(fromaddr))
logging.debug('toaddr = {}'.format(toaddr))

def sendmail(mailserver, fromaddr, toaddr, subject, msg):
    msg = 'From: {}\r\nTo: {}\r\nSubject: {}\r\n\r\n{}'.format(fromaddr, toaddr, subject, msg)
    try:
        server = smtplib.SMTP(mailserver)
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()
    except:
        logging.error('Unable to send email using SMTP server: {}'.format (mailserver))


try:
    response = requests.get(b2bi_url, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
except requests.exceptions.RequestException as e:
    # problems with connecting to the b2bi server and REST API call. Send an email and stop the program with exit code 1
    logging.error('Unable to execute REST API on {}. B2Bi Server not running'.format(b2bi_url))
    sendmail(smtp_server, fromaddr, toaddr, 'B2Bi REST API call failed on server {}'.format(b2bi_server),
             'Unable to execute REST API on {}. B2Bi server not running'.format(b2bi_url))
    sys.exit(1)
else:
    # no problem with the connection lets check the http response code
    if response.status_code == 200:
        # load the response message into a json object
        resp_payload = json.loads(str(response.text))
    else:
        # http response code is not equal to 200. Send an email and stop the program with exit code 1
        subject= 'B2Bi REST API call failed on server {} due to HTTP response code: {}'.format(b2bi_url, str(response.status_code))
        message= 'Unable to execute REST API on {}. Check if the user has the rights to execute the B2Bi REST APIs or the view system status priveleges.'.format(b2bi_url)
        sendmail(smtp_server, fromaddr, toaddr, subject, message)
        logging.error(message)
        sys.exit(1)

    # loop throug the json object and create a dictionary (key, value hashmap) of the type and status fields
    for item in resp_payload:
        systemnode_status[item['type']] = item['status']

    # loop through the systemnode_status dictionary and do a check on the key value pairs
    for k, v in systemnode_status.items():
        if (k == 'CN') or (k == 'TE') or (k == 'B2B'):
            if v.lower() != 'running':
                email = True

        elif (k == "Integration Engine"):
            if v.lower() != 'started':
                email = True

    if email:
        message='B2Bi System nodes on {} not running'.format (b2bi_url)
        sendmail(smtp_server, fromaddr, toaddr, message,
                 str(systemnode_status))
        logging.error(message)
        sys.exit(1)
    else:
        logging.info('B2Bi nodes are running!')
        sys.exit(0)
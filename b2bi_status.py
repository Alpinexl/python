####################################################
#
# Author: Robert van Gangelen, Axway BV
# Version: 0.1
# Creation date: 24-10-2017	
# 	
# Run like: python b2bi_status.py <hostname>
#      example: python b2bi_status.py l1161o0003.cicapp.nl	
#
####################################################

import requests
import smtplib
import sys
from requests.auth import HTTPBasicAuth
import json
from configparser import ConfigParser
from pathlib import Path
import datetime

scriptname = Path(sys.argv[0])
inifilename = scriptname.with_suffix('')
logfilename = scriptname.with_suffix('')
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
    print('Unable to find key ' + str(e) + ' ' 'in ini file')

b2bi_url = b2bi_server + ':' + b2bi_port + b2bi_api_url

def write_to_log(message):
    with open(str(logfilename) + '.log', 'a') as file:
        datum = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(datum + ' ' + message + '\n')


def sendmail(mailserver, fromaddr, toaddr, subject, msg):
    msg = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (fromaddr, toaddr, subject, msg)
    try:
        print(msg)
        server = smtplib.SMTP(mailserver)
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()
    except:
        write_to_log('Unable to send email using SMTP server: ' + mailserver)


try:
    response = requests.get(b2bi_url, auth=HTTPBasicAuth(b2bi_username, b2bi_passwd))
except:
    # problems with connecting to the b2bi server and REST API call. Send an email and stop the program with exit code 1
    write_to_log('Unable to execute REST API on ' + b2bi_url + '. B2Bi Server not running')
    sendmail(smtp_server, fromaddr, toaddr, 'B2Bi REST API call failed',
             'Unable to execute REST API on ' + b2bi_url + '. B2Bi Server not running')
    sys.exit(1)
else:
    # no problem with the connection lets check the http response code
    if response.status_code != 200:
        # http response code is not equal to 200. Send an email and stop the program with exit code 1
        print(response.status_code)
        subject= 'B2Bi REST API call failed on server ' + b2bi_url + ' due to HTTP response code: ' + str(response.status_code)
        message = 'Unable to execute REST API on ' + b2bi_url + '. Check if the user has the rights to execute the B2Bi REST APIs or the view system status priveleges.'
        sendmail(smtp_server, fromaddr, toaddr, subject,message)
        write_to_log(message)
        sys.exit(1)
    else:
        # load the response message into a json object
        resp_payload = json.loads(str(response.text))

    # create a dictionary (key, value hashmap) of the type and status fields
    for item in resp_payload:
        systemnode_status[item['type']] = item['status']

    # loop through the hashmap and do a check on the key value pairs
    for k, v in systemnode_status.items():
        if (k == 'CN') or (k == 'TE') or (k == 'B2B'):
            if v.lower() != 'running':
                email = True

        elif (k == "Integration Engine"):
            if v.lower() != 'started':
                email = True

    if email:
        message='B2Bi System nodes on ' + b2bi_url + ' not running'
        sendmail(smtp_server, fromaddr, toaddr, message,
                 str(systemnode_status))
        write_to_log(message)
        sys.exit(1)
    else:
        write_to_log('B2Bi nodes are running!')
        sys.exit(0)

####################################################
#
# Author: Robert van Gangelen, Axway BV
# Version: 0.1
# Creation date: 16-11-2017	
# 	
# Run like: python check_traffic.py
#      example: python check_traffic.py	
# 
#  When program execution fails it returns exit code 1
#  Program uses ini file for the basic configuration
#  Program uses log file for execution information
#  Log file is located in the same directory as the py file
####################################################

import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
from requests.auth import HTTPBasicAuth
import json
from configparser import ConfigParser
from pathlib import Path
import datetime
import time
import logging
import os
mail=False
report_trafficjam=False
mailbody = []

# set the logging
logging.basicConfig(filename='check_traffic.log',level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')

scriptname = Path(sys.argv[0])
inifilename = scriptname.with_suffix('')
config = ConfigParser()
config.read(str(inifilename) + '.ini')

# read values from a section
try:
    traffic_url = config['CheckTraffic']['url']
    traffic_roads = config['CheckTraffic']['roads']
    traffic = bool(config['CheckTraffic']['traffic'])
    roadWorks = bool(config['CheckTraffic']['roadworks'])
    smtp_server = config['Mail']['smtp_server']
    smtp_port = config['Mail']['smtp_port']
    smtp_user = config['Mail']['smtp_user']
    smtp_pwd = config['Mail']['smtp_pwd']
    fromaddr = config['Mail']['from_addres']
    toaddr = config['Mail']['to_addres']
except KeyError as e:
    logging.error('Unable to find key {} in ini file'.format (str(e)))
    sys.exit(1)

# if logging is set to DEBUG mode print out the following information for debug purposes
logging.debug('traffic_url = {}'.format(traffic_url))
logging.debug('traffic_roads = {}'.format(traffic_roads))
logging.debug('traffic = {}'.format(str(traffic)))
logging.debug('roadWorks = {}'.format(str(roadWorks)))
logging.debug('smtp_server = {}'.format(smtp_server))
logging.debug('smtp_port = {}'.format(smtp_port))
logging.debug('smtp_user = {}'.format(smtp_user))
logging.debug('fromaddr = {}'.format(fromaddr))
logging.debug('toaddr = {}'.format(toaddr))

# Function for converting seconds to minutes
def converttominute(delay):
    minutes = float(delay) / 60
    return str(int(minutes))

# Function for converting meters to km
def converttokm(distance):
    km = float(distance) / 1000
    return str(int(km))

# Function to send an email
# def send_email(subject, body):
 
#     # Prepare actual message
#     message = """From: %s\nTo: %s\nSubject: %s\n\n%s
#     """ % (smtp_user, ", ".join(toaddr), subject, body)
#     try:
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.ehlo()
#         server.starttls()
#         server.login(smtp_user, smtp_pwd)
#         server.sendmail(fromaddr, toaddr, message)
#         server.close()
#         logging.info ('Successfully sent the mail to {}'.format(toaddr))
#     except:
#         logging.error('failed to send mail ' + 'using SMTP server: ' + smtp_server)
#         print ('failed to send mail')

def send_email(subject, body):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddr

    # Record the MIME types of both parts - text/plain and text/html.
    part = MIMEText(body, 'html')

    msg.attach(part)
    try:
        server = smtplib.SMTP('smtp.gmail.com', '587')
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pwd)
        server.sendmail(fromaddr, toaddr, msg.as_string())
        server.close()
    except:
         logging.error('failed to send mail ' + 'using SMTP server: ' + smtp_server)

def sethtml():

    html = """\
    <html>
        <head>
            <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            th, td {
                padding: 5px;
                text-align: left;
                font-size:  8px;
            }
            th {
                bgcolor: lightgrey;
            }
            caption {
                padding: 5px;
                text-align: left;
                font-size:  10px;
                font-weight:bold;
            }
            </style>
        </head>
    <body>
    """

    return html

try:
    response = requests.get(traffic_url)
except requests.exceptions.RequestException as e:
    # problems with connecting to the b2bi server and REST API call. Send an email and stop the program with exit code 1
    logging.error('Unable to execute REST API on {}. Traffic server not available'.format(traffic_url))
    sendmail(smtp_server, fromaddr, toaddr, 'Traffic REST API call failed',
             'Unable to execute REST API on {}. Traffic server not running'.format(traffic_url))
    sys.exit(1)
else:
    # no problem with the connection lets check the http response code
    if response.status_code == 200:
        # load the response message into a json object
        json_payload = json.loads(str(response.text))
    else:
        # http response code is not equal to 200. Send an email and stop the program with exit code 1
        subject= 'Traffic call failed on server {} due to HTTP response code: {}'.format(traffic_url, str(response.status_code))
        body= 'Unable to fetch the traffic information from {}. Due to HTTP response code: {}'.format(traffic_url, str(response.status_code))
        sendmail(subject, body)
        logging.error(message)
        sys.exit(1)

listofroads = traffic_roads.split(",")

# check if the highways are not empty in the INI file
if len(listofroads) == 0:
    logging.error('No highways found in ini file')
    sys.exit(1)

# set the report datetime based on the dateTime in the payload
report_datetime = datetime.datetime.strptime(json_payload['dateTime'], '%Y%m%d, %H:%M').strftime('%d %b %Y, %H:%M')

trafficjams={}
roadworks={}
radars={}
jamcounter = 0
radarcounter = 0

for item, value in json_payload.items():
    if item == 'roadEntries':
        roadEntries = list(value) 
        for road in roadEntries:
            roadnr = road['road']
            eventlist=dict(road['events'])
            for k, v in eventlist.items():
                if k == 'trafficJams':
                    trafficjams[roadnr] = v
                if k == 'roadWorks':
                    roadworks[roadnr] = v

#print(radars)
#print(radars)

mailbody.append('<h3>' + report_datetime + '</h3>')
mailbody.append('<table style="width:100%">')
mailbody.append('<caption>File overzicht</caption>')
mailbody.append('<tr><th>File</th><th>Vertraging</th><th>Lengte</th><th>Omschrijving</th></tr>')

for k, v in trafficjams.items():
    mail==True
    if k in listofroads: 
        for t in list(v):
            jamcounter += 1
            trafficmessage = dict(t)
            mailbody.append('<tr>')
            mailbody.append('<td>' + trafficmessage['location'] + '</td>')
                                
            if 'delay' in trafficmessage.keys():
                mailbody.append ('<td>' + converttominute(trafficmessage['delay']) + ' minutes' + '</td>')
            else:
                mailbody.append ('<td/>')
            if 'distance' in trafficmessage.keys(): 
                mailbody.append ('<td>' + converttokm(trafficmessage['distance']) + ' km' + '</td>')
            else:
                mailbody.append ('<td/>')

            mailbody.append ('<td>' + trafficmessage['description'] + '</td>')

mailbody.append('<tr></table><p/>')
mailbody.append('<table style="width:100%">')
mailbody.append('<caption>Wegwerkzaamheden overzicht</caption>')
mailbody.append('<tr><th>Werk</th><th>Omschrijving</th></tr>')

for k, v in roadworks.items():
    if k in listofroads:
        
        for t in list(v):
            roadmessage = dict(t)
            mailbody.append('<tr>')
            mailbody.append ('<td>' + roadmessage['location'] + '</td>')
            mailbody.append ('<td>' + roadmessage['description'] + '</td>')
            mailbody.append('</tr>')
mailbody.append('</tr></table></body></html>')
# for k, v in radars.items():
#     #if k in listofroads:
#     for t in list(v):
#         radarcounter += 1
#         radar = dict(t)
#         mailbody.append ('[Radar] ' + radar['location'] + '\n')


if jamcounter != 0:
    send_email('{} {} Files meldingen gevonden!'.format(report_datetime, jamcounter), sethtml() + ''.join(mailbody))

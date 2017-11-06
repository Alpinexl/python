import sys
import requests
import smtplib
import os
import datetime
from configparser import ConfigParser
from pathlib import Path

scriptname = Path(sys.argv[0])
inifilename = scriptname.with_suffix('')
logfilename = scriptname.with_suffix('')
config = ConfigParser()
config.read(str(inifilename) + '.ini')

try:
    loadbalancer_server = config['Config']['loadbalancer_server']
    loadbalancer_port = config['Config']['loadbalancer_port']
    healthcheck_api = config['Config']['healthcheck_api']
    smtp_server = config['Mail']['smtp_server']
    fromaddr = config['Mail']['from_addres']
    toaddr = config['Mail']['to_addres']
except KeyError as e:
    print('Unable to find key ' + str(e) + ' ' 'in ini file')

url_loadbalancer =  loadbalancer_server + ':' + loadbalancer_port + healthcheck_api
sendnoemail=os.path.dirname(sys.argv[0]) + os.sep + 'send_no.email'
print(sendnoemail)
logfile=str(logfilename) + '.log'

def write_to_log (message):
    with open(logfile, "a") as file:
        datum = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(datum + ' ' + message + '\n')

def sendmail (mailserver, fromaddr, toaddr, subject, msg):
    msg = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (fromaddr, toaddr, subject, msg)
    try:
        True
        #server = smtplib.SMTP(mailserver)
        #server.sendmail(fromaddr, toaddr, msg)
        #server.quit()
    except:
        write_to_log('Unable to send email to mailserver ' + smtp_server)
        sys.exit(1)
try:
    response = requests.get(url_loadbalancer)
except requests.exceptions.RequestException as e:
    if not os.path.isfile(sendnoemail):
        sendmail(smtp_server, fromaddr, toaddr, "Unable to execute healthcheck on loadbalancer.", "Unable to execute healthcheck on loadbalancer.")
        open (sendnoemail,'a').close()
	
    write_to_log("Unable to execute healthcheck on loadbalancer")
    sys.exit(1)

if response.status_code == 200:
    if os.path.isfile(sendnoemail):
        os.remove(sendnoemail)
    write_to_log("Healthcheck OK")
else:
    if not os.path.isfile(sendnoemail):
        sendmail(smtp_server, fromaddr, toaddr, "Succesfully execute healthcheck on hostname. " + url_loadbalancer + ' but with response code: ' + response.status_code, "Unable to execute healthcheck on hostname.")
        open(sendnoemail, 'a').close()
        sys.exit(1)

import os
from configparser import ConfigParser
from pathlib import Path
import sys
import datetime
import time
import logging

# function to send an email
def sendmail(mailserver, fromaddr, toaddr, subject, msg):
    msg = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (fromaddr, toaddr, subject, msg)
    try:
        logging.debug ('Email message: {}'.format(msg))
        server = smtplib.SMTP(mailserver)
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()
    except:
        logging.error('Unable to send email using SMTP server: ' + mailserver)

# set the logger basic configuration
logging.basicConfig(filename='b2bi_watchdog.log',level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')

retrycounter = 0
scriptname = Path(sys.argv[0])
inifilename = str(scriptname.with_suffix('')) + '.ini'
logfilename = scriptname.with_suffix('')
config = ConfigParser()
filefound = False

# check if ini file exists
if os.path.isfile(str(inifilename)):
	config.read(str(inifilename))	
else:
    logging.error('Unable to find ini file:' + inifilename)
    sys.exit(1)

# read values from a section from the ini file
try:
    b2bi_inputdir = config['B2Bi']['b2bi_inputdir']
    b2bi_outputdir = config['B2Bi']['b2bi_outputdir']
    b2bi_filename = config['B2Bi']['b2bi_filename']
    sleeptime = config['B2Bi']['sleeptime']
    retry = config['B2Bi']['retry']  
    smtp_server = config['Mail']['smtp_server']
    fromaddr = config['Mail']['from_addres']
    toaddr = config['Mail']['to_addres']

except KeyError as e:
    print('Unable to find key {} in ini file'.format(str(e)))
    sys.exit(1)

# if loglevel is DEBUG print all variables field with ini file
logging.debug('b2bi_inputdir = {}'.format(b2bi_inputdir))
logging.debug('b2bi_outputdir = {}'.format(b2bi_outputdir))
logging.debug('b2bi_filename = {}'.format(b2bi_filename))
logging.debug('sleeptime = {}'.format(sleeptime))
logging.debug('retry = {}'.format(retry))
logging.debug('smtp_server = {}'.format(smtp_server))
logging.debug('fromaddr = {}'.format(fromaddr))
logging.debug('toaddr = {}'.format(toaddr))

# set the tmp directory
tmp_b2bi_inputdir = b2bi_inputdir + os.sep + 'tmp'

# create the tmp dir
try:
    os.makedirs(tmp_b2bi_inputdir)
except OSError as e:
    logging.error('Error creating tmp directory: {}. Error = {}'.format (tmp_b2bi_inputdir, str(e)))        

# create the watchdog file in the tmp directory
with open(tmp_b2bi_inputdir + os.sep + b2bi_filename, 'w') as file:
    file.write('Watchdog file')
    file.close

# move the watchdog file to the b2bi pickup directory
os.rename(tmp_b2bi_inputdir + os.sep + b2bi_filename, b2bi_inputdir + os.sep + b2bi_filename)

# clean up the tmp directory
os.removedirs(tmp_b2bi_inputdir) 

# lets try to find the file in X attempts
for x in range(int(retry)):
    retrycounter +=1
    logging.info('Check if file: {} is present in directory: {}. Attempt number = {}'.format(b2bi_filename,b2bi_outputdir,str(retrycounter)))
    time.sleep(int(sleeptime))
    
    # check if the file exists
    if os.path.isfile(b2bi_outputdir + os.sep + b2bi_filename):
        # file found set filefound on True and break the loop 
        filefound=True
        break
    else:
        # file not found so lets continue
        logging.info('The file not present... Lets try again!')
        continue

if filefound:
    logging.info('File found! And needed ' + str(retrycounter) + ' attempts to find the file : ' + b2bi_outputdir + os.sep + b2bi_filename)
    
    # clean up the watchdog file
    os.remove(b2bi_outputdir + os.sep + b2bi_filename)
    logging.info('File located on: ' + b2bi_outputdir + os.sep + b2bi_filename + ' removed')
else:
    logging.error('File not found... reties exhausted. Email will be send because b2bi is not running')
    sendmail(smtp_server, fromaddr, toaddr, 'Watchdog process failed', 'Watchdog process failed after all retrys')
    
    # if the watchdog file still exist in the input dir clean it up
    if os.path.isfile(b2bi_inputdir + os.sep + b2bi_filename):
        os.remove(b2bi_inputdir + os.sep + b2bi_filename)
        logging.info('File located on: ' + b2bi_inputdir + os.sep + b2bi_filename + ' removed')
import socket
from configparser import ConfigParser
from pathlib import Path
import sys
import logging

logging.basicConfig(filename='port_checker.log',level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')

scriptname = Path(sys.argv[0])
inifilename = scriptname.with_suffix('')
config = ConfigParser()
config.read(str(inifilename) + '.ini')

# read values from a section
try:
    server = config['Portchecker']['server']
    ports = config['Portchecker']['ports']
    timeout = config['Portchecker']['timeout']
except KeyError as e:
    logging.error('Unable to find key {} in ini file'.format (str(e)))

# if logging is set to DEBUG mode print out the following information for debug purposes
logging.debug('server = {}'.format(server))
logging.debug('ports = {}'.format(ports))
logging.debug('timeout = {}'.format(timeout))

port = ports.split(',')

for item in port:
	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(int(timeout))
		s.connect((server, int(item)))
	except socket.error:
		logging.error('Unable to connect to server {} on port {}.'.format(server, item))
	else:
		logging.info('Connected to server {} on port {}'.format(server, item))
		s.close

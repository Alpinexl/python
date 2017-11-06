from configparser import ConfigParser
from pathlib import Path
import sys

scriptname=Path(sys.argv[0])
inifilename=scriptname.with_suffix('')
config = ConfigParser()
config.read(str(inifilename) + '.ini')

# read values from a section
try:
    b2bi_server = config['B2Bi']['b2bi_server']
    b2bi_port = config['B2Bi']['b2bi_port']
    b2bi_username = config['B2Bi']['b2bi_username']
    b2bi_password = config['B2Bi']['b2bi_password']
    smtp_server = config['Mail']['smtp_server']
    from_addres = config['Mail']['from_addres']
    to_addres = config['Mail']['to_addres']
except KeyError as e:
    print('Unable to find key ' + str(e) + ' ' 'in ini file')



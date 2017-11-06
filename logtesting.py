import logging

logging.basicConfig(filename='logtesting.log',level=logging.INFO, 
	format='%(asctime)s %(levelname)s %(message)s')

logging.debug('debug regel')
logging.info('hallo dit is een logregel')
logging.warning('warning regel')
logging.error('error regel')
logging.critical('critical regel')
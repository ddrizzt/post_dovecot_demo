import mysql.connector
import sys
import os
import subprocess
import logging
import logging.config
import time
import salt
import salt.client
import json
import dcmaster

#############################################
###### Initial logging
#############################################
# create logger

logger_name = "simple"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)

# create file handler
log_path = "/mnt/post_dovecot_demo/logs/directmonitor.log"

fh = logging.FileHandler(log_path)
fh.setLevel(logging.INFO)

# create formatter
fmt = "%(asctime)s - %(levelname)s - %(message)s"
datefmt = "%a %d %b %Y %H:%M:%S"

# add handler and formatter to logger
formatter = logging.Formatter(fmt, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)
#############################################
argv = ''
if len(sys.argv) > 1:
    argv = sys.argv[1:]

logger.info('================ Start ===============')
logger.info('Input parameter %s' % argv)
dcm = dcmaster.DCMaster(logger)
if argv[0] == 'initial':
    dcm.initialClusterByHeartBeat()
elif argv[0] == 'monitoring':
    try:
        batch = 0
        while True:
            logger.info('Start monitoring batch %s' % batch)
            dcm.monitorWholeCluster()
            batch += 1
            time.sleep(5)
    except Exception, err:
        logger.error('%s' % err)

logger.info('================ END ===============')
sys.exit(0)

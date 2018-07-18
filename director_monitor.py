import mysql.connector
import sys
import os
import subprocess
import logging
import logging.config
import salt
import salt.client
import json

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

logger.info('================ Start ===============')

db = mysql.connector.connect(host="dovecotauth.cocsmvpnuzlc.us-west-2.rds.amazonaws.com", user="dovecot", password="dovecot123", database="servermail2")

sclient = salt.client.LocalClient()
resp = sclient.cmd('*', 'cmd.run', ['doveadm director status'])
print resp

logger.info('================ END ===============')

sys.exit(0)

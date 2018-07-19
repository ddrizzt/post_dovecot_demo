# This script just sync the newest director & backend IP list from DB, and refresh the director local config file /etc/dovecot/conf.d/10-director.conf
# Just update the local configure file, NO booting!

import mysql.connector
import sys
import os
import subprocess
import logging
import logging.config

#############################################
###### Initial logging
#############################################
# create logger
logger_name = "simple"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)

# create file handler
log_path = "/mnt/post_dovecot_demo/logs/directrefresh.log"

fh = logging.FileHandler(log_path)
fh.setLevel(logging.INFO)

# create formatter
fmt = "%(asctime)s - %(levelname)s - %(message)s"
datefmt = "%a %d %b %Y %H:%M:%S"
formatter = logging.Formatter(fmt, datefmt)

# add handler and formatter to logger
fh.setFormatter(formatter)
logger.addHandler(fh)
#############################################
logger.info('================ Start ===============')

ips_backend_fromf = ''
ips_director__fromf = ''
if os.path.isfile('/mnt/post_dovecot_demo/ipsbackend.dat'):
    ips_backend_fromf = open('/mnt/post_dovecot_demo/ipsbackend.dat', 'r').read()
if os.path.isfile('/mnt/post_dovecot_demo/ipsdirector.dat'):
    ips_director__fromf = open('/mnt/post_dovecot_demo/ipsdirector.dat', 'r').read()

if len(sys.argv) > 1:
    logger.info("Refresh configure file through input parameter %s" % sys.argv[1:])
    for argv in sys.argv[1:]:
        if argv.startswith('d:'):
            argv = argv.replace('d:', '')
            ips_director_str = argv.replace(',', ' ')
        elif argv.startswith('b:'):
            argv = argv.replace('b:', '')
            ips_backend_str = argv.replace(',', ' ')
else:
    logger.info("Refresh configure file through DB")
    db = mysql.connector.connect(host="dovecotauth.cocsmvpnuzlc.us-west-2.rds.amazonaws.com", user="dovecot", password="dovecot123", database="servermail2")
    cursor = db.cursor()
    cursor.execute("select group_concat(local_ip4 SEPARATOR ' ') from backend_director_monitoring where type = 'backend' AND status = 1 group by 'all' order by 1")
    ips_backend = cursor.fetchone()
    cursor.execute("select group_concat(local_ip4 SEPARATOR ' ') from backend_director_monitoring where type = 'director' AND status = 1 group by 'all' order by 1")
    ips_director = cursor.fetchone()
    db.close()

    if ips_director != None and ips_backend != None and len(ips_backend) > 0 and len(ips_director) > 0:
        ips_director_str = ips_director[0]
        ips_backend_str = ips_backend[0]
        logger.info('Dovecot directors [%s]' % ips_director_str)
        logger.info('Dovecot backends [%s]' % ips_backend_str)
    else:
        logger.error('ERROR Dovecot backend or director is not ready !!! backend(%s), director(%s)' % (ips_backend, ips_director))
        logger.info('================ END ===============')
        sys.exit(0)

# Check IPs updated or not.
if ips_backend_str == ips_backend_fromf and ips_director_str == ips_director__fromf:
    logger.info('Address unchanged.')
else:
    logger.info('Address updated, refresh director configure file.')
    # Update dovecot director conf filesashuru
    with open("./10-director.conf", "rt") as fin:
        with open("./10-director_new.conf", "wt") as fout:
            for line in fin:
                line = line.replace('[DIRECTOR_IPs]', ips_director_str)
                line = line.replace('[BACKEND_IPs]', ips_backend_str)
                fout.write(line)
    fout.close()

    with open('/mnt/post_dovecot_demo/ipsbackend.dat', 'w') as text_file:
        text_file.write(ips_backend_str)
    with open('/mnt/post_dovecot_demo/ipsdirector.dat', 'w') as text_file:
        text_file.write(ips_director_str)
    os.rename('/mnt/post_dovecot_demo/10-director_new.conf', '/etc/dovecot/conf.d/10-director.conf')

logger.info('================ END ===============')

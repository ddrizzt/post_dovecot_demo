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

db = mysql.connector.connect(host="dovecotauth.cocsmvpnuzlc.us-west-2.rds.amazonaws.com", user="dovecot", password="dovecot123", database="servermail2")

ips_backend_fromf = ''
ips_director__fromf = ''

if os.path.isfile('/mnt/post_dovecot_demo/ipsbackend.dat'):
    ips_backend_fromf = open('/mnt/post_dovecot_demo/ipsbackend.dat', 'r').read()

if os.path.isfile('/mnt/post_dovecot_demo/ipsdirector.dat'):
    ips_director__fromf = open('/mnt/post_dovecot_demo/ipsdirector.dat', 'r').read()

cursor = db.cursor()
cursor.execute("select group_concat(local_ip4 SEPARATOR ' ') from backend_director_ips where type = 'backend' AND TIME_TO_SEC(TIMEDIFF(now(),updated_at)) < 100 group by 'all' order by 1")
ips_backend = cursor.fetchone()

cursor.execute("select group_concat(local_ip4 SEPARATOR ' ') from backend_director_ips where type = 'director' AND TIME_TO_SEC(TIMEDIFF(now(),updated_at)) < 100 group by 'all' order by 1")
ips_director = cursor.fetchone()

db.close()

if len(ips_backend) > 0 and len(ips_director) > 0:
    ips_director_str = ips_director[0]
    ips_backend_str = ips_backend[0]

    logger.info('Dovecot directors [%s]' % ips_director_str)
    logger.info('Dovecot backends [%s]' % ips_backend_str)

    # Check IPs updated or not.
    if ips_backend_str == ips_backend_fromf and ips_director_str == ips_director__fromf:
        logger.info('Address unchanged.')
    else:
        logger.info('Address updated, refresh director configure file.')
        # Update dovecot director conf file
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

        # For demo show I used doveadm reload command here, for production here should use 'doveadm ring add ip port' instead.
        # This add command should only be called on one director at a time. Or it will cause un-expected issue.
        # Backend add or move have to reboot the service or use 'doveadm director add/remove' logic.
        # os.system('doveadm reload')
        # os.system('service dovecot restart')
        cmd_restart = '/bin/systemctl restart dovecot.service'
        logger.info("Restart dovecot service :: " + cmd_restart)
        p = subprocess.Popen(cmd_restart, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            logger.info("Exec return:" + line[:-1])
        retval = p.wait()

else:
    logger.error('ERROR Dovecot backend or director is not ready !!! backend(%s), director(%s)' % (ips_backend[0], ips_director[0]))

logger.info('================ END ===============')

sys.exit(0)

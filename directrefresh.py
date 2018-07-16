import mysql.connector
import sys
import datetime
import os

print '%s :: ====== Start =====' % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

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

    print '%s :: Dovecot directors [%s]' % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), ips_director_str)
    print '%s :: Dovecot backends [%s]' % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), ips_backend_str)

    # Check IPs updated or not.
    if ips_backend_str == ips_backend_fromf and ips_director_str == ips_director__fromf:
        print '%s :: Address unchanged.' % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    else:
        print '%s :: Address updated, refresh director configure file.' % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
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
        os.system('doveadm reload')

else:
    print '%s :: ERROR Dovecot backend or director is not ready !!! backend(%s), director(%s)' % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), ips_backend[0], ips_director[0])

print '%s :: ====== END =====' % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

sys.exit(0)

#NOTE:: This is a DOVECOT BACKEND CONFIG FILE!!!
#Mount EFS
mkdir /efs
cd / && mount -t efs fs-62f299cb:/ efs

# Replace dovecot configure file & restart dovecot
mv /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.bak
cp /mnt/post_dovecot_demo/dovecot_backend.conf /etc/dovecot/dovecot.conf
cp /mnt/post_dovecot_demo/dovecot-bg-sql.conf.ext /etc/dovecot/
service dovecot restart

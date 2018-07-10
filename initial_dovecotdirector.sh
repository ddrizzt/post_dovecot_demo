#NOTE:: This is a DOVECOT DIRECTOR CONFIG FILE!!!
#Mount EFS
mkdir /efs
cd / && mount -t efs fs-62f299cb:/ efs

# Replace dovecot configure file & restart dovecot
mv /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.bak
cp /mnt/post_dovecot_demo/dovecot_director.conf /etc/dovecot/dovecot.conf

mv /etc/dovecot/conf.d/10-director.conf mv /etc/dovecot/conf.d/10-director.conf.bak
cp /mnt/post_dovecot_demo/10-director.conf /etc/dovecot/conf.d/10-director.conf
service dovecot restart

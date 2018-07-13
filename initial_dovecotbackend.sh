#NOTE:: This is a DOVECOT BACKEND CONFIG FILE!!!
#Mount EFS
mkdir /efs
cd / && mount -t efs fs-62f299cb:/ efs

# Replace dovecot configure file & restart dovecot
mv /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.bak
cp /mnt/post_dovecot_demo/dovecot_backend.conf /etc/dovecot/dovecot.conf
cp /mnt/post_dovecot_demo/dovecot-bg-sql.conf.ext /etc/dovecot/

#Deploy crontab for heartbeat.sh
chmod +x /mnt/post_dovecot_demo/heartbeat.sh
echo "* * * * * /mnt/post_dovecot_demo/heartbeat.sh backend" > heartbeat.cron && crontab -u root heartbeat.cron && rm -f heartbeat.cron

service dovecot restart

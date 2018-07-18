#NOTE:: This is a DOVECOT DIRECTOR CONFIG FILE!!!

# Replace dovecot configure file & restart dovecot
mv /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.bak
cp /mnt/post_dovecot_demo/dovecot_director.conf /etc/dovecot/dovecot.conf
cp /mnt/post_dovecot_demo/dovecot-bg-sql.conf.ext /etc/dovecot/

mv /etc/dovecot/conf.d/10-director.conf mv /etc/dovecot/conf.d/10-director.conf.bak
cd /mnt/post_dovecot_demo/ && cat 10-director.conf | perl -ne ' chomp($_);  $str = $_; $str =~ s/\[DIRECTOR_IPs\]/127.0.0.1/g; $str =~ s/\[BACKEND_IPs\]/127.0.0.1/g; print "$str\n";' > /etc/dovecot/conf.d/10-director.conf

#Deploy crontab for heartbeat.sh
chmod +x /mnt/post_dovecot_demo/heartbeat.sh
mkdir -p /mnt/post_dovecot_demo/logs/
echo "* * * * * /mnt/post_dovecot_demo/heartbeat.sh director >> /mnt/post_dovecot_demo/logs/heartbeats.log 2>&1" > heartbeat.cron && crontab -u root heartbeat.cron && rm -f heartbeat.cron

#service dovecot restart

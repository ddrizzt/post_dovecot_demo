# Create users
useradd -u 2100 guest -p abc123
useradd -u 2101 kevin -p abc123
useradd -u 2102 eric -p abc123
useradd -u 2103 tom -p abc123
useradd -u 2104 jason -p abc123
useradd -u 2105 peter -p abc123

#Mount EFS
#mkdir /efs
#cd / && mount -t efs fs-62f299cb:/ efs && rm -rf /efs/*
mkdir -p /efs/Mail && chmod 777 /efs/Mail
mkdir -p /efs/dovecotindex && chmod 777 /efs/dovecotindex

# Replace postfix config file and restart
cd /mnt/post_dovecot_demo/ && cat postfix_main.cf | perl -ne ' chomp($_);  $str = $_; $str =~ s/\[DOMAIN\]/$ENV{'DOMAIN'}/g; print "$str\n";' > main.cf
mv /etc/postfix/main.cf /etc/postfix/main.cf.bak && mv /mnt/post_dovecot_demo/main.cf /etc/postfix/main.cf
service postfix restart

#Init RDS data
echo 'DROP DATABASE IF exists servermail2; CREATE DATABASE servermail2;' | mysql -hdovecotauth.cocsmvpnuzlc.us-west-2.rds.amazonaws.com -udovecot -pdovecot123 -P3306
cd /mnt/post_dovecot_demo/ && cat rds_mysql_init.sql | perl -ne ' chomp($_);  $str = $_; $str =~ s/\[DOMAIN\]/$ENV{'DOMAIN'}/g; print "$str\n";' > init.sql
mysql -hdovecotauth.cocsmvpnuzlc.us-west-2.rds.amazonaws.com -udovecot -pdovecot123 -P3306 servermail2 < init.sql

#Send some test mail
cd /mnt/post_dovecot_demo/ && cat sendtestmail.sh | perl -ne ' chomp($_);  $str = $_; $str =~ s/\[DOMAIN\]/$ENV{'DOMAIN'}/g; print "$str\n";' > /mnt/post_dovecot_demo/sendtestmail_new.sh
chmod +x /mnt/post_dovecot_demo/sendtestmail_new.sh && sh /mnt/post_dovecot_demo/sendtestmail_new.sh

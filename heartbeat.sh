# Here should call some status check script to make sure current dovecot_backend or director works fine....

####### TBD: status check script here

# Once the status is fine, refresh the IP info into RDS DB.
cd /mnt/post_dovecot_demo/ && \
 STATUS=1 && \
 DOVECOT_TYPE=$1 && \
 IPV4=`curl -s http://169.254.169.254/latest/meta-data/local-ipv4` && \
 DNSPUBLIC=`curl -s http://169.254.169.254/latest/meta-data/public-hostname` && \
 DNSPRIVATE=`curl -s http://169.254.169.254/latest/meta-data/local-hostname` && \
 echo "INSERT INTO backend_director_ips (type, local_ip4, public_dns, private_dns, status, updated_at) VALUES('$DOVECOT_TYPE', '$IPV4', '$DNSPUBLIC', '$DNSPRIVATE', $STATUS, now()) ON DUPLICATE KEY UPDATE updated_at=now(), status='$STATUS';" |\
 mysql -hdovecotauth.cocsmvpnuzlc.us-west-2.rds.amazonaws.com -udovecot -pdovecot123 -P3306 servermail2


if [ $1 = "director" ] ; then
    cd /mnt/post_dovecot_demo/ && python directrefresh.py
fi

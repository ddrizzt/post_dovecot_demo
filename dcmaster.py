import mysql.connector
import sys
import os
import subprocess
import logging
import logging.config
import salt
import salt.client
import json
import re
import time


class DCMaster:
    "Dovecot monitor class, use saltstack to monitor & manager dovecot direct & backend nodes."

    def __init__(self, logger):
        self.directors = dict()
        self.backends = dict()
        self.log = logger
        self.sclient = salt.client.LocalClient()

    def saltExec(self, node='', cmd=''):
        if len(node) < 1 or len(cmd) < 1:
            return
        self.log.info('Exec cmd on %s: %s' % (node, cmd))
        resp = self.sclient.cmd(node, 'cmd.run', [cmd])
        self.log.info('Resp cmd on %s: %s\n%s' % (node, cmd, json.dumps(resp, indent=4)))
        return resp

    def getHeartbeatInfo(self):
        hb = {}
        # Read from DB first
        db = mysql.connector.connect(host="dovecotauth.cocsmvpnuzlc.us-west-2.rds.amazonaws.com", user="dovecot", password="dovecot123", database="servermail2")
        cursor = db.cursor()
        cursor.execute("select type, local_ip4, private_dns, public_dns, updated_at from backend_director_ips")
        data = cursor.fetchall()
        for row in data:
            type = row[0]
            ip4 = row[1]
            privatedns = row[2]
            publicdns = row[3]
            updated_at = ''
            hb[privatedns] = {'type': type, 'ip': ip4, 'private_dns': privatedns, 'public_dns': publicdns, 'status': '0', 'updated_at': updated_at}
        db.close()
        return hb

    def flushDBData(self):
        rows = []
        for key in self.backends:
            if self.backends[key]['status'] != '1':
                continue
            rows.append("('backend', '%s', '%s', '%s', '%s', now())" % (self.backends[key]['ip'], self.backends[key]['public_dns'], self.backends[key]['private_dns'], self.backends[key]['status']))

        for key in self.directors:
            if self.directors[key]['status'] != '1':
                continue
            rows.append("('director', '%s', '%s', '%s', '%s', now())" % (self.directors[key]['ip'], self.directors[key]['public_dns'], self.directors[key]['private_dns'], self.directors[key]['status']))

        data_body = str.join(',', rows)
        db = mysql.connector.connect(host="dovecotauth.cocsmvpnuzlc.us-west-2.rds.amazonaws.com", user="dovecot", password="dovecot123", database="servermail2")
        cursor = db.cursor()
        cursor.execute("REPLACE INTO backend_director_monitoring(type, local_ip4, public_dns, private_dns, status, updated_at) VALUES %s" % (data_body))
        self.log.info('Updated rows %s:' % cursor.rowcount)
        db.commit()
        db.close()

    def rebootService(self, node=''):
        # TBD: Force reboot all director services. If node=All, then reboot all!
        if node == 'All':
            node = '*'
        elif node == 'bakcend':
            # TBD should not hardcoded
            node = '*-11-0-1-*'
        elif node == 'director':
            # TBD should not hardcoded
            node = '*-11-0-0-*'
        self.log.info('Rebooting dovecot service...')
        self.saltExec(node, 'service dovecot restart 2>/dev/null')

    def listAll(self):
        self.log.info('==== Backends\n%s' % json.dumps(self.backends, indent=4))
        self.log.info('==== Directors\n%s' % json.dumps(self.directors, indent=4))

    def updateDirectorConfig(self):
        # Combine backend & director to a parameter string like: d:11.0.0.1,11.0.0.1 b:11.0.1.1,11.0.1.2
        backends = []
        for key in self.backends:
            if self.backends[key]['status'] != '1':
                continue
            backends.append(self.backends[key]['ip'])

        directors = []
        for key in self.directors:
            if self.directors[key]['status'] != '1':
                continue
            directors.append(self.directors[key]['ip'])

        if len(directors) < 1 or len(backends) < 1:
            self.log.error('No enough backend or directors d:%s, b:%s' % (str.join(',', directors), str.join(',', backends)))
            return

        cmd = 'cd /mnt/post_dovecot_demo/ && python directrefresh.py d:%s b:%s' % (str.join(',', directors), str.join(',', backends))
        self.saltExec('*-11-0-0-*', cmd)

        # Force reboot whole cluster...
        self.rebootService('All')

    def initialClusterByHeartBeat(self):
        self.log.info('Get heartbeat info from DB:backend_director_ips')

        data = self.getHeartbeatInfo()
        for key in data:
            type = data[key]['type']
            ip4 = data[key]['ip']
            privatedns = data[key]['private_dns']
            publicdns = data[key]['public_dns']
            status = data[key]['status']
            updated_at = data[key]['updated_at']

            if type == 'director':
                self.directors[privatedns] = {'ip': ip4, 'private_dns': privatedns, 'public_dns': publicdns, 'status': '0', 'updated_at': updated_at}
            elif type == 'backend':
                self.backends[privatedns] = {'ip': ip4, 'private_dns': privatedns, 'public_dns': publicdns, 'status': '0', 'updated_at': updated_at}

        self.log.info('Read Salt cluster information and compare DB data')

        resp = self.sclient.cmd('*', 'test.ping')
        for key in resp:
            if self.backends.has_key(key) and resp[key] == True:
                self.backends[key]['status'] = '1'
            elif self.directors.has_key(key) and resp[key] == True:
                self.directors[key]['status'] = '1'

        self.listAll()

        self.log.info('Insert final data into DB.')
        # Insert final data into DB.
        self.flushDBData()

        self.log.info('Refresh director config file and reboot whole cluster')

        self.updateDirectorConfig()

    def checkNodeStatus(self, node, skipfailed=True):
        status = dict()
        resp = self.saltExec(node, 'service dovecot status 2>/dev/null')
        for key in resp:
            passed = re.match(r'dovecot\s+\(pid\s+\d+\)\s+is\s+running...', resp[key]) is not None
            if skipfailed and passed == False:
                continue
            status[key] = passed

        return status

    def checkBackendSynced(self):
        # Get backend list from directors
        resp = self.saltExec('*11-0-0-*', 'doveadm director status')

        return True

    def monitorWholeCluster(self):
        self.log.info('Start whole dovecluster monitoring...')
        # Get heartbeat data from DB.
        hbData = self.getHeartbeatInfo()

        # Run ping test against directors and backends and compare with DB heartbeat data.
        nodeStatus = self.checkNodeStatus('*', False)
        # TODO Here!!!!
        for key in nodeStatus:
            if nodeStatus[key] == False:
                # Handle failed node!
                self.log.warn('Node failed %s!' % key)

            else:
                # Handle running node!
                if (self.backends.has_key(key) or self.directors.has_key(key)) and hbData.has_key(key):
                    self.log.info('Node running well. %s' % key)
                elif not hbData.has_key(key):
                    # This is a new node but hadn't send out heartbeat info into DB yet. Just wait.
                    self.log.info('New node find, wait for heartbeat message. %s' % key)
                elif hbData.has_key(key) and hbData[key]['status'] == '1' and not self.backends.has_key(key) and not self.directors.has_key(key):
                    # This is a new node and found heartbeat info from DB
                    self.log.info('New node find, need add to cluster. %s' % key)
                    if hbData[key]['type'] == 'backend':
                        self.log.info('Adding new backend..' % key)
                        retry = 0
                        resp = False
                        while retry < 3:
                            self.saltExec(self.backends[self.backends.keys()[0]], 'doveadm director add %s' % hbData[key]['ip'])
                            resp = self.checkBackendSynced()
                            if not resp:
                                time.sleep(5)
                                retry += 1
                                self.log.info('Wait backend data synced...')
                        if retry < 3 and not resp:
                            self.log.error('Backend sync failed... Need reboot!')
                        # TODO here, more words need be done. Very complex!!!!!

                    elif hbData[key]['type'] == 'director':
                        self.log.info('Adding new director..' % key)

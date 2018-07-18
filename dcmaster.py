import json


class DCmaster:
    "Dovecot monitor class, use saltstack to monitor & manager dovecot direct & backend nodes."

    def __init__(self):
        self.directors = dict()
        self.backends = dict()

    def fetchFromDB(self):
        print ''

    def addBackend(self, n='', data=dict()):
        self.backends[n] = data
        # TBD: Call doveadm director add

    def addDirector(self, n='', data=dict()):
        self.directors[n] = data
        # TBD: Call doveadm director ring add

    def listAll(self):
        print json.dumps(self.backends, indent=4)
        print json.dumps(self.directors, indent=4)

    def rmBacend(self, n=''):
        self.backends.pop(n)
        # TBD: Call doveadm director ring remove

    def rmDirect(self, n=''):
        self.directors.pop(n)
        # TBD: Call doveadm director remove

    def checkAllSynced(self):
        # TBD: Call doveadm director ring status on each directors to make sure director synced.
        # TBD: Call doveadm director status on each directors to make sure backens synced.
        print 'TBD'

    def rebootDirectors(self, node=''):
        # TBD: Force reboot all director services. If node=All, then reboot all!
        self.checkAllSynced()



dcm = DCmaster()
dcm.addBackend('Node1', {'name': 'node1', 'ip': '11.0.0.1', 'public_dns': 'aaa.com', 'status': '1'})
dcm.addBackend('Node2', {'name': 'node2', 'ip': '11.0.0.2', 'public_dns2': 'abc.com', 'status': '1'})
dcm.listAll()
print len(dcm.directors)
print len(dcm.backends)

import sys
import fandango as fn
import fandango.db as fdb
import PyTangoArchiving as pta

servers = dict()

hosts = sys.argv[1:] or ['archiving04','archiving05','archiving06','archiving07']

tables = ['att_scalar_devlong_ro']

def get_host_dbs(h, user='manager', passw='manager'):
    r = fn.defaultdict(fn.Struct)
    d = 'information_schema'
    db = fdb.FriendlyDB('information_schema',h,'manager','manager')
    dbs = [l for l in fn.join(db.Query('show databases')) if l.startswith('hdb') and not l=='hdb']
    for d in dbs:
        r[d].db=pta.HDBpp(d,h,'manager','manager')
    return r

for h in hosts:
    servers[h] = get_host_dbs(h)

for h,dbs in servers.items():
    for d,obj in dbs.items():
        db = obj.db
        obj.size = db.getDbSize()
        obj.tables = dict((t,db.getTableSize(t)) for t in (tables or db.get_data_tables()))
        obj.partitions = fn.defaultdict(dict)
        for t in obj.tables:
            parts = db.getTablePartitions(t)
            for p in parts:
                obj.partitions[t][p] = db.getPartitionSize(t,p)
                
for h,dbs in servers.items():
    for d,obj in dbs.items():
        db = obj.db
        obj.bigtables = [t[1] for t in reversed(sorted((v,k) for k,v in obj.tables.items()))]
        obj.lastparts = [t[1] for t in 
                         reversed(sorted((db.get_partition_time_by_name(p),p) for t,ps in obj.partitions.items() for p in ps))]
        obj.maxpart = ('',0)
        for t,ps in obj.partitions.items():
            for p in ps:
                if obj.partitions[t][p] > obj.maxpart[1]:
                    obj.maxpart = p,obj.partitions[t][p]
        
#Briefing
headers = 'host', 'db_name', 'size', 'bigtables', 'tabsizes', 'maxpartsize', 'lastparts', 'tstart', 'tstop'

for h,dbs in servers.items():
    for d,obj in dbs.items():
        
        


        

        


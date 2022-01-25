import threading
import time

from whatap.conf.configure import Configure as conf
from whatap.trace.trace_context_manager import TraceContextManager
from whatap.util.date_util import DateUtil
from whatap.util.hexa32 import Hexa32

from whatap.util.linked_map import LinkedMap
from resource import getrusage, RUSAGE_SELF


class TraceContext(object):
    transfer_id = None
    transfer_info = None

    def __init__(self):
        self.host = ''
        self.elapsed = 0

        self.isStaticContents = 'false'

        self.id = TraceContextManager.getId()
        self.thread = threading.current_thread()
        self.thread_id = TraceContextManager.start(self)

        self.start_time = 0
        self.start_cpu = 0
        self.start_malloc = 0

        self.status = 0

        self.service_hash = 0
        self.service_name = ''
        self.remoteIp = ''
        self.error = 0
        self.error_step = ''
        self.http_method = ''
        self.http_query = ''
        self.http_content_type = ''

        self.sql_count = 0
        self.sql_time = 0
        self.sql_insert = 0
        self.sql_update = 0
        self.sql_delete = 0
        self.sql_select = 0
        self.sql_others = 0

        self.executed_sqlhash = 0
        self.active_sqlhash = 0
        self.active_dbc = 0
        self.active_crud = 0

        self.httpc_checked = False
        self.httpc_count = 0
        self.httpc_time = 0
        self.httpc_url = ''

        self.active_httpc_hash = 0
        self.httpc_host = ''
        self.httpc_port = 0

        self.mtid = 0
        self.mdepth = 0
        self.mcallee = 0

        self.mcaller_txid = 0
        self.mcaller_pcode = 0
        self.mcaller_spec = ''
        self.mcaller_url = ''
        self.mcaller_poid = ''
        self.transfer_poid = None

        self.userid = ''
        self._rawuserid = ''
        self.userAgent = 0
        self.userAgentString = ''
        self.referer = ''
        self.login = ''
        self.userTransaction = 0
        self.debug_sql_call = False
        self.lastSqlStep = None
        self.profileActive = 0

        self.jdbc_updated = False
        self.jdbc_update_record = 0
        self.jdbc_identity = 0
        self.jdbc_commit = 0
        self.resultSql = LinkedMap()

        self.rs_count = 0
        self.rs_time = 0
        self.db_opening = False
        self.socket_connecting = False

        self.mcaller_url_hash= 0

        self.lctx = {}
        self.is_ignored = False

    def getElapsedTime(self, time=None):
        if not time:
            time = DateUtil.now()
        return time - self.start_time

    def getCpuTime(self):
        return int(time.time())

    def getMemory(self):
        # https://docs.python.org/3/library/resource.html?highlight=resource#resource-usage
        return int(getrusage(RUSAGE_SELF)[3] + getrusage(RUSAGE_SELF)[4])

    def resetStartTime(self):
        self.start_time = 0

    def transfer(self):
        if self.transfer_id:
            return self.transfer_id

        sb = []
        sb.append(Hexa32.toString32(self.mtid))
        sb.append(str(self.mdepth + 1))
        sb.append(Hexa32.toString32(self.id))
        transfer_id = ','.join(sb)
        return transfer_id

    def transferInfo(self):
        if self.transfer_info:
            return self.transfer_info

        sb = []
        sb.append(str(conf.mtrace_spec))
        sb.append(str(self.service_hash))
        
        transfer_info = ','.join(sb)
        return transfer_info

    def setTransfer(self, headerString):
        x = headerString.find(',')
        if x > 0:
            self.mtid = Hexa32.toLong32(headerString[0:x])
            y = headerString.find(',', x + 1)
            if y > 0:
                self.mdepth = int(headerString[x + 1:y])
                z = headerString.find(',', y + 1)

                if z < 0:
                    self.mcaller_txid = Hexa32.toLong32(headerString[y + 1:])
                else:
                    self.mcaller_txid = Hexa32.toLong32(headerString[y + 1: z])

    def setTransferInfo(self, headerString):
        x = headerString.index(',')
        s1 = headerString[0: x]
        self.mcaller_spec = s1
        self.mcaller_url_hash = headerString[x + 1: ]

    def setTxid(self, myid):
        self.id = Hexa32.toLong32(myid)

    def transferPOID(self):
        if not self.transfer_poid:
            self.transfer_poid = ",".join((Hexa32.toString32(conf.PCODE), Hexa32.toString32(conf.OKIND), Hexa32.toString32(int(conf.OID))))    

        return self.transfer_poid

from pyArango.connection import *
from pyArango.collection import *
from pyArango.graph import *
from .support import *
import datetime
import os
import json
import re

class BasicElement():
    if os.environ.get('D20_ORM_CONF') != None:
        conf = json.loads(os.environ.get('D20_ORM_CONF'))
        arangoURL=conf.get('D20_ORM_DBURL')
        username=conf.get('D20_ORM_DBUSERNAME')
        password=conf.get('D20_ORM_DBPASSWORD')        
    else:
        print("No configuration given, cannot start.")
        raise Exception

    db_client = Connection(arangoURL=arangoURL, username=username, password=password, verify=True, verbose=True, statsdClient=None, reportFileName=None, loadBalancing='round-robin', use_grequests=False, use_jwt_authentication=False, use_lock_for_reseting_jwt=True, max_retries=10)
    db_name = ''
    cascade = False
    @classmethod
    def search_attributes(cls):
        return []

    @classmethod
    def get_collection(cls):
        return None

    @classmethod
    def getAll(cls):
        return None
        
    @classmethod
    def build_query_parameters(cls, start_date=None, end_date=None) -> dict:
        qp = {}
        if start_date != None:
            qp.update({'start': start_date})
        if end_date != None:
            qp.update({'end': end_date})
        return qp


    @classmethod
    def build_filter_string(cls, filters:dict, start_date=None, end_date=None, date_dim='date_activity') -> str:
        attribute_list = [{'val':filters[att] , 'dim': att, 'op':'=='} for att in filters if filters[att] != None ]
        filters_list = []
        for att in attribute_list:
            if isinstance(att['val'], str):
                if att["op"] == '=~':
                    filters_list.append(f'Regex_Test(m.`{att["dim"]}`,"{att["val"]}", true)')
                else:
                    filters_list.append(f'm.`{att["dim"]}` {att["op"]} "{att["val"]}"')
            else:
                filters_list.append(f'm.`{att["dim"]}` {att["op"]} {att["val"]}')
        if start_date != None:
            filters_list.append(f'(m.{date_dim} >= @start)')
        if end_date != None:
            filters_list.append(f'(m.{date_dim} <= @end)')
        filters_string = ' && '.join(filters_list)
        return filters_string
    

    def auth(self):
        return False
    
    def isEdge(self):
        return False

    def vertex(self):
        return {'_from': '', '_to': ''}

    def cascade_delete(self):
        return False

    def cascade_update(self):
        return False

    def cascade_create(self):
        return False

    def createMany(self):
        # try:
        self.date_created= datetime.datetime.utcnow()
        self.date_updated = self.date_created
        self.deleted = self.get('deleted', False)
        if self.deleted == None:
            self.deleted = False
        for val in self.values:
            val['date_created'] = self.date_created
            val['date_updated'] = self.date_updated
            val['deleted'] = self.deleted
            for key in self.attributes:
                if key in val and val[key] == None:
                    val.pop(key)
            val = self.build_edges(val)
        aql = f'for nd IN {json.dumps(self.values)} \
            INSERT nd into {self.get_collection()} \
            LET inserted = NEW \
            RETURN inserted._key'
        res = self.db.AQLQuery(aql, rawResults=True, batchSize=100000)
        for i,val in enumerate(self.values):
            val['_key'] = res[i]
        # except:
        #     res = None
        #     self.status = False
        self.status = res != None
        
    

    # TODO: def build_filter_string(filters:dict) -> str
    def wipeByFilter(self, start_date=None, end_date=None, date_dim='date_activity'):
        # try:
        qf = self.build_filter_string(self.to_dict(), start_date=start_date, end_date=end_date, date_dim=date_dim)
        query = 'for m in '+ self.get_collection() +'\
                FILTER '+qf+'\
                REMOVE m in '+ self.get_collection()
        res = self.db.AQLQuery(query, rawResults=True, batchSize=100)
        # except:
        #     self._key = None
        #     self.status = False
        #     self.found = []

    def create(self):
        try:
            self.date_created= datetime.datetime.utcnow()
            self.date_updated = self.date_created
            self.deleted = self.get('deleted', False)
            if self.deleted == None:
                self.deleted = False
            to_insert = self.to_dict()
            for key in self.attributes:
                if key in to_insert and to_insert[key] == None:
                    to_insert.pop(key)
            to_insert = self.build_edges(to_insert)
            ins_obj = self.db[self.get_collection()].createDocument(to_insert)
            ins_obj.save()
            self._key = ins_obj._key
            if self.cascade == True:
                try:
                    self.cascade_create()
                except:
                    pass
        except:
            ins_obj = None
            self.status = False
        self.status = ins_obj != None

    def get_alias(self):
        return self.get('_key')

    def wipe(self):
        try:
            del_obj = self.db[self.get_collection()].fetchDocument(self._key)
            del_obj.delete()
            self.status = del_obj._key == None
        except:
            self.status = False
        self._key = None

    def delete(self):
        try:
            self.deleted = True
            self.active = False
            self.status = self.update()
            if self.cascade == True:
                try:
                    self.cascade_delete()
                except:
                    pass
        except:
            self.status = False
        self._key = None

    def find(self):
        try:
            found = self.db[self.get_collection()].fetchDocument(self._key)
            if found['deleted'] == True:
                found = None
            for key in self.attributes:
                setattr(self, key, found.getStore()[key] if key in found.getStore() else self.get(key))
            if '_to' in self.attributes:
                self._to = self.get('_to').split("/")[1]
            if '_from' in self.attributes:
                self._from = self.get('_from').split("/")[1]
            self.status = True
        except:
            self._key = None
            self.status = False
    
    def find_multikey(self, keys:list):
        try:
            self.find()
        except:
            pass
        if self._key != None:
            return        
        for key in keys:
            val = self.get(key)
            self._key = val
            try:
                self.find()
            except:
                pass
            if self._key != None:
                return
            for skey in keys:
                try:
                    self.findGraph({skey:val}, avoid_regex=True)
                    res = self.found[0]
                    self._key = res['_key']
                    self.find()
                except:
                    pass
                if self._key != None:
                    return

    def findGraph(self, query, avoid_regex=False):
        search_query = []
        for k in query:
            if isinstance(query[k], str) and not avoid_regex:
                # if type(query[k]) is not unicode:
                #     query[k] = unicode(query[k], encoding='utf-8')

                # query[k] = re.sub("+", '\+', query[k])
                query[k] = re.sub("[àáâãäå]", 'a', query[k])
                query[k] = re.sub("[èéêë]", 'e', query[k])
                query[k] = re.sub("[ìíîï]", 'i', query[k])
                query[k] = re.sub("[òóôõö]", 'o', query[k])
                query[k] = re.sub("[ùúûü]", 'u', query[k])
                query[k] = re.sub("[ýÿ]", 'y', query[k])
                query[k] = query[k] + '$'
                search_query.append({'dim': k, 'op': '=~', 'val': query[k]})
            else:
                search_query.append({'dim': k, 'op': '==', 'val': query[k]})
        self.search(search_query)

    def search(self, query, limit=None, start_date=None, end_date=None, date_dim='date_activity'):
        try:
            qf = self.build_filter_string(query, start_date=start_date, end_date=end_date, date_dim=date_dim)
            if limit != None:
                qf = qf + ' limit ' + str(limit)
            query = 'for m in '+ self.get_collection() +'\
                    FILTER '+qf+'\
                    return DISTINCT m'
            self.found = self.db.AQLQuery(query, rawResults=True, batchSize=100)
            self.found = list(filter(lambda x: not 'deleted' in x or x['deleted'] != True, self.found))
            if '_to' in self.attributes:
                for x in self.found:
                    x['_to'] = x['_to'].split("/")[1]
                    x['_from'] = x['_from'].split("/")[1]
            if 'password' in self.attributes:
                for x in self.found:
                    x['password'] = ''
            self.status = True
            if self.found == None:
                self.found = []
        except:
            self._key = None
            self.status = False
            self.found = []

    def get(self, att, default=None):
        res = getattr(self, att, default)
        if res == None:
            return default
        return res

    def get_class(self):
        return 'BasicElement'

    def get_distinct_elements(self, dims=['_key']):
        d = ', '.join([f'{dim} = doc.{dim}' for dim in dims])
        ds = '{' + ', '.join([f'{dim}' for dim in dims]) + '}'
        filter = ' and '.join([ f'm.{att} == "{self.get(att)}"' if isinstance(self.get(att), str) else f'm.{att} == {self.get(att)}' for att in self.get('attributes') if self.get(att) != None])
        query = f'FOR doc in {self.get_collection()} FILTER {filter} COLLECT {d} RETURN DISTINCT {ds}'
        self.delements = []
        [self.delements.append(e) for e in self.db.AQLQuery(query, rawResults=True, batchSize=1000)]

    def make(self):
        self.attributes = ['_key']
        for key in self.attributes:
            setattr(self, key, None)

    def do_publish(self, t):
        try:
            to_update = {'publish':t}
            update_obj = self.get_collection().fetchDocument(self._key)
            before = update_obj['_rev']
            update_obj.set(to_update)
            update_obj.patch()
            after = update_obj['_rev']
        except:
            return False
        return before != after

    def to_dict(self):
        res = {}
        for key in self.attributes:
            res[key] = self.get(key)
        return res

    def build_edges(self, base_obj):
        if self.isEdge() == True:
            from_to = self.vertex()
            if self.get('_to') != None and base_obj['_to'].find(f'{from_to["_to"]}/') != 0:
                base_obj['_to'] = f'{from_to["_to"]}/{self.get("_to")}'
            if self.get('_from') != None and base_obj['_from'].find(f'{from_to["_from"]}/') != 0:
                base_obj['_from'] = f'{from_to["_from"]}/{self.get("_from")}'
        return base_obj


    def update(self):
        try:
            self.date_updated = datetime.datetime.utcnow()
            to_update = self.to_dict()
            try:
                to_update.pop('date_created')
            except:
                pass
            try:
                to_update.pop('user_created')
            except:
                pass
            for key in self.attributes:
                if key in to_update and (to_update[key] == None or re.search(r'^(obj_){1}\w+$', key) != None or re.search(r'^(alias_){1}\w+$', key) != None):
                    to_update.pop(key)
            to_update = self.build_edges(to_update)
            update_obj = self.db[self.get_collection()].fetchDocument(self._key)
            before = update_obj['_rev']
            update_obj.set(to_update)
            update_obj.patch()
            after = update_obj['_rev']
            if self.cascade == True and before != after:
                try:
                    self.cascade_update()
                except:
                    pass
        except:
            return False
        return before != after

    def __init__(self, mode = None, data = None, multi = False):
        # try:
        self.db = self.db_client[self.db_name]
        self.make()
        if mode != None:
            if multi == True:
                self.values = []
                for i,val in enumerate(data):
                    temp_val = {}
                    for key in self.attributes:
                        temp_val[key] =val[key] if key in val else None
                    self.values.append(temp_val)         
                if mode == 'create': # OK
                    self.status = self.createMany()      
                # if mode == 'delete': # OK
                #     self.status = self.deleteMany()        
            else:    
                for key in self.attributes:
                    setattr(self, key, data[key] if key in data else None)
                if mode == 'create': # OK
                    self.status = self.create()
                elif mode == 'update': # OK
                    self.status = self.update()
                elif mode == 'set': # OK
                    self.status = True
                elif mode == 'find':  # OK
                    self.find()
                elif mode == 'fetch':  # OK
                    self.findGraph(data)
                elif mode == 'fetch_exact':  # OK
                    self.findGraph(data, avoid_regex=True)
                elif mode == 'delete': # OK
                    self.delete()
                elif mode == 'wipe': # OK
                    self.wipe()
                elif mode == 'wipe_filter': # OK
                    self.wipeByFilter()
                elif mode == 'publish': # OK
                    self.status = self.do_publish(data['publish'])
                elif mode == 'auth': # OK
                    self.auth()
                elif mode == 'search': # OK
                    self.search(data)
                elif mode == 'limited_search': # OK
                    self.search(data.pop('query', None), data.pop('limit', None))
        
        # except:
        #     print("Unexpected error.")
        #     self._key = None
        #     self.status = False
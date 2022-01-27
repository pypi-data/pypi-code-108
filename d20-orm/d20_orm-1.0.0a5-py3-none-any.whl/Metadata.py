# File: ArangoDB Datafield based Metadata
# Author: alexsanchezvega
# Company: d20
# Version: 1.0

from pyArango.connection import *
from pyArango.collection import *
from pyArango.graph import *
from .BasicElement import BasicElement
import json
import os

class Metadata():
    if os.environ.get('D20_ORM_CONF') != None:
        conf = json.loads(os.environ.get('D20_ORM_CONF'))
        arangoURL=conf.get('D20_ORM_DBURL')
        username=conf.get('D20_ORM_DBUSERNAME')
        password=conf.get('D20_ORM_DBPASSWORD')        
    else:
        print("No configuration given, cannot start.")
        raise Exception

    db_client = Connection(arangoURL=arangoURL, username=username, password=password, verify=True, verbose=True, statsdClient=None, reportFileName=None, loadBalancing='round-robin', use_grequests=False, use_jwt_authentication=False, use_lock_for_reseting_jwt=True, max_retries=10)
    db_name = 'metadata'

    def __init__(self):
        if not self.db_client.hasDatabase('metadata'):
            self.db = self.db_client.createDatabase('metadata')
            # self.db.createCollection(className='Collection', name='DataFields')
            # self.db.createCollection(className='Collection', name='Parameters')
            # self.db.createCollection(className='Collection', name='Labels')
            # self.db.createCollection(className='Collection', name='Log')
            # self.db.createCollection(className='Collection', name='countries')
            # self.db.createCollection(className='Collection', name='LocationHistoryCatalogue')
            # self.db.createCollection(className='Collection', name='cp')
        else:
            self.db = self.db_client['metadata']
        collections = ['DataFields', 'Parameters', 'Labels', 'Log', 'Countries', 'LocationHistoryCatalogue', 'Zipcodes']
        for collection in collections:
            if not self.db.hasCollection(collection):
                self.db.createCollection(collection)

    class DataFields(Collection):
        _fields = {
        }

    class Countries(Collection):
        _fields = {
        }

    class Parameters(Collection):
        _fields = {
        }   

    class Labels(Collection):
        _fields = {
        }   

    class Log(Collection):
        _fields = {
        }   

    class LocationHistoryCatalogue(Collection):
        _fields = {
        }   

    class Zipcodes(Collection):
        _fields = {
        }   

    class DataField(BasicElement):
        db_name = 'metadata'
        
        def get_all(self):
            filter = ' and '.join([ f'm.{att} == "{self.get(att)}"' if isinstance(self.get(att), str) else f'm.{att} == {self.get(att)}' for att in self.get('attributes') if self.get(att) != None])
            query = 'for m in '+ self.get_collection() +'\
                    FILTER '+filter+'\
                    SORT m.order\
                    return m'
            self.datafields = []
            try:
                [self.datafields.append(e) for e in self.db.AQLQuery(query, rawResults=True, batchSize=1000)]
            except:
                pass
            
        @classmethod
        def get_col_dict(cls):
            if os.environ.get('D20_ORM_CONF') != None:
                conf = json.loads(os.environ.get('D20_ORM_CONF'))
                col_dict=conf.get('D20_ORM_CLASS_TO_COL_MAP')  
            else:
                print("No configuration given, cannot start.")
                raise Exception
            return col_dict

        @classmethod
        def coll_to_class(cls, coll):
            col_dict = cls.get_col_dict()
            return col_dict.get(coll, coll)

        @classmethod
        def class_to_coll(cls, cl):
            col_dict = cls.get_col_dict()
            res = cl
            for e in col_dict.items():
                if e[1] == cl:
                    res = str(e[0])
                    break
            return res

        @classmethod
        def get_collection(cls):
            return 'DataFields'

        def get_class(self):
            return 'DataField'
                
        def make(self):
            self.obj_type = self.get_class().lower()
            self.active = True
            self.deleted = False
            self.attributes = ['obj_type', 'active', 'deleted']
            self.get_all()
            self.attributes = []
            [self.attributes.append(f.get('name')) for f in self.datafields]
            self.scopes = {}
            for f in self.datafields:
                if not f.get('scope') in self.get('scopes'):
                    self.scopes[f.get('scope')] = []
                self.scopes[f.get('scope')].append(f.get('name'))
            for key in self.attributes:
                setattr(self, key, None)

    class Parameter(BasicElement):
        db_name = 'metadata'
        
        @classmethod
        def get_collection(cls):
            return 'Parameters'

        def make(self):
            self.attributes = ['_key', 'name', 'desc', 'code', 'value', 'created', 'updated', 'active', 'deleted']
            for key in self.attributes:
                setattr(self, key, None)

    class Label(BasicElement):
        db_name = 'metadata'
        
        @classmethod
        def get_collection(cls):
            return 'Labels'

        def make(self):
            self.attributes = ['_key', 'name', 'lang', 'code', 'value', 'created', 'updated', 'active', 'deleted']
            for key in self.attributes:
                setattr(self, key, None)


    class LogEntry(BasicElement):
        db_name = 'metadata'
        
        @classmethod
        def get_collection(cls):
            return 'Log'

        def make(self):
            self.attributes = ['_key', 'action', 'user', 'api_user', 'datetime', 'token', 'api_token', 'source', 'user_agent', 'user_location', 'user_ip', 'host_ip']
            for key in self.attributes:
                setattr(self, key, None)


    class LocationLog(BasicElement):
        db_name = 'metadata'
        
        @classmethod
        def get_collection(cls):
            return 'LocationHistoryCatalogue'

        def make(self):
            self.attributes = ['_key', 'type', 'location', 'date']
            for key in self.attributes:
                setattr(self, key, None)

    class Countries_col(BasicElement):
        db_name = 'metadata'
        
        @classmethod
        def get_collection(cls):
            return 'Countries'

        def make(self):
            self.attributes = ['_key', 'name', 'translations', 'alpha3Code']
            for key in self.attributes:
                setattr(self, key, None)

        def get_all(self):
            query = 'for m in '+ self.get_collection() +'\
                    return m'
            self.datafields = []
            try:
                [self.datafields.append(e) for e in self.db.AQLQuery(query, rawResults=True, batchSize=1000)]
            except:
                pass


    class cp_col(BasicElement):
        db_name = 'metadata'
        
        @classmethod
        def get_collection(cls):
            return 'Zipcodes'

        def make(self):
            self.attributes = ['_key', 'IdEnt', 'Entidad', 'Ciudad', 'Municipio', 'Colonia', 'CP']
            for key in self.attributes:
                setattr(self, key, None)

        def get_all(self):
            query = 'for m in '+ self.get_collection() +'\
                    return m'
            self.datafields = []
            try:
                [self.datafields.append(e) for e in self.db.AQLQuery(query, rawResults=True, batchSize=1000)]
            except:
                pass

        def get_by_cp(self, cp):
            query = 'for m in '+ self.get_collection() +'\
                    filter m.CP == "' + cp + '"\
                    return m'
            self.datafields = []
            try:
                [self.datafields.append(e) for e in self.db.AQLQuery(query, rawResults=True, batchSize=1000)]
            except:
                pass

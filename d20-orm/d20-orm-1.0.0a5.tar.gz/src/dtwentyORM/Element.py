# File: ArangoDB ORM
# Author: alexsanchezvega
# Company: d20
# Version: 2.0

from pyArango.connection import *
from pyArango.collection import *
from pyArango.graph import *
from .support import *
from .BasicElement import BasicElement

class Element(BasicElement):

    from .Metadata import Metadata

    def get_class(self):
        return 'Element'

    def dict_by_scope(self, scopes=[]):
        res = {}
        for s in scopes:
            if s in self.get('scopes'):
                for a in self.get('scopes')[s]:
                    res[a] = self.get(a)
        return res

    def make(self):
        df = self.Metadata.DataField('set', {'obj_type':self.get_class().lower(), 'active': True, 'deleted': False})
        df.get_all()
        dfa = df.get('datafields')
        self.data_fields = dfa
        self.attributes = []
        [self.attributes.append(f.get('name')) for f in self.data_fields]
        self.scopes = {}
        self.obj_attributes = []
        for f in self.data_fields:
            if f.get('type') == 'object' and f.get('isArray') != True:
                self.obj_attributes.append({'name':f.get('name'), 'obj_type':f.get('subtype')})
            if not f.get('scope') in self.get('scopes'):
                self.scopes[f.get('scope')] = []
            self.scopes[f.get('scope')].append(f.get('name'))
        for key in self.attributes:
            setattr(self, key, None)
            
    def get_related_object(self, otype, okey):
        cached_res = search_obj_cache(otype, okey)
        if cached_res != None:
            return cached_res
        ans = []
        obj = self.db[self.Metadata.DataField.class_to_coll(otype)].fetchDocument(okey)
        df = self.Metadata.DataField('set', {'obj_type':self.Metadata.DataField.coll_to_class(otype).lower(), 'active': True, 'deleted' :False, 'search_extract':True})
        df.get_all()
        dfb = self.Metadata.DataField('set', {'obj_type':self.Metadata.DataField.coll_to_class(otype).lower(), 'active': True, 'deleted' :False, 'scope':'basic'})
        dfb.get_all()
        schema = df.get('datafields', [])
        schema_basic = dfb.get('datafields', [])
        ans = [obj.getStore(), schema, schema_basic]
        add_obj_cache(otype, okey, obj.getStore(), schema, schema_basic)
        return ans

    def find(self):
        try:
            found = self.db[self.get_collection()].fetchDocument(self._key)
            if found.getStore().get('deleted') == True:
                found = None
            for key in self.attributes:
                setattr(self, key, found.getStore()[key] if key in found.getStore() else self.get(key))
            for att in self.obj_attributes:
                try:
                    otype = att['obj_type']
                    att_val = self.get(att['name'])
                    if '_to' == att['name']:
                        otype = self.get('_to').split("/")[0]
                        self._to = self.get('_to').split("/")[1]
                        [o_to, schema, schema_basic] = self.get_related_object(otype, self._to)
                        if len(schema) > 0:
                            alias = schema[0]['name']
                            if alias in o_to:
                                self.alias_to = o_to[alias]
                            else:
                                self.alias_to = ''
                            self.attributes.append('alias_to')
                            self.scopes['basic'].append('alias_to')
                            self.obj_to = {}
                            for df in schema_basic:
                                if df['name'] in o_to:
                                    self.obj_to[df['name']] = o_to[df['name']] 
                            self.attributes.append('obj_to')
                            self.scopes['basic'].append('obj_to')
                    elif '_from' == att['name']:
                        otype = self.get('_from').split("/")[0]
                        self._from = self.get('_from').split("/")[1]
                        [o_from, schema, schema_basic] = self.get_related_object(otype, self._from)
                        if len(schema) > 0:
                            alias = schema[0]['name']
                            if alias in o_from:
                                self.alias_from = o_from[alias]
                            else:
                                self.alias_from = ''
                            self.attributes.append('alias_from')
                            self.scopes['basic'].append('alias_from')
                            self.obj_from = {}
                            for df in schema_basic:
                                if df['name'] in o_from:
                                    self.obj_from[df['name']] = o_from[df['name']] 
                            self.attributes.append('obj_from')
                            self.scopes['basic'].append('obj_from')
                    elif self.get(att['name']) != '' and self.get(att['name']) != [] and self.get(att['name']) != None:
                        [obj, schema, schema_basic] = self.get_related_object(otype, att_val)
                        if len(schema) > 0:
                            alias = schema[0]['name']
                            if alias in obj:
                                self.__setattr__(f'alias_{att["name"]}',obj[alias])
                                self.attributes.append(f'alias_{att["name"]}')
                                self.scopes['basic'].append(f'alias_{att["name"]}')
                            obj_p = {}
                            for df in schema_basic:
                                if df['name'] in obj:
                                    obj_p[df['name']] = obj[df['name']]
                            self.__setattr__(f'obj_{att["name"]}',obj_p)
                            self.attributes.append(f'obj_{att["name"]}')
                            self.scopes['basic'].append(f'obj_{att["name"]}')
                except:
                    pass
            self.status = True
        except:
            self._key = None
            self.status = False
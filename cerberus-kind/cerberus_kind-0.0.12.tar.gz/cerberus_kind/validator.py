import warnings
import cerberus
import json
import copy
from collections import OrderedDict
from .utils import kind_schema
warnings.simplefilter("ignore", UserWarning)

# Way 1: using cerberus API
class Validator(cerberus.Validator):
    def __init__(self, schema, *args, **kwargs):
        super().__init__(schema, *args, **kwargs)

    def validate(self, document, schema=None, update=False, normalize=True):
        schema = schema or self.schema
        if schema and '__root__' in schema:
            document = {'__root__': document}
        result = super(Validator, self).validate(document, schema, update=update, normalize=normalize)
        if '__root__' in self.document:
            # Unwrap.
            self.document = self.document['__root__']
            for e in self._errors:
                e.schema_path = tuple(e.schema_path[1:])
                if len(e.document_path) > 1:
                    e.document_path = tuple(e.document_path[1:])
        return result
        
    def normalized(self, document, schema=None, *args, **kwargs):
        if 'ordered' in kwargs: 
            self._config['_ordered'] = kwargs.get('ordered', False)
            del kwargs['ordered']
        if not schema: schema = copy.deepcopy(self.schema)
        if schema and '__root__' in schema:
            document = {'__root__': document}
        for k, v in schema.items():
            selector_schema = v.get('selector')
            if selector_schema and len(selector_schema):
                kind = document.get(k, {}).get('kind', '').lower()
                if not kind in selector_schema:
                    kind = next(iter(selector_schema))  # default schema
                # Replace
                v['schema']=v['selector'][kind]
                del v['selector']
                v['schema']['kind'] = kind_schema(kind)
        result = super(Validator, self).normalized(document, schema, *args, **kwargs)
        if self._config.get('_ordered'):
            result = OrderedDict(sorted(result.items(), key=lambda x: self.schema.get(x[0],{}).get('order', float('inf')))) 
        if '__root__' in result:
            result = result['__root__']
        return result

    def normalized_by_order(self, document, schema=None, *args, **kwargs):
        return self.normalized(document, schema, ordered=True, *args, **kwargs)

    def _validate_order(self, constraint, field, value):
        '''For use YAML Editor'''
    
    def _validate_selector(self, constraint, field, value):
        value = value or {}
        kind = value.get('kind', '').lower()
        if not kind in constraint: kind = next(iter(constraint.keys()))
        schema = constraint.get(kind)
        schema['kind'] = kind_schema(kind)
        validator = self._get_child_validator(field, (field, kind), schema=schema)
        if not validator(value, update=self.update, normalize=hasattr(self, 'document')):
            self._error(field, cerberus.errors.ERROR_GROUP, validator._errors)

# Way 2: Reconstruct schema and replace

# class Validator(cerberus.Validator):
#     def __init__(self, schema, *args, **kwargs):
#         super().__init__(schema, *args, **kwargs)
#         # self._selector_list, self._schema_map
#         if not self.is_child and not self.is_fork: 
#             self._prepare_schema()

#     @property
#     def is_fork(self):
#         return self._config.get('_fork')

#     @property
#     def is_ordered(self):
#         return self._config.get('_ordered')

#     def _prepare_schema(self, schema=None):
#         schema_map = {}
#         selector_list = []
#         def attach_kind(doc):
#             default_key = next(iter(doc)).title()
#             for k, v in doc.items():
#                 v['kind'] = {
#                     'type': 'string',
#                     'allowed': [k.title()],
#                     'default': default_key,
#                     'order': 0
#                 } 
#         def traverse(doc, path=[], fullpath=[], is_metadata=False):
#             if isinstance(doc, dict) or isinstance(doc, cerberus.schema.DefinitionSchema):
#                 if is_metadata:
#                     schema_map['.'.join(path)] = doc
#                     for k, v in doc.items():
#                         if k == 'selector':
#                             selector_list.append({
#                                 'doc_path': path,
#                                 'base_path': fullpath[:-1] if path[-1] == '*' else fullpath,
#                                 'valuesrules': path[-1] == '*',
#                             })
#                             attach_kind(v)
#                         if k in ['schema']:
#                             traverse(v, path, fullpath+[k], False)
#                         elif k in ['selector']:
#                             for _ in v:
#                                 traverse(v[_], path+[f"[{_}]"], fullpath+["schema"], False)
#                         elif k in ['valuesrules']:
#                             traverse(v, path+['*'], fullpath+[k], True)
#                 else:
#                     for k, v in doc.items():
#                         traverse(v, path+[k], fullpath+[k], True)
#         if schema: self.schema = schema
#         traverse(self.schema)
#         self._schema_map = schema_map
#         self._selector_list = selector_list

#     def _freeze_schema(self, document):
#         frozen = json.loads(json.dumps(dict(self.schema)))
#         def get_kind(doc, path, stack=[]):
#             if path:
#                 key = path.pop(0)
#                 if key[0] == '[' and key[-1] == ']':
#                     kind = key[1:-1]
#                     if kind == doc.get('kind').lower():
#                         yield from get_kind(doc, path, stack+[key])
#                 elif key == '*':
#                     for k in doc:
#                         yield from get_kind(doc.get(k), path, stack+[k])  
#                 else:
#                     yield from get_kind(doc.get(key), path, stack+[key])   
#             else:
#                 yield stack[-1], doc.get('kind')
#         removal_path = set([])
#         for i in self._selector_list:
#             base = frozen
#             for _ in i['base_path']:
#                 base = base[_]
#             if i['valuesrules']:
#                 base['schema'] = base.get('schema', {})
#                 for key, kind in get_kind(document, json.loads(json.dumps(i['doc_path']))):
#                     base['schema'][key] = {
#                         'type': 'dict',
#                         'schema': base['valuesrules']['selector'][kind.lower()]
#                     }
#                     removal_path.add('.'.join(i['base_path']+['valuesrules']))
#             else:
#                 for key, kind in get_kind(document, json.loads(json.dumps(i['doc_path']))):
#                     base['schema'] = base['selector'][kind.lower()]
#                     removal_path.add('.'.join(i['base_path']))
#         for _ in removal_path:
#             base = frozen
#             for path in _.split('.'):
#                 base = base[path]
#             del base['selector']
#         return frozen

#     def validate(self, document, schema=None, update=False, normalize=True):
#         if self.is_child or self.is_fork:
#             result = super(Validator, self).validate(document, update=update, normalize=normalize)
#         else:
#             if schema: self._prepare_schema(schema)
#             if self.schema and '__root__' in self.schema:
#                 document = {'__root__': document}
#             schema = self._freeze_schema(document)
#             self._validator = self.__class__(schema, allow_unknown=self.allow_unknown, purge_unknown=self.purge_unknown, require_all=self.require_all, _fork=True)
#             result = self._validator.validate(document, update=update, normalize=normalize)
#             self.document = self._validator.document
#             self._errors = self._validator._errors
#             if '__root__' in self.document:
#                 # Unwrap.
#                 self.document = self.document['__root__']
#                 for e in self._errors:
#                     e.schema_path = tuple(e.schema_path[1:])
#                     if len(e.document_path) > 1:
#                         e.document_path = tuple(e.document_path[1:])
#         return result
    
#     def normalized(self, document, schema=None, *args, **kwargs):
#         if self.is_child or self.is_fork:
#             result = super(Validator, self).normalized(document, schema, *args, **kwargs)
#             if self.is_ordered:
#                 result = OrderedDict(sorted(result.items(), key=lambda x: self.schema.get(x[0],{}).get('order', float('inf')))) 
#         else:
#             if schema: self._prepare_schema(schema)
#             if self.schema and '__root__' in self.schema:
#                 document = {'__root__': document}
#             schema = self._freeze_schema(document)

#             ordered = kwargs.get('ordered')
#             if ordered is not None: del kwargs['ordered']
#             self._validator = self.__class__(schema, allow_unknown=self.allow_unknown, purge_unknown=self.purge_unknown, require_all=self.require_all, _fork=True, _ordered=ordered)
#             result = self._validator.normalized(document, schema, *args, **kwargs)
#             if '__root__' in result:
#                 result = result['__root__']
#         return result

#     def _kind_schema(self, kind):
#         return {
#             'type': 'string',
#             'allowed': [kind.title()],
#             'default': kind.title(),
#             'order': 0
#         }

#     def normalized_by_order(self, document, schema=None, *args, **kwargs):
#         return self.normalized(document, schema, ordered=True, *args, **kwargs)

#     def _validate_order(self, constraint, field, value):
#         '''For use YAML Editor'''
    
#     def _validate_selector(self, constraint, field, value):
#         ...
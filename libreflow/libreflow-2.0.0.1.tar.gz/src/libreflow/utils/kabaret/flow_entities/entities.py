import time

from kabaret import flow
from kabaret.flow_entities.entities import Entity, EntityCollection


class CustomEntityCollection(EntityCollection):
    '''
    This class provides add and remove operators, and allows type injections
    on elements whose type is derived from its mapped_type (returned by
    `mapped_type()`).
    '''
    _mapped_types = flow.HashParam()

    def get_property(self, entity_name, property_name):
        value = (
            self.get_entity_store()
            .get_collection(self.collection_name())
            .find_one(
                {'name': entity_name},
                { property_name: 1},
            )
        )
        try:
            return value[property_name]
        except KeyError:
            default = getattr(self._get_mapped_item_type(entity_name), property_name).get_default_value()
            return default

    def add(self, name, object_type=None):
        '''
        Adds an object to the map.
        If provided, object_type must be a subclass of the map's mapped_type (returned by the
        classmethod mapped_type())
        '''
        mapped_type = flow.injection.resolve(
            self.mapped_type(), self
        )
        if object_type is None:
            object_type = mapped_type
        elif not issubclass(object_type, mapped_type):
            raise TypeError(
                'Cannot add %r of type %r to Map %r: not a subclass of %r' % (
                    name, object_type, self.oid(), mapped_type
                )
            )
        else:
            # Resolve potential injections on provided object type
            object_type = flow.injection.resolve(object_type, self)

        if '.' in name:
            raise TypeError(
                'Invalid object name %r (it must be a valid attribute name).' % (name,))
        try:
            exec(name + '=None') in {}
        except:
            raise TypeError(
                'Invalid object name %r (it must be a valid attribute name).' % (name,))
        if name in dir(self):
            raise ValueError(
                'Cannot add an item "%r", this name is already defined in the class "%s" (%s).' %
                (
                    name, self.__class__.__name__, self._mng.oid()
                )
            )
        if self.has_mapped_name(name):
            raise ValueError(
                'An item %r is already mapped in %r.' %
                (
                    name, self._mng.oid()
                )
            )

        object_qualified_type_name = self._mng.get_qualified_type_name(
            object_type)
        
        c = self.get_entity_store().get_collection(self.collection_name())
        c.insert_one({'name': name})
        self._mapped_types.set_key(name, object_qualified_type_name)

        # Reset collection cache to get newly created entry
        self._document_cache = None

        return self.get_mapped(name)

    def remove(self, name):
        self._mapped_types.del_key(name)
        c = self.get_entity_store().get_collection(self.collection_name())
        c.delete_one({'name': name})

    def _get_mapped_item_type(self, mapped_name):
        '''
        Returns the type of the given mapped item.
        NB: The GUI assumes that the returned type is a subclass
        of mapped_type().

        '''
        object_qualified_type_name = self._mapped_types.get_key(mapped_name)
        try:
            object_type = self._mng.qualified_type_name_to_type(
                object_qualified_type_name
            )
        except ImportError:
            mapped_type = flow.injection.resolve(
                self.mapped_type(), self
            )
            logging.getLogger('kabaret.ui').debug(
                'WARNING: unable to access type %r. Downgrading to map default type %r' % (
                    object_qualified_type_name, mapped_type
                )
            )
            object_type = mapped_type
        return object_type


class GlobalEntityCollection(EntityCollection):
    '''
    An entity collection which stores entities at the scope of an entire project.

    Entities of this collection are mapped by their oids.
    '''
    
    def columns(self):
        return ['Oid', 'Type']
    
    def _fill_row_cells(self, row, item):
        self.mapped_names()

        oid = item.oid()
        row['Oid'] = oid
        row['Type'] = self._document_cache[oid].get(
            'mapped_type',
            self._mng.get_qualified_type_name(self.mapped_type())
        )
    
    def get_mapped(self, name):
        return self.root().get_object(name)


class EntityView(EntityCollection):
    '''
    A collection acting as a view on a subset of a GlobalEntityCollection.

    User may return the global collection name in the `collection_name()` method.
    '''

    def mapped_names(self, page_num=0, page_size=None):
        oids = super(EntityView, self).mapped_names(page_num, page_size)
        return [oid.rsplit('/', maxsplit=1)[-1] for oid in oids]

    def query_filter(self):
        return {'name': {'$regex': f'^{self.oid()}/[^/]*'}}
    
    def add(self, name, object_type=None):
        '''
        Adds an object to the map.
        If provided, object_type must be a subclass of the map's mapped_type (returned by the
        classmethod mapped_type())
        '''
        mapped_type = flow.injection.resolve(
            self.mapped_type(), self
        )

        # Check file type
        if object_type is None:
            object_type = mapped_type
        elif not issubclass(object_type, mapped_type):
            raise TypeError(
                'Cannot add %r of type %r to Map %r: not a subclass of %r' % (
                    name, object_type, self.oid(), mapped_type
                )
            )

        # Check file name
        if '.' in name:
            raise TypeError(
                'Invalid object name %r (it must be a valid attribute name).' % (name,))
        try:
            exec(name + '=None') in {}
        except:
            raise TypeError(
                'Invalid object name %r (it must be a valid attribute name).' % (name,))
        if name in dir(self):
            raise ValueError(
                'Cannot add an item "%r", this name is already defined in the class "%s" (%s).' %
                (
                    name, self.__class__.__name__, self._mng.oid()
                )
            )
        
        if self.has_mapped_name(name):
            raise ValueError(
                'An item %r is already mapped in %r.' %
                (
                    name, self._mng.oid()
                )
            )

        object_qualified_type_name = self._mng.get_qualified_type_name(object_type)
        oid = f'{self.oid()}/{name}'

        # Add entry to project's Mongo store
        self.get_entity_store().get_collection(self.collection_name()).insert_one({
            'name': oid,
            'mapped_type': object_qualified_type_name
        })
        self._document_cache = None # Reset cache

        return self.get_mapped(name)

    def remove(self, name):
        '''
        Removes an Entity from the map.
        '''
        try:
            self._mng.destroy_child(name)
        except flow.MissingChildError:
            # was not yet instantiated, nothing to destroy
            pass

        self.get_entity_store().get_collection(self.collection_name()).delete_one(
            {'name': f'{self.oid()}/{name}'}
        )
        self._document_cache = None # Reset cache
    
    def clear(self):
        '''
        Clears all Entities belonging to this map.
        '''
        for name in self.mapped_names():
            try:
                self._mng.destroy_child(name)
            except flow.MissingChildError:
                # was not yet instantiated, nothing to destroy
                pass
        
        self.get_entity_store().get_collection(self.collection_name()).delete_many(
            self.query_filter()
        )
        self._document_cache = None # Reset cache
    
    def set_property(self, entity_name, property_name, value):
        self.get_entity_store().get_collection(self.collection_name()).update_one(
            {"name": f'{self.oid()}/{entity_name}'},
            {"$set": {property_name: value}},
        )

    def get_property(self, entity_name, property_name):
        self.root().session().log_debug(f'===========> {self.oid()}/{entity_name} {property_name}')
        value = (
            self.get_entity_store()
            .get_collection(self.collection_name())
            .find_one(
                {"name": f'{self.oid()}/{entity_name}'},
                {property_name: 1},
            )
        )
        try:
            return value[property_name]
        except KeyError:
            default = getattr(self._get_mapped_item_type(entity_name), property_name).get_default_value()
            return default
    
    def _fill_row_cells(self, row, item):
        if self._document_cache is None:
            # trigger a cache update:
            # FIXME: this cache update is not paginated :'(
            self.mapped_names()
        entity_oid = item.oid()
        for name, label in self.mapped_type().get_property_names_and_labels():
            row[label] = self._document_cache[entity_oid].get(name, "")
        row['Name'] = item.name()

    def _get_mapped_item_type(self, mapped_name):
        self.mapped_names()
        
        oid = f'{self.oid()}/{mapped_name}'
        object_qualified_type_name = self._document_cache[oid].get('mapped_type', None)
        
        if object_qualified_type_name is None:
            return self.mapped_type()
        
        try:
            object_type = self._mng.qualified_type_name_to_type(
                object_qualified_type_name
            )
        except ImportError:
            object_type = self.mapped_type()
            self.root().session().log_debug(
                'WARNING: unable to access type %r. Downgrading to map default type %r' % (
                    object_qualified_type_name, object_type
                )
            )
        
        return object_type

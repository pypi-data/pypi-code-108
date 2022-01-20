#!/usr/bin/env python3

from __future__ import print_function

import json


#==================================================================================================
''' class PlaceHolder

    This class allows using attributes to read property bag values
    without modifying the property bag.

'''
class PlaceHolder():

    ''' Constructor
    '''
    def __init__(self, pb, k, defstr, defval):
        self.__dict__['pb'] = pb
        self.__dict__['k'] = [k]

        self.__dict__['defval'] = defval
        try:
            self.__dict__['throwval'] = issubclass(defval, Exception)
        except:
            self.__dict__['throwval'] = False

        self.__dict__['defstr'] = defstr
        try:
            self.__dict__['throwstr'] = issubclass(defstr, Exception)
        except:
            self.__dict__['throwstr'] = False

    ''' Get attribute operator
        @param [in] k   - Attribute name
    '''
    def __getattr__(self, k):
        self.__dict__['k'].append(k)
        return self

    ''' Get item operator
        @param [in] k   - item name
    '''
    def __getitem__(self, k):
        self.__dict__['k'].append(k)
        return self

    ''' Set attribute operator
        @param [in] k   - Attribute name
        @param [in] v   - Attribute value to set
    '''
    def __setattr__(self, k, v):
        pb = self.__dict__['pb']
        for i in self.__dict__['k']:
            pb[i] = dict()
            pb = pb[i]
        pb[k] = v

    ''' Throws an error, trying to delete a non-existent key
        @param [in] k   - Key of item to be deleted
    '''
    def __delattr__(self, k):
        raise ValueError('No such key : %s'%'.'.join(self.__dict__['k']))

    ''' Throws an error, trying to call non-existent value
    '''
    def __call__(self, *args):
        raise ValueError('Not callable : %s'%'.'.join(self.__dict__['k']))

    ''' Return false if cast to bool, or default value if it is bool
    '''
    def __bool__(self):
        if self.__dict__['throwval']:
            raise self.__dict__['defval']('No such key : %s'%'.'.join(self.__dict__['k']))
        return bool(self.__dict__['defval'])

    ''' Return 0 if cast to int, or default value if int
    '''
    def __int__(self):
        if self.__dict__['throwval']:
            raise self.__dict__['defval']('No such key : %s'%'.'.join(self.__dict__['k']))
        return int(self.__dict__['defval'])

    ''' Return 0 if cast to index, or default value if int
    '''
    def __index__(self):
        if self.__dict__['throwval']:
            raise self.__dict__['defval']('No such key : %s'%'.'.join(self.__dict__['k']))
        return -1

    ''' Return 0 if cast to float, or default value if float
    '''
    def __float__(self):
        if self.__dict__['throwval']:
            raise self.__dict__['defval']('No such key : %s'%'.'.join(self.__dict__['k']))
        return float(self.__dict__['defval'])

    ''' Compares the object to the default value if same type, otherwise returns false
    '''
    def __compare(self, other, f):
        if self.__dict__['throwval']:
            raise self.__dict__['defval']('No such key : %s'%'.'.join(self.__dict__['k']))
        if type(other) == type(self.__dict__['defval']):
            return f(other, type(other)(self.__dict__['defval']))
        return False

    def __eq__(self, other):
        return self.__compare(other, lambda a, b: a == b)
    def __gt__(self, other):
        return self.__compare(other, lambda a, b: a > b)
    def __ge__(self, other):
        return self.__compare(other, lambda a, b: a >= b)
    def __lt__(self, other):
        return self.__compare(other, lambda a, b: a < b)
    def __le__(self, other):
        return self.__compare(other, lambda a, b: a <= b)

    ''' Throws an error or returns a default value
    '''
    def __repr__(self):
        if self.__dict__['throwstr']:
            raise self.__dict__['defstr']('No such key : %s'%'.'.join(self.__dict__['k']))
        return str(self.__dict__['defstr'])



#==================================================================================================
''' class Bag

    Flexible property bag container.

    @begincode

        bag = pb.Bag({'a':'b'}, c='d')
        print(bag)                      # > {"a": "b", "c": "d"}

        bag.b.c.d.e = 42
        print(bag.b.c.d.e)              # > 42
        print(bag.toJson())             # > {"a": "b", "c": "d", "b": {"c": {"d": {"e": 42}}}}

    @endcode
'''
class Bag():

    ''' Constructor
        @param [in] i           - dict to initialize object with
        @param [in] defstr      - Default string value when non exists
        @param [in] defval      - Default value when non exists

        If default values are not provided, an exception willl be thrown instead.
    '''
    def __init__(self, _i=None, _defstr=ValueError, _defval=None, **kwargs):

        self.__dict__['defstr'] = _defstr
        self.__dict__['defval'] = _defval

        if isinstance(_i, dict):
            self.__dict__['pb'] = _i
        elif isinstance(_i, Bag):
            self.__dict__['pb'] = _i.__dict__['pb']
        elif isinstance(_i, str):
            self.__dict__['pb'] = json.loads(_i)
        else:
            self.__dict__['pb'] = dict()

        if len(kwargs):
            self.__dict__['pb'].update(kwargs)

    ''' Index operator
        @param [in] k   - Key to return
    '''
    def __getitem__(self, k):
        if k not in self.pb:
            return PlaceHolder(self.pb, k, self.__dict__['defstr'], self.__dict__['defval'])
        if isinstance(self.pb[k], dict):
            return Bag(self.pb[k])
        return self.pb[k]
        # return self.pb[k]

    ''' Assignment operator
        @param [in] k   - Key to set
        @param [in] v   - New value to set
    '''
    def __setitem__(self, k, v):
        self.pb[k] = v

    ''' Delete item operator
        @param [in] k   - Key of item to be deleted
    '''
    def __delitem__(self, k):
        del self.pb[k]

    ''' Get attribute operator
        @param [in] k   - Attribute name
    '''
    def __getattr__(self, k):
        if k not in self.pb:
            return PlaceHolder(self.pb, k, self.__dict__['defstr'], self.__dict__['defval'])
        if isinstance(self.pb[k], dict):
            return Bag(self.pb[k])
        return self.pb[k]

    ''' Set attribute operator
        @param [in] k   - Attribute name
        @param [in] v   - Attribute value to set
    '''
    def __setattr__(self, k, v):
        self.__dict__['pb'][k] = v

    ''' Delete item operator
        @param [in] k   - Key of item to be deleted
    '''
    def __delattr__(self, k):
        del self.pb[k]


    ''' Length operator
    '''
    def __len__(self):
        return len(self.pb)

    ''' String cast
    '''
    def __str__(self):
        return self.toJson()

    ''' Object declaration cast
    '''
    def __repr__(self):
        items = (f"{k}={v!r}" for k, v in self.pb.items())
        return "{}({})".format(type(self).__name__, ", ".join(items))

    ''' Key iterator
    '''
    def __iter__(self):
        for k in self.pb:
            yield k

    ''' Equality operator
    '''
    def __eq__(self, other):
        if isinstance(other, dict):
            return self.pb == other
        elif isinstance(other, Bag):
            return self.pb == other.pb
        return NotImplemented

    ''' Return object as dict
    '''
    def as_dict(self):
        return self.pb

    ''' Get value using compound key
        @param [in] ks      - Compound key
        @param [in] defval  - Default value
        @param [in] sep     - Key separator

        @returns    The value at the specified key or defval
                    if the key path is not found.

        Example:
        @begincode

            # Equivalent to v = pb['path']['to']['value']
            v = pb.get("path.to.value", "default")
            v = pb.get("path/to/value", "default", "/")

        @endcode
    '''
    def get(self, ks, defval=None, sep='.'):
        d = 0
        r = self.pb
        try:
            if not isinstance(ks, str):
                return r[ks] if ks in r else defval
            if not ks:
                return r
            for k in ks.split(sep):
                if not isinstance(r, dict) and not isinstance(r, Bag):
                    return defval
                d += 1
                r = r[k]
        except Exception as e:
            return defval
        return r if 0 < d else defval

    ''' Return True if key exists, else False
        @param [in] ks      - Compound key
        @param [in] sep     - Key separator

        @returns    True if key exists, else False.

        Example:
        @begincode

            pb.exists("path.to.value") == True

            pb.exists("path/to/value", "/") == False

        @endcode
    '''
    def exists(self, ks, sep='.'):
        d = 0
        r = self.pb
        try:
            if not isinstance(ks, str):
                return r[ks] if ks in r else defval
            if not ks:
                return r
            for k in ks.split(sep):
                if not isinstance(r, dict) and not isinstance(r, Bag):
                    return False
                d += 1
                r = r[k]
        except Exception as e:
            return False
        if 0 >= d:
            return False
        return True

    ''' Deletes the specified key
        @param [in] ks      - Compound key
        @param [in] sep     - Key separator

        @returns    True if key was deleted, else False.

        Example:
        @begincode

            pb.delete("path.to.value")
            pb.delete("path/to/value", "/")

        @endcode
    '''
    def delete(self, ks, sep='.'):
        d = 0
        a = self.pb
        r = None
        try:
            if not isinstance(ks, str):
                if ks in a:
                    del a[ks]
                    return True
            if not ks:
                return False
            for k in ks.split(sep):
                if not isinstance(a, dict) and not isinstance(a, Bag):
                    return False
                d += 1
                if r:
                    a = a[r]
                r = k
        except Exception as e:
            return False
        if 0 >= d:
            return False
        del a[r]
        return True

    ''' Set value using compound key
        @param [in] ks      - Compound key
        @param [in] val     - New value to set
        @param [in] sep     - Key separator

        Example:
        @begincode

            # Equivalent to pb['path']['to']['value'] = 42
            pb.set("path.to.value", 42)
            pb.set("path/to/value", 42, "/")

        @endcode
    '''
    def set(self, ks, val, sep='.'):
        if not ks:
            if isinstance(val, dict):
                self.__dict__['pb'] = val
            elif isinstance(val, Bag):
                self.__dict__['pb'] = val.pb
            return self.pb
        kn = None
        r = self.pb
        if not isinstance(ks, str):
            r[ks] = val
            return r[ks]
        for k in str(ks).split(sep):
            if kn:
                if kn not in r:
                    r[kn] = dict()
                elif not isinstance(r[kn], dict):
                    r[kn] = dict()
                r = r[kn]
            kn = k
        if kn:
            r[kn] = val
            return r[kn]
        return None

    ''' Get propertybag using compound key
        @param [in] ks      - Compound key
        @param [in] defval  - Default value
        @param [in] sep     - Key separator

        Same as get(), but returns a propertybag object instead of dict

        @returns    The propertybag at the specified key or defval
                    if the key path is not found.

        Example:
        @begincode

            # Equivalent to v = pb.path.to.value
            v = pb.pb("path.to.value", "default")
            v = pb.pb("path/to/value", "default", "/")

        @endcode
    '''
    def bag(self, ks, defval=None, sep='.'):
        d = 0
        r = self.pb
        try:
            if not isinstance(ks, str):
                if ks not in r:
                    return defval
                d += 1
                r = r[ks]
            elif not ks:
                return r
            else:
                for k in ks.split(sep):
                    if not isinstance(r, dict) and not isinstance(r, Bag):
                        return defval
                    d += 1
                    r = r[k]
        except Exception as e:
            return defval
        if 0 >= d:
            return defval
        if isinstance(r, dict):
            return Bag(r)
        return r

    ''' Merge the values from the specified property bag or array
    '''
    def merge(self, pb, overwrite=True):
        if isinstance(pb, dict):
            self.__dict__['pb'] = {**self.pb, **pb} if overwrite else {**pb, **self.pb}
        elif isinstance(pb, Bag):
            self.__dict__['pb'] = {**self.pb, **pb.pb} if overwrite else {**pb.pb, **self.pb}

    ''' Update property bag values
    '''
    def update(self, pb):
        if isinstance(pb, dict):
            self.__dict__['pb'].update(pb)
        elif isinstance(pb, Bag):
            self.__dict__['pb'].update(pb.pb)

    ''' Returns the dict items
    '''
    def items(self):
        return self.pb.items()

    ''' Returns the dict keys
    '''
    def keys(self):
        return self.pb.keys()

    ''' Returns the dict values
    '''
    def values(self):
        return self.pb.values()

    ''' Returns a copy of the property bag
    '''
    def copy(self):
        return Bag(self.pb.copy())

    ''' Converts properties to a json string
        @param [in] pretty      - Non-zero for a human friendly output
        @param [in] indent      - If pretty is set, set the indent size
        @param [in] sort_keys   - If pretty is set, sorts the keys when set
    '''
    def to_json(self, pretty=False, indent=2, sort_keys=True):
        if not pretty:
            return json.dumps(self.pb)
        else:
            return json.dumps(self.pb, indent=indent, sort_keys=sort_keys)

    ''' Alias for to_json()
    '''
    toJson = to_json

    ''' Initializes the object with the specified JSON string
        @param [in] s   - JSON string
    '''
    def from_json(s):
        self.pb = json.loads(s)

    ''' Alias for from_json()
    '''
    fromJson = from_json


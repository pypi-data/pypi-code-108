import requests
import json


"""
Helper classes for handling leversc settings changes
"""
class ChangeWrapper:
    """
    A wrapper class for bubbling property change updates to leversc class
    """
    def __init__(self, parent, incollection):
        self._parent = parent
        self._collection = incollection

    def _property_updated(self, childprop):
        self._parent._property_updated(self)

    def __getitem__(self, keyidx):
        elem = self._collection.__getitem__(keyidx)
        if isinstance(elem, (dict,list)):
            return __class__(self, elem)
        else:
            return elem
    
    def __setitem__(self, keyidx, v):
        self._collection.__setitem__(keyidx,v)
        self._property_updated(self)

    """
    Some Quality-of-life improvements for introspecting the wrappers
    """
    def __str__(self):
        return str(self._collection)

    def __repr__(self):
        return "%s(%s)"%(__class__.__name__, repr(self._collection))


class PropWrapper(ChangeWrapper):
    """
    Top-level property that runs setProperty (network send) on change updates
    """
    def __init__(self, lsc, propname, incollection):
        self._leversc = lsc
        self._propname = propname
        super(__class__,self).__init__(self,incollection)

    def unwrap(self):
        """
        Return an unwrapped version of this property (that can be edited without network overhead)
        """
        return self._collection

    def _property_updated(self, childprop):
        self._leversc.setProperty(self._propname, self._collection)

    def __str__(self):
        return str(self._collection)

    def __repr__(self):
        return "%s(%s)"%(__class__.__name__, repr(self._collection))


# retrieves/sets viewParams, renderParams, uiParams, etc....
def setProperty(self,propertyName,propertyStruct):
    if isinstance(propertyStruct,PropWrapper):
        propertyStruct = propertyStruct.unwrap()
    URL = self._leversc_url("/"+propertyName)
    response = requests.post(URL,json=propertyStruct)
    
def getProperty(self,propertyName):
    URL = self._leversc_url("/"+propertyName)
    response = requests.get(URL)
    property = response.json()
    if 'list'==type(property):
        # view and render params come as 1 element list
        property = property[0]
    return PropWrapper(self,propertyName,property)

#coding: utf-8
from flask.json import JSONEncoder                                                                                                    
from datetime import date

class IsoJSONEncoder(JSONEncoder):                                                                                                    
    def default(self, obj):                                                                                                           
        try:                                                                                                                          
            if isinstance(obj, date):                                                                                                 
                return obj.isoformat().replace('+00:00', 'Z')
            iterable = iter(obj)                                                                                                      
        except TypeError:                                                                                                             
            pass                                                                                                                      
        else:                                                                                                                         
            return list(iterable)                                                                                                     
        return JSONEncoder.default(self, obj)  
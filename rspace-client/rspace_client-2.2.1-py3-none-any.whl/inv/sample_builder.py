# -*- coding: utf-8 -*-


class BaseSample:
    
        
    def setname(self, name):
        self.name=name
    def setdescription(self, description):
        self.description= description
    def settags (self, tags):
        self.tags = tags
    def __repr__(self):
        rc=f"""
        {type(self)} : name={self.name}, description ={self.desc}, tags={self.tags},
        fields = {self.__dict__}
        """
        return rc
                
    
    
class SampleBuilder:
    
    def __field_setter_factory(f):
        f_name = f['name']
        f_type= f['type']
        
       
        def fn(self, val=None):
            if val is not None:
                setattr(self, f_name, val)
                return self
            else:
                return  self.__dict__[f_name]
        fn.__name__= f_name
        fn.__doc__ = f"Set sample field named '{f_name}' of type '{f_type}'"
        return fn
    
    
    def __init__(self, sample_template):
        clazzname = sample_template['name']
        self.clazz = type(clazzname, (BaseSample,), {})
        for f in sample_template['fields']:
            f_name = f['name']
            func =  SampleBuilder.__field_setter_factory(f)
            setattr(self.clazz, f_name, func)
        
        
    def as_class(self):
        return self.clazz
            
    
st={'name':'Enzyme', 'fields': [{'name': 'a', 'type': 'string'}, {'name': 'b', 'type': 'number'}]}
a = SampleBuilder(st)
e= a.as_class()
e1=e()

## TODO - set type info in doc string. Include allowed values if radio or field.



import inspect
import dill as pickle
from pathlib import Path

import joblib

from humailib.cloud_tools import GoogleCloudStorage

class FunctionsGherkin:
    """
    This class finds, saves, loads and reinstates all local functions that have a certain
    parameter signature.
    """
    
    def __init__(self):
        
        self.funcs = []
        return

    def find(self, vars_in_scope = None, param_signature = ['X','params']):
        
        if vars_in_scope is None:
            vars_in_scope = globals().copy()

        self.funcs = []
        for var_name in vars_in_scope:
            if inspect.isfunction( vars_in_scope[var_name] ):
                params = list( inspect.signature(vars_in_scope[var_name]).parameters )
                if params == param_signature:
                    self.funcs.append( (var_name, vars_in_scope[var_name], params) )
                    
                    
    def reinstate(self, vars_in_scope = None):
        
        if vars_in_scope is None:
            vars_in_scope = globals()
            
        for fname, fobj, params in self.funcs:
            print("[FunctionsGherkin::reinstate] Adding function '{}', with parameters = {}".format(fname, params))
            vars_in_scope[fname] = fobj
            
        return True
    

    def save(self, filename, gcs=None, cache_dir='./cache'):
        
        if 'gs://' in filename:
            if gcs is None:
                gcs = GoogleCloudStorage()
                
            cache_filename = cache_dir + '/' + filename.split('/')[-1]
            file = open(cache_filename, 'wb')
            pickle.dump(self.funcs, file)
            file.close()
            
            gcs.upload_file(cache_filename, filename)
        else:
            file = open(filename, 'wb')
            pickle.dump(self.funcs, file)
            file.close()
            
        return True
    
    
    def load(self, filename, gcs=None, cache_dir='./cache'):
        
        if 'gs://' in filename:
            if gcs is None:
                gcs = GoogleCloudStorage()
                
            cache_filename = Path(cache_dir + '/' + filename.split('/')[-1])
            gcs.download_file(filename, cache_filename)
            cache_filename = cache_dir + '/' + filename.split('/')[-1]
            file = open(cache_filename, 'rb')
            funcs = pickle.load(file)
            file.close()  

            self.funcs = funcs
        else:
            file = open(filename, 'rb')
            funcs = pickle.load(file)
            self.funcs = funcs
            file.close()  
            
        return True
    
    
    def load_and_reinstate(self, filename, vars_in_scope = None, gcs = None, cache_dir='./cache'):
        
        if self.load(filename, gcs=gcs, cache_dir=cache_dir):
            return self.reinstate(vars_in_scope = vars_in_scope)
    
        return False
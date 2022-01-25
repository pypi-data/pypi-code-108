from mudpy.containers import mvar, mhist, mdict

    
class vdict(mdict):
    def set(self, key, **kwargs):
        if key not in self.keys():
            self[key] = mvar(**kwargs)
        else:
            for s in mvar.__slots__:
                if s in kwargs.keys():
                    setattr(self[key], s, kwargs[s])
            
    # depreciate 1n volt ppg parameter
    def __getitem__(self, key): 
        
        if key in ['volt_start', 'volt_stop', 'volt_incr']:
            print("DEPRECIATION: 'volt_start', 'volt_stop', and 'volt_incr' "+\
                 "have been depreciated in favour of "+\
                 "'scan_start', 'scan_stop', and 'scan_incr'")
            
            key = key.replace('volt', 'scan')
        
        return dict.__getitem__(self, key)
        
class hdict(mdict):
    def set(self, key, **kwargs):
        if key not in self.keys():
            self[key] = mhist(**kwargs)
        else:
            for s in mhist.__slots__:
                if s in kwargs.keys():
                    setattr(self[key], s, kwargs[s])


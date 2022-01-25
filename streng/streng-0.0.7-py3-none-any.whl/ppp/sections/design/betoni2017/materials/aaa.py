from cached_property import cached_property

class MaterialsStrength:
    def __init__(self, fck, fyk, αcc=0.85, γc=1.5, γs=1.15):
        self.fck = fck
        self.fyk = fyk
        self.αcc = αcc
        self.γc = γc
        self.γs = γs

    @property
    def fck(self):
        return self._fck
    
    @fck.setter
    def fck(self, value):
        self.invalidate_cache('fcd')
        self._fck = value
  
    @property
    def γc(self):
        return self._γc
    
    @γc.setter
    def γc(self, value):
        self.invalidate_cache('fcd')
        self._γc = value

    @property
    def αcc(self):
        return self._αcc
    
    @αcc.setter
    def αcc(self, value):
        self.invalidate_cache('fcd')
        self._αcc = value

    @property
    def fyk(self):
        return self._fyk
    
    @fyk.setter
    def fyk(self, value):
        self.invalidate_cache('fcd')
        self._fyk = value
  
    @property
    def γs(self):
        return self._γs
    
    @γs.setter
    def γs(self, value):
        self.invalidate_cache('fcd')
        self._γs = value

    def _fcd_invalidate(self):
        if 'fcd' in self.__dict__.keys():
            del self.__dict__['fcd']

    def _fyd_invalidate(self):
        if 'fyd' in self.__dict__.keys():
            del self.__dict__['fyd']

    def invalidate_cache(self, key):
        if key in self.__dict__.keys():
            del self.__dict__[key]



    @cached_property
    def fcd(self):
        # print('calculating fcd')
        return self.αcc * self.fck / self.γc

    @cached_property
    def fyd(self):
        # print('calculating fyd')
        return self.fyk / self.γs



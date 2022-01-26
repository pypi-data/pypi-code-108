
class TObject:
    
    FUNDAMENTAL_TYPE = None
    
    @property
    def obj(self):
        return self._obj
    
    @obj.setter
    def obj(self, ref):
        if ref is None:
            self._obj = None
        elif not isinstance(ref, self.FUNDAMENTAL_TYPE):
            raise ValueError(f"Invalid ROOT object. Object must be an instance of {self.FUNDAMENTAL_TYPE}.")
        self._obj = ref
    
    def __init__(self, obj=None):
        self.obj = obj
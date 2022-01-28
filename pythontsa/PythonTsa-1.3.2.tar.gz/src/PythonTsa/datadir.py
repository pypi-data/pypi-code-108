def getdtapath():
      import os
      import PythonTsa 
      dtapath=os.path.dirname(PythonTsa.__file__)
      newdtapath=dtapath+'\\Ptsadata'
      
      return newdtapath
      

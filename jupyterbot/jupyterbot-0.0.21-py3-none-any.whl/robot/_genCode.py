
def _genCode(self):

  self._strFrames = str(self._frames)

  #Inject code

  if self._rtype == 'generic':
    self.code = '''
    const ''' + self._strName + ''' = new Robot(''' + self._strlinkInfo + ''',''' + self._strFrames + ''');
    sceneElements.push(''' + self._strName  + ''');
    //USER INPUT GOES HERE
    '''

  if self._rtype == 'sDOF':
    self.code = '''
    const ''' + self._strName + ''' = sDOF(''' + self._strFrames + ''');
    sceneElements.push(''' + self._strName + ''');
    //USER INPUT GOES HERE
    '''
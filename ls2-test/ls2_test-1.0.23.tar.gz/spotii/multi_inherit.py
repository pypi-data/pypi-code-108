class A():
    def __init__(self):
        print ('First %s nothing')

class B():
    def __init__(self, value):
        print ('Second %s' % value)

class Log(A, B):
    def __init__(self, b):
        A.__init__(self)
        B.__init__(self, b)

        print ('Log')

x = Log( 2222)

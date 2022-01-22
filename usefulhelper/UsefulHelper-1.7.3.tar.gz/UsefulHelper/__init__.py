"""
Helper
"""


# Emm...
class Start:
    def __init__(self, name, path):
        with open(path, 'w') as self.Project:
            self.Project.write('Name:' + name + '\n')

    def setup(self):
        pass

    def pack(self):
        pass


class BuildError(BaseException):
    def __init__(self, things):
        super(BuildError, self).__init__()
        print(things + ' is wrong')
        
        
class CreateError(BaseException):
    def __init__(self, get):
        super(CreateError, self).__init__()
        print(get)

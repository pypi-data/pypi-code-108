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

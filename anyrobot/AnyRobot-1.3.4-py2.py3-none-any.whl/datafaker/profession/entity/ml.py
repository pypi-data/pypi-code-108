
class machine(object):
    def __init__(self,search):
        self.search = search

    def inquire(self):
        if isinstance(self.search, list):
            return [12,23,45]
        else:
            return [34,56,67]
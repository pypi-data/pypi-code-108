
 
class Col:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.title = name

    def filter(self, product_qs):
        return product_qs

    def __repr__(self):
        return 'Col:' + str(self)

    def __str__(self):
        return self.code

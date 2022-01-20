

class Row:
    """ this is a list of cells """
    def __init__(self, product):
        self.product = product
        self.cells = []

    def add_cell(self, cell):
        self.cells.append(cell)

    def __repr__(self):
        return 'Row:' + str(self)

    def __str__(self):
        return str(self.product.id)

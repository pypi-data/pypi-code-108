

class dataset():

    def __init__(self):
        self.cols = []          # Stores the columns
        self.col_lbl = []       # Stores the name of the column
        self.col_type = []      # Stores the type of column (lbl vs feat)

    def __getitem__(self, key):
        if isinstance()

class column():

    def __init__(self):
        self.vals = []

    def __getitem__(self, key):
        return self.vals[key]
    def __setitem__(self, key, item):
        self.vals[key] = item

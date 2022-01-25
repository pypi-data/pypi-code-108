from .column import Column


class TextColumn(Column):
    
    def __init__(self, name):
        super().__init__(name, 'TEXT')
        self.name = name
        self.data_type = "TEXT"
    
    def __str__(self):
        ''' Returns a string in the format of MySQL '''
        
        sql = "{name} TEXT".format(name=self.name)
        
        return sql
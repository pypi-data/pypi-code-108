from ..column import Column


class CreatedAtColumn(Column):
    
    
    def __init__(self):
        super().__init__('created_at', 'TIMESTAMP')
        self.default = 'CURRENT TIMESTAMP'
    
    def __str__(self):
        ''' Returns a string in the form of a MySQL column '''
        
        sql = 'created_at TIMESTAMP NOT NULL DEFAULT {default}'.format(default=self.default)
        
        return sql
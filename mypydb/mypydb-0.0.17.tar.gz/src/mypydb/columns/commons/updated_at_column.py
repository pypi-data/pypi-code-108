from ..column import Column


class UpdatedAtColumn(Column):
    
    def __init__(self):
        super().__init__('updated_at', 'TIMESTAMP')
    
    def __str__(self):
        ''' Returns a string in the format of MySQL '''
        
        sql = "updated_at TIMESTAMP NULL DEFAULT NULL"
        
        return sql
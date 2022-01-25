from ..int_column import IntColumn


class CreatedByIdColumn(IntColumn):
    
    def __init__(self, length=11, nullable=True, default=None):
        super().__init__('created_by_id')
        self.length = length
        self.nullable = nullable
        self.default = default
    
    def __str__(self):
        ''' Returns a string in an SQL format '''
        
        sql = "{name} INT({length})".format(name=self.name, length=self.length)
        
        if self.nullable is True:
            sql += " NULL"
        
        if self.nullable is False:
            sql += " NOT NULL"
        
        if self.default is not None:
            sql += " DEFAULT {default}".format(default=self.default)
        
        return sql
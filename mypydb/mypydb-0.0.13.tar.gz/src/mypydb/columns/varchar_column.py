from .column import Column


class VarcharColumn(Column):
    
    def __init__(self, name, length, nullable=True, default=None):
        self.name = name
        self.data_type = 'VARCHAR'
        self.length = length
        self.nullable = nullable
        self.default = default
    
    def __str__(self):
        ''' Returns a string in the format of SQL '''
        
        sql = "{name} {data_type}({length})".format(name=self.name, data_type=self.data_type, length=self.length)
        
        if self.nullable is True:
            sql += " NULL"
        elif self.nullable is False:
            sql += " NOT NULL"
        
        if self.default is not None:
            sql += " DEFAULT {default}".format(default=self.default)
        
        return sql
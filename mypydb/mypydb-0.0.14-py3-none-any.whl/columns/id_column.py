from .column import Column


class IdColumn(Column):
    
    def __init__(self, name='id', length=11, nullable=False):
        super().__init__(name, 'INT')
        self.name = name
        self.data_type = 'INT'
        self.length = length
        self.nullable = nullable
        self.auto_increment = True
        self.primary_key = True
    
    def get_id_column_sql(self):
        return self.id_col_sql
    
    def __str__(self):
        ''' Returns a string in a format of MySQL for the column '''
        
        sql = "{name} INT({length})".format(name=self.name, length=self.length)
        
        if self.nullable is True:
            sql += " NULL"
        
        if self.nullable is False:
            sql += " NOT NULL"
        
        if self.auto_increment is True:
            sql += " AUTO_INCREMENT"
        
        if self.primary_key is True:
            sql += " PRIMARY KEY"
        
        return sql
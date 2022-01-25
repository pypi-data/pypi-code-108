from .column import Column


class DoubleColumn(Column):
    
    def __init__(self, name, nullable, default=None, num_digits=None, num_decimal_digits=None):
        super().__init__()
        self.name = name
        self.data_type = 'DOUBLE'
        self.num_digits = num_digits
        self.num_decimal_digits=num_decimal_digits
        self.nullable = nullable
        self.default = default
    
    def __str__(self):
        ''' Returns a string of the column in MySQL format '''
        
        sql = "{name} {data_type}".format(name=self.name, data_type=self.data_type)
        
        if self.num_digits is not None and self.num_decimal_digits is not None:
            sql += "({num_digits}, {num_decimal_digits})".format(num_digits=self.num_digits, num_decimal_digits=self.num_decimal_digits)
        
        if self.nullable is True:
            sql += " NULL"
        elif self.nullable is False:
            sql += " NOT NULL"
        
        if self.default is not None:
            sql += " DEFAULT {default}".format(default=self.default)
        
        return sql
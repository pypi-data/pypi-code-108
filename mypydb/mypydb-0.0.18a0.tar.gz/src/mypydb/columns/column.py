class Column():

    def __init__(self, name, data_type, length=None, nullable=False, default=None, auto_increment=False, primary_key=False, foreign_keys=False):
        self.name = name
        self.data_type = data_type
        self.length = length
        self.nullable = nullable
        self.default = default
        self.auto_increment = auto_increment
        self.primary_key = primary_key
        self.foreign_keys = foreign_keys

    def __str__(self):
        column = "{name} {data_type}".format(
            name=self.name, data_type=self.data_type)

        if self.length is not None:
            column += "({length})".format(length=self.length)

        if self.nullable == False:
            column += " NOT NULL"
        elif self.nullable == True:
            column += " NULL"

        if self.default is not None:
            column += " DEFAULT {default}".format(default=self.default)

        if self.auto_increment is True:
            column += " AUTO_INCREMENT"

        if self.primary_key is True:
            column += " PRIMARY KEY"

        return column

from mypydb.columns import Column, IdColumn
from mypydb.columns.commons import CreatedByIdColumn, CreatedAtColumn, UpdatedAtColumn


class Table():

    def __init__(self, name, if_not_exists=True, has_create_by_id=True):
        self.name = name
        self.if_not_exists = if_not_exists
        self.has_create_by_id = has_create_by_id
        self.columns = []
        # self.set_table_columns()
    
    def get_columns(self):
        return self.columns
    
    def set_columns(self, columns):
        self.columns.clear()
        for column in columns:
            self.columns.append(column.__str__())
    
    def set_table_columns(self):
        ''' Sets the columns for the table '''
        
        id_col = IdColumn()
        created_by_id_col = CreatedByIdColumn()
        created_at_col = CreatedAtColumn()
        updated_at_col = UpdatedAtColumn()
        
        self.columns.append(id_col.__str__())
        self.columns.append(created_by_id_col.__str__())
        self.columns.append(created_at_col.__str__())
        self.columns.append(updated_at_col.__str__())
    
    def get_create_table_sql(self):
        
        sql = "CREATE TABLE "
        
        if self.if_not_exists is True:
            sql += "IF NOT EXISTS {name} (".format(name=self.name)
        else:
            sql += "{name} (".format(name=self.name)
        
        for column in self.columns:
            sql += "{column}".format(column=column)
            if self.columns.index(column) == len(self.columns) - 1:
                sql += ");"
            else:
                sql += ", "
        
        return sql
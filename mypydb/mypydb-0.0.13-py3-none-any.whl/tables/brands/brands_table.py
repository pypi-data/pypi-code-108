from mypydb.columns import IdColumn, VarcharColumn, TextColumn
from mypydb.columns.commons import CreatedByIdColumn, CreatedAtColumn, UpdatedAtColumn
from mypydb.tables import Table


class BrandsTable(Table):

    def __init__(self, name, if_not_exists=True, has_create_by_id=True):
        super().__init__(name, if_not_exists, has_create_by_id)
        self.columns = []
        self.set_table_columns()
    
    def set_table_columns(self):
        ''' Sets the columns for this table '''
        
        id_col = IdColumn()
        self.columns.append(id_col.__str__())
        
        title_col = VarcharColumn('title', 45, nullable=False)
        self.columns.append(title_col.__str__())
        
        summary_col = TextColumn('summary')
        self.columns.append(summary_col.__str__())
        
        notes_col = TextColumn('notes')
        self.columns.append(notes_col.__str__())
        
        created_by_id_col = CreatedByIdColumn()
        self.columns.append(created_by_id_col.__str__())
        
        created_at_col = CreatedAtColumn()
        self.columns.append(created_at_col.__str__())
        
        updated_at_col = UpdatedAtColumn()
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
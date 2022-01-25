from mypydb.tables import Table
from mypydb.columns import IdColumn, VarcharColumn, TextColumn
from mypydb.columns.commons import CreatedByIdColumn, CreatedAtColumn, UpdatedAtColumn


class CategoriesTable(Table):

    def __init__(self, name='categories', if_not_exists=True, has_create_by_id=True):
        super().__init__(name=name, if_not_exists=if_not_exists, has_create_by_id=has_create_by_id)
        self.columns = []
        self.set_table_columns()
    
    def set_table_columns(self):
        ''' Sets the columns for the table '''
        
        id_col = IdColumn()
        self.columns.append(id_col.__str__())
        
        title_col = VarcharColumn('title', 100, nullable=False)
        self.columns.append(title_col.__str__())
        
        description_col = TextColumn('description')
        self.columns.append(description_col.__str__())
        
        notes_col = TextColumn('notes')
        self.columns.append(notes_col.__str__())
        
        created_by_id_col = CreatedByIdColumn()
        self.columns.append(created_by_id_col.__str__())
        
        created_at_col = CreatedAtColumn()
        self.columns.append(created_at_col.__str__())
        
        updated_at_col = UpdatedAtColumn()
        self.columns.append(updated_at_col.__str__())
    
    def get_create_table_sql(self):
        return super(CategoriesTable, self).get_create_table_sql()

from mypydb.columns import Column, IdColumn, VarcharColumn, IntColumn
from mypydb.columns.commons import CreatedAtColumn, UpdatedAtColumn
from mypydb.tables import Table


class UsersTable(Table):

    def __init__(self, name='users', if_not_exists=True):
        super().__init__(name=name, if_not_exists=if_not_exists, has_create_by_id=False)
        self.columns = []
        self.set_table_columns()
        
    def set_table_columns(self):
        ''' Sets the columns for the table '''
        
        id_col = IdColumn()
        self.columns.append(id_col.__str__())
        
        fname_col = VarcharColumn('first_name', 45, nullable=False)
        self.columns.append(fname_col.__str__())
        
        lname_col = VarcharColumn('last_name', 45, nullable=False)
        self.columns.append(lname_col.__str__())
        
        username_col = VarcharColumn('username', 45, nullable=False)
        self.columns.append(username_col.__str__())
        
        email_col = VarcharColumn('email', 255, nullable=False)
        self.columns.append(email_col.__str__())
        
        phone_col = VarcharColumn('phone', 20, nullable=True)
        self.columns.append(phone_col.__str__())
        
        address_id_col = IntColumn('address_id')
        self.columns.append(address_id_col.__str__())
        
        password_col = VarcharColumn('password', 255, nullable=False)
        self.columns.append(password_col.__str__())
        
        created_at_col = CreatedAtColumn()
        self.columns.append(created_at_col.__str__())
        
        updated_at_col = UpdatedAtColumn()
        self.columns.append(updated_at_col.__str__())
    
    def get_create_table_sql(self):
        return super(UsersTable, self).get_create_table_sql()
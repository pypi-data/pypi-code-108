from mypydb.tables import Table
from mypydb.columns import IdColumn, IntColumn, VarcharColumn, DoubleColumn, TextColumn
from mypydb.columns.commons import CreatedByIdColumn, CreatedAtColumn, UpdatedAtColumn


class PaymentsTable(Table):
    
    def __init__(self):
        self.name = 'payments'
        self.if_not_exists = True
        self.has_create_by_id = True
        
        ''' Create the columns '''
        
        id_col = IdColumn()
        customer_id_col = IntColumn('customer_id')
        payment_type_col = VarcharColumn('payment_type', 45, nullable=False)
        amount_col = DoubleColumn('amount', nullable=False)
        details_col = TextColumn('details')
        created_by_id_col = CreatedByIdColumn()
        created_at_col = CreatedAtColumn()
        updated_at_col = UpdatedAtColumn()
        
        self.columns = [
			id_col.__str__(), customer_id_col.__str__(), payment_type_col.__str__(), amount_col.__str__(),
			details_col.__str__(), created_by_id_col.__str__(), created_at_col.__str__(), updated_at_col.__str__()
		]
    
    def get_create_table_sql(self):
        return super(PaymentsTable, self).get_create_table_sql()
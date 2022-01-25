class Resource:
    name: str

    redshift_table_name: str

    def __init__(self, name: str, redshift_table_name: str):
        self.name = name
        self.redshift_table_name = redshift_table_name


resource_map = {
    'block': Resource(name='block',
                      redshift_table_name='blocks'),

    'transaction': Resource(name='transaction',
                            redshift_table_name='raw_transactions'),

    'log': Resource(name='log',
                    redshift_table_name='raw_logs'),

    'receipt': Resource(name='receipt',
                        redshift_table_name='receipts'),

    'contract': Resource(name='contracts',
                         redshift_table_name='raw_contracts'),

    'trace': Resource(name='trace',
                      redshift_table_name='raw_traces')
}

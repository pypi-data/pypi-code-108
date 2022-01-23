class Resource:
    name: str

    redshift_table_name: str

    exclude_columns: [int]

    bytea_columns: [int]

    def __init__(self,
                 name: str,
                 redshift_table_name: str,
                 exclude_columns: [int],
                 bytea_columns: [int],
                 bool_columns: [int]):
        self.name = name
        self.redshift_table_name = redshift_table_name
        self.exclude_columns = exclude_columns
        self.bytea_columns = bytea_columns
        self.bool_columns = bool_columns


resource_map = {
    'block': Resource(name='block',
                      redshift_table_name='blocks',
                      exclude_columns=[4, 5, 6, 7, 8, 13],
                      bytea_columns=[1, 2, 3, 9],
                      bool_columns=[]),

    'transaction': Resource(name='transaction',
                            redshift_table_name='raw_transactions',
                            exclude_columns=[],
                            bytea_columns=[0, 2, 5, 6, 10],
                            bool_columns=[]),

    'log': Resource(name='log',
                    redshift_table_name='raw_logs',
                    exclude_columns=[],
                    bytea_columns=[[1, 3, 5, 6]],
                    bool_columns=[]),

    'receipt': Resource(name='receipt',
                        redshift_table_name='receipts',
                        exclude_columns=[],
                        bytea_columns=[0, 2, 6, 7],
                        bool_columns=[]),

    'contract': Resource(name='contracts',
                         redshift_table_name='raw_contracts',
                         exclude_columns=[],
                         bytea_columns=[0, 1],
                         bool_columns=[]),

    'trace': Resource(name='trace',
                      redshift_table_name='raw_traces',
                      exclude_columns=[17],
                      bytea_columns=[1, 3, 4, 6, 7],
                      bool_columns=[15])
}

from typing import List

# pseudo-code to be executed when a dataset is added to a clean room from a data connection

CLEAN_ROOMS = {
    '80422c05-6612-4090-bfe8-15aacc1fb62b': {
        'name': 'Habu ID Graph Clean Room',
        'idgraph_type': 'habu'
    },
    '31c682e6-b3b4-42f3-8b1a-330ac69f85fd': {
        'name': 'Custom ID Graph Clean Room',
        'idgraph_type': 'custom',
        'idgraph_data_connection_id': '86843b18-a135-4c61-b80a-845870a714e0'
    }
}

DATA_CONNECTIONS = {
    '19ddf6c3-9287-4f7f-9bd1-5ac83c3ab32b': {
        'name': 'SHASTA.CLEAN_ROOM_EXAMPLE.USER_CRM_DATA_EMAIL',
        'identity_type': 'SHA256',
        'columns': [
            {
                'name': 'GENDER',
                'is_identity_column': False
            },
            {
                'name': 'AGE_RANGE',
                'is_identity_column': False
            },
            {
                'name': 'HOUSEHOLD_INCOME',
                'is_identity_column': False
            },
            {
                'name': 'PROFESSION',
                'is_identity_column': False
            },
            {
                'name': 'CUSTOMER_STATUS',
                'is_identity_column': False
            },
            {
                'name': 'EMAIL_SHA256',
                'is_identity_column': True
            }
        ]
    },
    # ID GRAPH DATA CONNECTION
    '86843b18-a135-4c61-b80a-845870a714e0': {
        'name': 'SHASTA.CLEAN_ROOM_EXAMPLE.ID_GRAPH',
        'parent_id_type': 'HOUSEHOLD_ID',
        'parent_id_column': 'S_HOUSEHOLD_ID',
        'identity_type_column': 'ID_TYPE',
        'identity_value_column': 'ID'
    }
}


def get_clean_room(clean_room_id):
    return CLEAN_ROOMS.get(clean_room_id, None)


def get_data_connection(data_connection_id):
    return DATA_CONNECTIONS.get(data_connection_id, None)


def get_data_connection_columns(data_connection_id):
    return DATA_CONNECTIONS.get(data_connection_id).get('columns', None)


def get_dataset_view_sql(clean_room_id, data_connection_id, dataset_columns: List[str]):
    sf_clean_room_id = clean_room_id.replace('-', '').upper()
    clean_room = get_clean_room(clean_room_id)
    data_connection = get_data_connection(data_connection_id)
    dc_name = data_connection.get('name', None) # DB.SCHEMA.TABLE or DB.SCHEMA.VIEW
    dc_obj_name = dc_name.split('.')[2] # The table or view name
    dc_identity_type = data_connection.get('identity_type', None)
    dc_identity_column = None
    dc_columns = get_data_connection_columns(data_connection_id)
    for column in dc_columns:
        if column.get('is_identity_column', False):
            dc_identity_column = column.get('name', None)
    if dc_name is None or dc_identity_type is None or dc_identity_column is None:
        # erroneous data connection setup => nothing to do
        return

    view_name = "HABU_CLEAN_ROOM_%s.CLEAN_ROOM.V_%s" % (sf_clean_room_id, dc_obj_name)
    view_columns = ', '.join(dataset_columns)

    id_graph_type = clean_room.get('idgraph_type', None)

    view_sql = None
    if id_graph_type is None or id_graph_type == 'habu':
        view_sql = """CREATE OR REPLACE SECURE VIEW %s AS SELECT '%s' AS CLEAN_ROOM_ID, %s, %s FROM %s""" % (view_name, clean_room_id, view_columns, dc_identity_column, dc_name)
    elif id_graph_type == 'custom':
        idgraph_data_connection_id = clean_room.get('idgraph_data_connection_id', None)
        if idgraph_data_connection_id is None:
            # erroneous data connection setup => custom id graph without id graph data connection id in clean room
            return
        idgraph_data_connection = get_data_connection(idgraph_data_connection_id)
        idgraph_dc_name = idgraph_data_connection.get('name', None)
        parent_id_type = idgraph_data_connection.get('parent_id_type', None)
        parent_id_column = idgraph_data_connection.get('parent_id_column', None)
        identity_type_column = idgraph_data_connection.get('identity_type_column', None)
        identity_value_column = idgraph_data_connection.get('identity_value_column', None)
        view_columns = ', '.join(['T1.%s' % col for col in dataset_columns])
        view_sql = """CREATE OR REPLACE SECURE VIEW %s AS 
        SELECT '%s' AS CLEAN_ROOM_ID, %s, T2.%s AS %s
        FROM %s, %s
        WHERE T1.%s = T2.%s AND T2.%s = '%s'
        """ % (view_name, clean_room_id, view_columns, parent_id_column, parent_id_column, dc_name, idgraph_dc_name,
               dc_identity_column, identity_value_column, identity_type_column, dc_identity_type)
    return view_sql


if __name__ == "__main__":
    habu_view_sql = get_dataset_view_sql(
        clean_room_id='80422c05-6612-4090-bfe8-15aacc1fb62b',
        data_connection_id='19ddf6c3-9287-4f7f-9bd1-5ac83c3ab32b',
        dataset_columns=['GENDER', 'AGE_RANGE']
    )
    print(habu_view_sql)

    custom_view_sql = get_dataset_view_sql(
        clean_room_id='31c682e6-b3b4-42f3-8b1a-330ac69f85fd',
        data_connection_id='19ddf6c3-9287-4f7f-9bd1-5ac83c3ab32b',
        dataset_columns=['GENDER', 'AGE_RANGE']
    )
    print(custom_view_sql)

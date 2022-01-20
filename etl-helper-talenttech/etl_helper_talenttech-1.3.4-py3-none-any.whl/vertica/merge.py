def vertica_merge(
        table_name,
        staging_table_name,
        conn,
        fields,
        key_fields,
        filter_merge_fields=None,
):
    """
    :param table_name:  main_table to update
    :param staging_table_name: temp table for using to update
    :param conn: sql alchemy connection
    :param filter_merge_fields:
    :param fields: fields needed to update
    :param key_fields: fields to join with temp table
    :return: Nothing
    """
    key_fields = key_fields or ["id"]
    merge_statement = """MERGE INTO {table_name} src
             USING {staging_table_name} tgt
                ON {join_key_fields}
             WHEN MATCHED {filter_merge_condition} THEN
             UPDATE SET {update_fields}
             WHEN NOT MATCHED THEN
             INSERT VALUES ({insert_fields})"""

    join_key_fields = " AND ".join(
        ['tgt."{field}"=src.{field}'.format(field=key) for key in key_fields]
    )

    update_fields = ",".join(
        ['"{field}"=tgt."{field}"'.format(field=field) for field in fields]
    )
    if filter_merge_fields is not None:
        filter_merge_condition = " AND " + " AND ".join(
            [
                'tgt."{field}" <> src."{field}".format(field=field)'.format(field=field)
                for field in filter_merge_fields
            ]
        )
    else:
        filter_merge_condition = ""

    insert_fields = ",".join(['tgt."{}"'.format(field) for field in fields])
    merge_statement = merge_statement.format(
        table_name=table_name,
        staging_table_name=staging_table_name,
        join_key_fields=join_key_fields,
        filter_merge_condition=filter_merge_condition,
        update_fields=update_fields,
        insert_fields=insert_fields,
    )
    conn.execute(merge_statement)
    return merge_statement

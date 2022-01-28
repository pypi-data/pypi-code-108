

def init(facebook, params):
    table_name = "%s.app_system_user" % facebook.config.get("schema_name")
    columns_name = ["id", "app_id_name", "app_secret_name", "access_token_name"]
    data = {
        "table_name": table_name,
        "columns_name": columns_name,
        "rows": [[params.get(c) for c in columns_name]]
    }
    facebook.transactional_dbstream.send_data(data,replace=False)

def insert_json_into_table(
        json,
        table_name,
        column_map,
        json_column_map,
        function_map=None,
        conflict_cols=None,
        update_cols=None
):
    [target_key] = {v.split(".")[0] for v in json_column_map.values()}

    return (
        f"""{_build_json_cte(json)}
        {_build_insert_statement(table_name, column_map, json_column_map)}
        {_build_select_statement(column_map, json_column_map, function_map or {})}
        FROM ({_build_json_array_subquery(target_key)})x {_build_on_conflict(conflict_cols, update_cols)}
"""
    )


def _build_json_cte(json):
    return f"WITH _json_cte AS (SELECT '{json}'::json AS _json)"


def _build_insert_statement(table, column_map, json_column_map):
    return f"INSERT INTO {table} ({', '.join(_get_column_order(column_map, json_column_map))})"


def _build_on_conflict(conflict_cols, update_cols):
    if conflict_cols and update_cols:
        sql = f"ON CONFLICT ({', '.join(conflict_cols)}) "
        update = f"DO UPDATE SET ({','.join(update_cols)}) = ({','.join(map(lambda x: 'excluded.' + x, update_cols))})"
        sql = sql + update
    elif conflict_cols:
        sql = "ON CONFLICT DO NOTHING"
    else:
        sql = ''

    return sql


def _build_json_array_subquery(target_key):
    return f"SELECT json_array_elements(_json->'{target_key}') AS _jsondict FROM _json_cte"


def _build_select_statement(column_map, json_column_map, function_map):
    lines = []

    for alias, definition in column_map.items():
        if alias in function_map:
            result = _apply_function(alias, definition, function_map)
            result = f"{result} AS {alias}"

        else:
            result = f"{definition} AS {alias}"

        lines.append(result)

    for alias, definition in json_column_map.items():
        result = _parse_json_line(alias, definition)

        if alias in function_map:
            result = _apply_function(alias, result, function_map)

        lines.append(result)

    return f"SELECT {', '.join(lines)}"


def _get_column_order(column_map, json_column_map):
    return [
        *column_map.keys(),
        *json_column_map.keys()
    ]


def _parse_json_line(k, v):
    parts = v.split('.')

    if len(parts) == 2:
        statement = f"_jsondict ->> '{parts[1]}' AS {k}"

    elif len(parts) == 3:
        statement = f"_jsondict -> '{parts[1]}' ->> '{parts[2]}' AS {k}"

    return statement


def _apply_function(k, statement, function_map):
    statement, alias = statement.split(' AS ')
    return f"{function_map[k].format(statement)} as {alias}"

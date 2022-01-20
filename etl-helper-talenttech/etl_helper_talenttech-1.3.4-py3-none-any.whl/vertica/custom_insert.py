import json


def myconverter(o):
    return o.__str__()


def write_list_as_json_str(fields_json, rows):
    if fields_json is not None:
        for r in rows:
            for field_json in fields_json:
                if r[field_json] is not None:
                    try:
                        r[field_json] = json.loads(r[field_json])
                    except TypeError:
                        continue
    return "\n".join([json.dumps(dict(r), default=myconverter, ensure_ascii=False) or "{}" for r in rows])


def vertica_insert(cursor, target, fields, fields_json, data):
    copy_statement = (
        u"COPY {0} ({1}) FROM STDIN PARSER FJSONPARSER( "
        u" RECORD_TERMINATOR=E'\n', flatten_maps=false) ENFORCELENGTH  ABORT ON ERROR"
    ).format(target, ",".join(['"' + v + '"' for v in fields]))
    data_str = write_list_as_json_str(fields_json, data)
    cursor.copy(copy_statement, data_str)
    cursor.close()


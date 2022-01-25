def get_table_ids(general_tables_dict, table_name, *args, **kwargs):
    """ Вернуть список из ID в таблице """
    table_ids = []
    for data_repr, data_info in general_tables_dict[table_name]:
        table_ids.append(data_info['id'])
    return table_ids


def get_table_info(general_tables_dict, tablename, *args, **kwargs):
    """ Получить информацию о таблице """
    return general_tables_dict[tablename]


def get_table_rerps(general_tables_dict, table_name, *args, **kwargs):
    """ Получить репрезентативные значения из таблицы """
    try:
        return list(general_tables_dict[table_name].keys())
    except KeyError:
        return []


def get_id_by_repr_table(general_tables_dict, table_name, repr, id_name='id', *args, **kwargs):
    """ Вернуть ID из таблицы table_name"""
    table_info = get_table_info(general_tables_dict, table_name)
    _id = get_id_by_repr(table_info, repr, id_name)
    return _id


def get_id_by_repr(table_info, repr, id_name='id', *args, **kwargs):
    """ Вернуть значение ключа ID строки из таблицы table_name из массива general_tables_dict, где значение ключа
     repr_name=repr.
     На примере - из таблицы вида table_info={'ТКО': {'cat_name': 'TKO', id=13}},
     где 'trash_cats' - table_name,
     'TKO' - repr (Представление, которое используется в графическом приложении, понятное юзеру),
     'cat_name' - repr_name, (в таблице users это username, например),
     13 - id (его и возвращаем), """
    try:
        table_details = table_info[repr]
        return table_details[id_name]
    except KeyError:
        pass


def get_repr_by_id_table(general_tables_dict, table_name, id_value, id_key='id'):
    """ Вернуть репрезантивное значение repr_value ключа repr_key таблицы table_name у которого id_key=id_value """
    table_info = get_table_info(general_tables_dict, table_name)
    repr_value = get_repr_by_id(table_info, id_value)
    return repr_value


def get_repr_by_id(table_info, id_value, id_key='id'):
    """ Вернть из table_info такой ключ repr_key, в значние которого (которое тоже представляет из себя словарь),
    присутствует такая пара id_key:_id_value_, где _id_value=id_value"""
    try:
        id_value = int(id_value)
    except: pass
    for rerp_key, table_details in table_info.items():
        if table_details[id_key] == id_value:
            return rerp_key


def get_trashtypes_by_trashcat_repr(general_tables_dict, trash_types_table_name,
                                    trash_cats_table_name, trash_cat_repr):
    """ Вернуть все trash_types_repr из trash_types_table где trash_cat=trash_cats_table[trash_cat_repr][id_name]"""
    trash_cat_id = get_id_by_repr_table(general_tables_dict, trash_cats_table_name, trash_cat_repr)
    trash_types_table_info = get_table_info(general_tables_dict, trash_types_table_name)
    trash_types_list = get_trashtypes_by_trashcat_id(trash_types_table_info, trash_cat_id)
    return trash_types_list


def get_trashtypes_by_trashcat_id(trash_types_dict, trash_cat_id, trash_cat_column_name='category', *args, **kwargs):
    """ Вернуть те виды груза, у которых в поле trash_cat указано значение, равное значению аргумента trash_cat """
    matched = []
    for type_name, type_info in trash_types_dict.items():
        if type_info[trash_cat_column_name] == trash_cat_id:
            matched.append(type_name)
    return matched

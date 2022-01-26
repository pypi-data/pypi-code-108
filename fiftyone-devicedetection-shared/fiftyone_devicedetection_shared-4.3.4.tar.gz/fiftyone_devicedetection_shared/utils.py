# Python 2 compatible dict merging
def merge_two_dicts(x, y):
    z = x.copy()   
    z.update(y)
    return z
    
def get_value_type(value):       
    if type(value) is bool:
        value_type = "bool"
    elif type(value) is int:
        value_type = "int"
    if type(value) is str:
        value_type = "string"
    elif type(value) is float:
        value_type = "double"
    elif isinstance(type(value), list) :
        value_type = "string[]"
    else:
        value_type = ""
    return value_type
    
def is_same_type(value, expected_type):
    valueType = get_value_type(value)
    valid = (valueType == expected_type)
    return valid
    
def get_properties_from_header_file(file_path):
    # Parse header file to get the list of properties
    with open(file_path) as f:
        header = f.readline() \
        .replace(" ", "") \
        .replace("\"", "") \
        .replace("\n", "") \
        .replace("\\", "")  \
        .replace("//", "")
    properties_list = header.split(",")
    return properties_list

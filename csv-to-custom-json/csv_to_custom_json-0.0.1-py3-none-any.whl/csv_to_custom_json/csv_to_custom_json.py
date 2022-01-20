""" csv_to_custom_json by n4n5 """
from csv import reader as CSVreader
from os.path import isfile
from json import dumps as JSONstringify

# pylint: disable=W0102
# -> dangerous arguments
# pylint: disable=C0103
# -> Function name "parseFile"

def parseFile(path_to_file="", schema=None, options_user={}):
    """Global function to parse a file"""
    def check_options(options_user, attr, default_value):
        """ Check options or put default value """
        if attr in options_user:
            return options_user[attr]
        return default_value
    options = {
        "arrayParse": check_options(options_user, "arrayParse", True),
        "callBackForce": check_options(options_user, "callBackForce", False),
        "debug": check_options(options_user, "debug", False),
        "error": check_options(options_user, "error", False),
        "lineCallBack": check_options(options_user, "lineCallBack", None),
        "parse": check_options(options_user, "parse", True),
        "separator": check_options(options_user, "separator", ","),
        "privateSeparator": check_options(options_user, "privateSeparator", "..."),
        "overrideFirstLine": check_options(options_user, "overrideFirstLine", False),
        "avoidVoidLine": check_options(options_user, "avoidVoidLine", False)
    }
    if options["debug"]:
        if isinstance(schema, (list, dict)) and schema is not None:
            print("HAS SCHEMA")
        else:
            print("NO SCHEMA")
            print("OPTIONS", JSONstringify(options))
        if options["error"] == "no":
            print("Useless informations : just use try catch if you don't want error :)")
    if isinstance(path_to_file, str):
        if not isfile(path_to_file):
            if options["error"] == "no":
                return []
            raise ValueError("Can't access to the file : '{}'".format(path_to_file))

    if isinstance(path_to_file, str):
        csv_file = open(path_to_file)
        line_reader = CSVreader(csv_file, delimiter=options["separator"])
    elif isinstance(path_to_file, list):
        line_reader = path_to_file

    def create_fields_binding(schema_object, first_line, start_path=""):
        """ Create fields bindings """
        bindings = []
        for index, value in enumerate(schema_object):
            is_list = isinstance(schema_object, list)
            is_dict = isinstance(schema_object, dict)
            if is_list:
                one_element = index
            elif is_dict:
                one_element = value
            if start_path == "":
                path = '{}'.format(one_element)
            else:
                path = '{}{}{}'.format(
                    start_path, options["privateSeparator"], one_element)
            if isinstance(schema_object[one_element], (dict, list)):
                if isinstance(schema_object[one_element], list):
                    bindings.append({
                        "name": one_element,
                        "path": path,
                        "type": "helper-array"
                    })
                bindings = bindings + create_fields_binding(schema_object[one_element], first_line, path)
            else:
                if is_list and options["arrayParse"] and schema_object[one_element] in first_line:
                    bindings.append({
                        "name": schema_object[one_element],
                        "path": path,
                        "value": "string"
                    })
                else:
                    if one_element in first_line or callable(schema_object[one_element]):
                        bindings.append({
                            "name": one_element,
                            "path": path,
                            "value": schema_object[one_element]
                        })
                    else:
                        bindings.append({
                            "name": one_element,
                            "path": path,
                            "type": "static",
                            "value": schema_object[one_element]
                        })
        return bindings

    def parse_line(line, rows, first_line):
        """" Parse one line """
        if isinstance(schema, list):
            obj = []
        else:
            obj = {}
        all_values = line
        for one_row in rows:
            one_path_row = one_row["path"]
            one_path_name = one_row["name"]
            all_path = one_path_row.split(options["privateSeparator"])
            current_value = None
            if ('type' not in one_row) or ('type' in one_row and one_row["type"] is None):
                if 'value' not in one_row:
                    schema_value = None
                else:
                    schema_value = one_row["value"]
                if one_row["name"] in first_line:
                    index = first_line.index(one_row["name"])
                else:
                    index = -1
                if index == -1:
                    current_value = schema_value
                else:
                    if index < len(all_values):
                        current_value = all_values[index]
                if options["parse"] and current_value is not None:
                    if schema_value == "int" and current_value != '':
                        current_value = int(current_value)
                    elif schema_value == "float":
                        current_value = float(current_value)
                    elif schema_value == "string":
                        current_value = str(current_value)
                    elif callable(schema_value):
                        if callable(current_value):
                            # When the value is in an array
                            current_value = schema_value(all_values)
                        else:
                            current_value = schema_value(current_value)
            elif ('type' in one_row and one_row["type"] == "helper-array"):
                current_value = []
            elif ('type' in one_row and one_row["type"] == "static"):
                current_value = one_row["value"]
            good_place = None
            if len(all_path) > 1:
                good_place = obj
                long = len(all_path)
                for count in range(0, long):
                    next_path = all_path[count]
                    if isinstance(good_place, list):
                        next_path_int = int(next_path)
                    if count == (long - 1):
                        if isinstance(good_place, dict):
                            good_place[next_path] = ""
                    else:
                        if (isinstance(good_place, list) and next_path_int not in good_place) or next_path not in good_place:
                            if isinstance(good_place, list):
                                if len(good_place) < (next_path_int+1):
                                    # len() returns 0 and the first index of the list is 0 !
                                    good_place.insert(next_path_int, {})
                            else:
                                good_place[next_path] = {}
                        if isinstance(good_place, list):
                            if next_path_int < len(good_place):
                                good_place = good_place[next_path_int]
                        else:
                            good_place = good_place[next_path]
                if isinstance(good_place, list):
                    good_place.append(current_value)
                elif isinstance(good_place, dict):
                    good_place[one_path_name] = current_value
                else:
                    good_place = current_value
            else:
                if isinstance(obj, list):
                    place = int(one_path_row)
                    obj.insert(place, current_value)
                elif isinstance(obj, dict):
                    obj[one_path_row] = current_value
        return obj

    def parse_first_line(first_line):
        """ Parse the first line """
        if schema is not None:
            # None is default value for schema
            cols = create_fields_binding(schema, first_line)
            if options["debug"]:
                print("BINDINGS:", JSONstringify(cols, default=lambda o: '<not serializable>'))
        else:
            def dupli(element):
                """" Duplicate the first line """
                return {
                    "name": element,
                    "path": element
                }
            cols = [dupli(x) for x in first_line]
        return cols

    def reader(line_reader):
        """" Read the file """
        final_json = []
        if isinstance(path_to_file, str):
            first_line = next(line_reader)
        elif isinstance(path_to_file, list):
            first_line = line_reader[0].split(options["separator"])
            line_reader = line_reader[1:]
        if isinstance(options["overrideFirstLine"], list):
            first_line = options["overrideFirstLine"]
        rows = parse_first_line(first_line)
        for one_line in line_reader:
            parsed_line = {}
            if isinstance(path_to_file, list):
                one_line = one_line.split(options["separator"])
            elif isinstance(path_to_file, str) and isinstance(one_line, list) and not one_line:
                one_line = [''] #create a fake void line
            if options["avoidVoidLine"]:
                if (isinstance(one_line, list) and not one_line) or (isinstance(one_line, list) and len(one_line) >= 1 and one_line[0] == "") or one_line == "" or one_line == "\n" or one_line == "\r\n":
                    continue
            parsed_line = parse_line(one_line, rows, first_line)
            if callable(options["lineCallBack"]):
                res_callback = options["lineCallBack"](parsed_line, one_line)
                if res_callback is None:
                    if options["callBackForce"]:
                        parsed_line = res_callback
                    else:
                        if options["debug"]:
                            print(
                                "CallBack force at False and callBack result is not correct")
                else:
                    parsed_line = res_callback
            final_json.append(parsed_line)
        return final_json
    converted = reader(line_reader)
    if isinstance(path_to_file, str):
        csv_file.close()
    return converted

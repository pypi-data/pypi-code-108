from __future__ import absolute_import
import yaml
from _pistar.utilities.function_tools import get_current_time_format
from _pistar.utilities.function_tools import camel_to_snake
from _pistar.utilities.constants import ENCODE
from _pistar.utilities.constants import FILE_MODE
from _pistar.utilities.constants import YAML_TYPE
from _pistar.utilities.constants import GENERATE_KEYS
from _pistar.terminal import console_output


class GenerateTestCase:
    next_index = None
    __type = None

    def __init__(self):
        self.next_index = -1
        self.__type = "type"

    def get_testcase_data_from_yaml(self, filename):
        with open(filename, FILE_MODE.READ, encoding=ENCODE.UTF8) as stream:
            try:
                api = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                console_output(exc)
                return None
        api_paths = api["paths"]
        tc_struct_data = {}
        host = api["host"]
        config_data = {"host_url": host}
        tc_struct_data["info"] = {}
        tc_struct_data["config_data"] = config_data
        tc_struct_data["testcases"] = {}

        for path in api_paths:
            path_content = api_paths[path]
            for method in path_content:
                method_content = path_content[method]
                source_operation_id = method_content["operationId"]
                operation_id = camel_to_snake(source_operation_id)
                tc_filename = f"autocase_{operation_id}"

                cur_method_reference = {}
                if "consumes" in method_content:
                    cur_method_reference["common_header"] = {}
                    cur_method_reference["common_header"]["consume"] = method_content["consumes"][0]

                cur_method_reference["createRecord"] = f"{get_current_time_format()} auto generate"
                cur_method_reference["className"] = \
                    f"Autocase{source_operation_id[:1].upper()}{source_operation_id[1:]}"
                cur_method_reference["description"] = method_content["summary"]
                if "tags" in method_content:
                    tags = method_content["tags"]
                else:
                    tags = ["default"]
                filename = api["info"]["title"] + tags[0]
                filename = camel_to_snake(filename)
                cur_method_reference["awFilename"] = filename
                cur_method_reference["awMethodName"] = operation_id

                if method_content["parameters"]:
                    self.parse_parameter_type_to_python_type(cur_method_reference, method_content["parameters"], api)
                tc_struct_data["testcases"][tc_filename] = cur_method_reference
        return tc_struct_data

    def parse_parameter_type_to_python_type(self, method_reference, parameters, api):
        for parameter in parameters:
            if parameter["in"] == "body":
                # Only one body is allowed in parameters
                if "body" not in method_reference:
                    self.next_index = -1
                    self.insert_python_body_data(method_reference, parameter, api)
            else:
                self.add_param_in_struct_data(method_reference, parameter)

    def insert_python_body_data(self, method_reference, parameter, api):
        method_reference["body"] = []
        method_reference["body"].append(parameter["name"])
        method_reference["body"].append(self.get_body_type(parameter))
        method_reference["body"].append("request_body_object0")
        body_struct_data = self.get_body_struct_data(parameter, api)
        body_python_data = self.construct_python_body_data("", body_struct_data, -1, True)
        method_reference["body"].append(body_python_data)

    def get_body_type(self, parameter):
        # get body type，if have $ref, the type is object
        if "schema" in parameter:
            schema = parameter["schema"]
            if "$ref" in schema:
                return "object"
            else:
                return YAML_TYPE.COMPLEX_TYPE_TO_PYTHON[schema[self.__type]]
        else:
            return YAML_TYPE.COMPLEX_TYPE_TO_PYTHON[parameter[self.__type]]

    def get_body_struct_data(self, item, api):
        json_content = {}
        param_name = item["name"]
        if "schema" in item:
            self.__get_body_data_with_schema(item, json_content, api)
        elif item["type"] == "array":
            json_content[param_name] = [item["items"]["type"]]
        else:
            # if schema not in item and item type is not array, the type is base type
            json_content[param_name] = item["type"]
        return json_content

    def __get_body_data_with_schema(self, item, json_content, api):
        param_name = item["name"]
        schema = item["schema"]
        param_type = ""
        if "type" in schema:
            param_type = schema["type"]
        # if schema has $ref, the json need to be recursively constructed
        if "$ref" in schema:
            reference = schema["$ref"]
            ref_map = {}
            json_content[param_name] = ref_map \
                if self.construct_reference_json_object(api["definitions"],
                                                        ref_map,
                                                        reference[GENERATE_KEYS.DEFINITION:]) \
                else "object"
        elif param_type == "array":
            # if param_type is array, the array items also may be ref
            json_content[param_name] = self.__get_body_array_type(schema, api)
        else:
            # the param_type is base type
            json_content[param_name] = param_type

    def __get_body_array_type(self, schema, api):
        param_array = []
        items_instance = schema["items"]
        # if array has reference, save reference in array
        if "$ref" in items_instance:
            array_ref = items_instance["$ref"]
            ref_array_map = {}
            ref_array_map = ref_array_map \
                if self.construct_reference_json_object(api["definitions"],
                                                        ref_array_map,
                                                        array_ref[GENERATE_KEYS.DEFINITION:]) \
                else "object"
            param_array.append(ref_array_map)
        else:
            # save base type
            param_array.append(items_instance["type"])
        return param_array

    def add_param_in_struct_data(self, reference, parameter):
        param_name = parameter["in"] + "_params"
        if param_name not in reference:
            reference[param_name] = {}
        reference[param_name][parameter["name"]] = {}
        reference[param_name][parameter["name"]]["name"] = "request_" + parameter["in"] + "_" + parameter["name"]
        reference[param_name][parameter["name"]]["type"] = YAML_TYPE.COMPLEX_TYPE_TO_PYTHON[parameter[self.__type]]
        # if parameter type is array, need to get the array item type
        if parameter["type"] == "array":
            reference[param_name][parameter["name"]]["subValue"] = \
                YAML_TYPE.YAML_TYPE_VALUE[parameter["items"][self.__type]]
        else:
            reference[param_name][parameter["name"]]["value"] = YAML_TYPE.YAML_TYPE_VALUE[parameter[self.__type]]

    def construct_reference_json_object(self, reference_api, ref_map, ref_name):
        ref_object = reference_api[ref_name]
        if "properties" not in ref_object:
            return False
        properties = ref_object["properties"]
        for prop_key in properties:
            prop_type = ""
            if "type" in properties[prop_key]:
                prop_type = properties[prop_key]["type"]
            if "$ref" in properties[prop_key]:
                ref = properties[prop_key]["$ref"]
                ref_prop_map = {}
                ref_prop_map = ref_prop_map \
                    if self.construct_reference_json_object(reference_api,
                                                            ref_prop_map,
                                                            ref[GENERATE_KEYS.DEFINITION:]) \
                    else "object"
                ref_map[prop_key] = ref_prop_map
            elif prop_type == "array":
                items_instance = properties[prop_key]["items"]
                ref_map[prop_key] = self.__construct_ref_array_type(items_instance, reference_api)
            else:
                ref_map[prop_key] = prop_type
        return True

    def __construct_ref_array_type(self, item, api):
        prop_ref_array = []
        # if array has reference, save reference in array
        if "$ref" in item:
            array_ref = item["$ref"]
            ref_array_map = {}
            ref_array_map = ref_array_map \
                if self.construct_reference_json_object(api,
                                                        ref_array_map,
                                                        array_ref[GENERATE_KEYS.DEFINITION:]) \
                else "object"
            prop_ref_array.append(ref_array_map)
        else:
            # save base type
            prop_ref_array.append(item["type"])
        return prop_ref_array

    def construct_python_body_data(self, result, body_data, object_index, object_flag):
        # check body_data is array or object
        if not object_flag:
            result = self.__construct_array_content(result, body_data, object_index)
        else:
            result = self.__construct_object_content(result, body_data, object_index)
        return result

    def __construct_array_content(self, result, body_data, object_index):
        body_str = format("%27s" % "request_body_object")
        if isinstance(body_data[0], dict):
            self.next_index += 1
            cur_index = self.next_index
            result = result + body_str + str(self.next_index) + " = {}\n"
            result = self.construct_python_body_data(result, body_data[0], self.next_index, True)
            result = result + body_str + str(object_index) + ".append(request_body_object" + str(cur_index) + ")\n"
        elif isinstance(body_data[0], list):
            self.next_index += 1
            cur_index = self.next_index
            result = result + body_str + str(self.next_index) + " = []\n"
            result = self.construct_python_body_data(result, body_data[0], self.next_index, False)
            result = result + body_str + str(object_index) + ".append(request_body_object" + str(cur_index) + ")\n"
        else:
            result = result + body_str + str(object_index) + ".append(" + \
                     str(YAML_TYPE.YAML_TYPE_VALUE[body_data[0]]) + ")\n"
        return result

    def __construct_object_content(self, result, body_data, object_index):
        body_str = format("%27s" % "request_body_object")
        for item in body_data.items():
            if isinstance(item[1], dict):
                self.next_index += 1
                cur_index = self.next_index
                result = result + body_str + str(self.next_index) + " = {}\n"
                result = self.construct_python_body_data(result, item[1], self.next_index, True)
                if object_index != -1:
                    result = result + body_str + str(object_index) + "[\"" + item[0] + \
                             "\"] = request_body_object" + str(cur_index) + "\n"
            elif isinstance(item[1], list):
                self.next_index += 1
                cur_index = self.next_index
                result = result + body_str + str(self.next_index) + " = []\n"
                result = self.construct_python_body_data(result, item[1], self.next_index, False)
                if object_index != -1:
                    result = result + body_str + str(object_index) + "[\"" + item[0] + \
                             "\"] = request_body_object" + str(cur_index) + "\n"
            elif object_index == -1:
                result = result + "        request_body_object0 = " + str(YAML_TYPE.YAML_TYPE_VALUE[item[1]]) + "\n"
            else:
                result = result + body_str + str(object_index) + "[\"" + item[0] + \
                         "\"] = " + str(YAML_TYPE.YAML_TYPE_VALUE[item[1]]) + "\n"
        return result

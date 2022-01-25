import yaml

from _pistar.terminal import console_output
from _pistar.utilities.function_tools import get_current_time_format
from _pistar.utilities.function_tools import camel_to_snake
from _pistar.utilities.constants import ENCODE
from _pistar.utilities.constants import FILE_MODE
from _pistar.utilities.constants import YAML_TYPE


class GenerateAw:
    __query_key = None
    __header_key = None
    __path_key = None
    __body_key = None

    def __init__(self):
        self.__query_key = "query_params"
        self.__header_key = "header_params"
        self.__path_key = "path_params"
        self.__body_key = "body"

    def get_swagger_aw_data(self, filename):
        with open(filename, FILE_MODE.READ, encoding=ENCODE.UTF8) as stream:
            try:
                api = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                console_output(exc)
                return None
        api_paths = api["paths"]
        aw_struct_data = {"info": {}, "awTags": {}}
        aw_struct_data["info"]["title"] = api["info"]["title"]
        base_path = "" if api["basePath"] == "/" else api["basePath"]
        #  get request protocol, http protocol is preferred
        protocol = "http"
        if "schemes" in api:
            schemes = api["schemes"]
            if protocol not in schemes:
                protocol = schemes[0]

        for path_name in api_paths:
            path_content = api["paths"][path_name]
            # every path have many method, get method from path
            for method in path_content:
                method_content = path_content[method]
                cur_method_reference = {}
                # use tags to split aw in different files
                if "tags" in method_content:
                    tags = method_content["tags"]
                else:
                    tags = ["default"]
                cur_method_reference["createRecord"] = f"{get_current_time_format()} auto generate"
                cur_method_reference["method"] = method
                cur_method_reference["protocol"] = protocol
                cur_method_reference["getPath"] = base_path + path_name
                cur_method_reference["operationId"] = camel_to_snake(method_content["operationId"])
                # read parameters, put the parameters into the proper struct
                if method_content["parameters"]:
                    self.__parse_parameter_type_python_type(cur_method_reference, method_content["parameters"])
                tag_references = aw_struct_data["awTags"].get(tags[0], [])
                tag_references.append(cur_method_reference)
                aw_struct_data["awTags"][tags[0]] = tag_references
        return aw_struct_data

    def __parse_parameter_type_python_type(self, method_reference, parameters):
        for parameter in parameters:
            if parameter["in"] == "query":
                query_params = method_reference.get(self.__query_key, {})
                query_params[parameter["name"]] = \
                    YAML_TYPE.COMPLEX_TYPE_TO_PYTHON[parameter.get("type", "string")]
                method_reference[self.__query_key] = query_params
            elif parameter["in"] == "path":
                path_params = method_reference.get(self.__path_key, {})
                path_params[parameter["name"]] = \
                    YAML_TYPE.SIMPLE_TYPE_TO_PYTHON[parameter.get("type", "string")]
                method_reference[self.__path_key] = path_params
            elif parameter["in"] == "header":
                header_params = method_reference.get(self.__header_key, {})
                header_params[parameter["name"]] = \
                    YAML_TYPE.SIMPLE_TYPE_TO_PYTHON[parameter.get("type", "string")]
                method_reference[self.__header_key] = header_params
            else:
                body_params = method_reference.get(self.__body_key, [])
                body_params.append(parameter["name"])
                body_params.append("str")
                method_reference[self.__body_key] = body_params

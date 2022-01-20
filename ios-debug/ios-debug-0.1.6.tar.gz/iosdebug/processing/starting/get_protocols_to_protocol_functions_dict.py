import re
from collections import namedtuple


def get_protocols_to_protocol_functions_dict(repository_protocols, path_to_content_map):
    Function = namedtuple(
        "Function", "declaration, name, generic_parameter_clause, params, return_type"
    )

    protocol_to_protocol_functions = {}
    for protocol in repository_protocols:
        for path in path_to_content_map:
            if "protocol " + protocol in path_to_content_map[path]:
                content = path_to_content_map[path]
                function_instances = []
                protocol_definition = re.findall(
                    "protocol " + protocol + r".* {([\s\S]*?)\n}", content
                )[0]
                protocol_definition_lines = [
                    line
                    for line in protocol_definition.split("\n")
                    if "//" not in line
                    and "var" not in line
                    and "typealias" not in line
                ]
                protocol_definition = "\n".join(protocol_definition_lines)
                functions = protocol_definition.split("func ")
                functions = [
                    func
                    for func in functions
                    if "typealias " not in func
                    and "var " not in func
                    and "MARK" not in func
                ]
                functions = [function.strip() for function in functions]
                functions = [function for function in functions if function]
                functions = [function.replace("\n", "") for function in functions]
                functions = [" ".join(function.split()) for function in functions]
                print("- " * 40)
                print("Found functions for protocol", protocol + ":")
                print()

                for func in functions:
                    function_name = re.findall(r"(\w+)", func)[0]
                    generic_parameter_clause_match = re.findall(
                        r"<.*>", func.split("(")[0]
                    )
                    if generic_parameter_clause_match:
                        generic_parameter_clause = generic_parameter_clause_match[0]
                    else:
                        generic_parameter_clause = None

                    params_part = func.replace(function_name, "", 1)
                    if "->" in func:
                        params_part = params_part.split("->")[0]
                    params_part = re.findall(r"\((.*)\)", params_part)[0]
                    if generic_parameter_clause:
                        params_part = params_part.replace(generic_parameter_clause, "")

                    params = params_part.split(", ")
                    for index, param in enumerate(params):
                        if "(" in param and not ")" in param:
                            params[index] = params[index] + ", " + params[index + 1]
                            del params[index + 1]
                    return_type = re.findall(r"-> (.*)", func)
                    if params[0] == "" or params[0] == "()":
                        params = None
                    if return_type:
                        return_type = return_type[0]
                    else:
                        return_type = None

                    print("func", func)
                    print("- name:", function_name)
                    print("- generic parameter clause:", generic_parameter_clause)
                    print("- params:", params)
                    print("- return type:", return_type)
                    function_instances.append(
                        Function(
                            func,
                            function_name,
                            generic_parameter_clause,
                            params,
                            return_type,
                        )
                    )
                    print()
                print("- " * 40)
                protocol_to_protocol_functions[protocol] = function_instances
                print()
    return protocol_to_protocol_functions

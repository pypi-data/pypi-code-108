import re
from pprint import pprint
from collections import defaultdict


def get_mock_functions_variants(protocol_to_mocked_contents):
    result = {}
    for entity in protocol_to_mocked_contents:
        result[entity] = defaultdict(str)
        mocked_content = protocol_to_mocked_contents[entity]
        mocked_extension = re.findall("extension [\s\S]+?\n}", mocked_content)[0]
        functions_split = mocked_extension.split("func ")[1:]
        for function in functions_split:
            function_name = re.findall("([\s\S]+?) {", function)[0]
            cases = re.findall("case (.*\"):", function)
            result[entity][function_name] = cases
    return result

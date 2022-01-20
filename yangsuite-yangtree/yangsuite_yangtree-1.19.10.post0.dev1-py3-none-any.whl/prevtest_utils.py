# Copyright 2016 Cisco Systems, Inc
import os
import sys
import argparse
import json
import yaml
from jinja2 import Environment
from copy import deepcopy


def resolve_format_json(d, dcopy):
    for k, v in d.items():
        if type(v) is dict:
            d[k] = resolve_format_json(v, dcopy)
        else:
            if type(v) is str and '{' in v:
                temp = v.replace("\'", "\"")
                d[k] = json.loads(temp)
            else:
                d[k] = v

    return d


class PreConfigExtract:

    def __init__(self, test_file_path):
        if not os.path.isfile(test_file_path):
            raise

        self.test_file_path = test_file_path
        self.dir_path = os.path.dirname(test_file_path)
        self.env = Environment(
            variable_start_string='%{',
            variable_end_string='}'
        )

    def read_yaml(self, file_path):
        with open(file_path) as fp:
            stream = fp.read()
            data = yaml.full_load(stream)

            return stream, data

    def process(self):
        with open(self.test_file_path) as fp:
            line1 = fp.readline()

        data_file = line1.split(":")[1].strip()
        data_file_path = os.path.join(self.dir_path, data_file)

        if not os.path.isfile(data_file_path):
            raise OSError('Invalid data file: {0}'.format(str(data_file_path)))

        stream, data = self.read_yaml(data_file_path)

        preresolvedStream = self.env.from_string(stream).render(data)
        preresolvedStream = preresolvedStream.replace("'{", "{")
        preresolvedStream = preresolvedStream.replace("}'", "}")

        preresolvedData = yaml.full_load(preresolvedStream)
        resolvedData = resolve_format_json(
            preresolvedData.copy(),
            deepcopy(preresolvedData)
        )

        yang_content = resolvedData['data']['yang']['content']

        preconfig = {}
        for key in yang_content.keys():
            node = yang_content[key]['nodes'][0]
            xpath = node['xpath']
            value = node['value']
            preconfig[xpath] = value

        return preconfig


def main(argv):
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-pt", "--previous-tests", required=True,
        help="Path for previousely generated Test File"
    )

    args = parser.parse_args(argv)
    prev_test_file = args.previous_tests
    print("Resolving previous test file:", prev_test_file)

    obj = PreConfigExtract(prev_test_file)
    preconfig = obj.process()
    print(preconfig)


if __name__ == '__main__':
    main(sys.argv[1:])

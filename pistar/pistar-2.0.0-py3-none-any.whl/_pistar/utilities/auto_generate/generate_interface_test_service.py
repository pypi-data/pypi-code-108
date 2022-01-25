import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from _pistar.utilities.constants import ENCODE
from _pistar.utilities.constants import FILE_MODE
from _pistar.utilities.function_tools import camel_to_snake
from _pistar.terminal import console_output
from .aw_code_generate_service import GenerateAw
from .testcase_generate_service import GenerateTestCase


class GenerateInterfaceTest:
    output_path = None
    config_folder = "pistar/restapitest/config"
    aw_folder = "pistar/restapitest/aw"
    testcase_folder = "pistar/restapitest/testcase"

    def __init__(self, output_path):
        self.output_path = Path(output_path)
        if not self.output_path.exists():
            self.output_path.mkdir(parents=True)
        self.__template_folder = Path(__file__).parent.joinpath("template/interface")
        self.env = Environment(loader=FileSystemLoader(searchpath=self.__template_folder))

    def generate_test_case(self, filename):
        gene = GenerateTestCase()
        struct_data = gene.get_testcase_data_from_yaml(filename)
        if not struct_data:
            console_output("Failed to generate test case.")
            return None
        global_json_path = self.output_path.joinpath(self.config_folder, "global.json")
        write_json_file(global_json_path, struct_data["config_data"])

        config_util_path = self.output_path.joinpath(self.config_folder, "config_util.py")
        template = self.env.get_template("config_util.py.txt")
        output = template.render()
        write_file(config_util_path, output)

        template = self.env.get_template("testcase.py.txt")
        for test_case_name in struct_data["testcases"]:
            output = template.render({"testcase": struct_data["testcases"][test_case_name]})
            filename = f"{test_case_name}.py"
            cur_file_path = self.output_path.joinpath(self.testcase_folder, filename)
            write_file(cur_file_path, output)
            console_output(f"create test case {cur_file_path} success")

    def generate_aw(self, filename):
        template = self.env.get_template("aw.py.txt")
        gene = GenerateAw()
        # generate the aw struct data
        struct_data = gene.get_swagger_aw_data(filename)
        if not struct_data:
            console_output("Failed to generate aw.")
            return None
        for tag in struct_data["awTags"]:
            py_name = struct_data["info"]["title"] + tag
            py_name = f"{camel_to_snake(py_name)}.py"
            file_name = self.output_path.joinpath(self.aw_folder, py_name)
            output = template.render({"tagData": struct_data["awTags"][tag]})
            write_file(file_name, output)
            console_output(f"create aw {filename} file success")


def write_file(file_path, content):
    file_directory = Path(file_path).parent
    if not file_directory.exists():
        file_directory.mkdir(parents=True)
    with open(file_path, FILE_MODE.WRITE, encoding=ENCODE.UTF8) as out:
        out.write(content)


def write_json_file(file_path, content):
    file_directory = Path(file_path).parent
    if not file_directory.exists():
        file_directory.mkdir(parents=True)
    with open(file_path, FILE_MODE.WRITE, encoding=ENCODE.UTF8) as out:
        json.dump(content, out)

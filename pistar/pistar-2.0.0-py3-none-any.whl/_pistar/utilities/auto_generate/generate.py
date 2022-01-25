from pathlib import Path
from _pistar.utilities.auto_generate import GenerateInterfaceTest
from _pistar.terminal import console_output


def generate_file(arguments):
    swagger_path = Path(arguments.interface)
    if not swagger_path.exists():
        console_output('The input file is non-existent, please check.')
        return
    swagger_abspath = str(swagger_path.resolve())
    output_path = arguments.output
    gene = GenerateInterfaceTest(output_path)
    gene.generate_aw(swagger_abspath)
    gene.generate_test_case(swagger_abspath)

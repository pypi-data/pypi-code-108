from glob import glob
import os
import re
from colorama import Fore
from ..process import run_process, run_process_interactive, TimeoutError, ExitCodeError
from .. import utils
from .base_judge import BaseJudge

class JavaJudge(BaseJudge):
    def __init__(self, base_dir, tests, args, src="src", out="out"):
        super().__init__(base_dir, tests, args)

        # Compilation folder (.class)
        self.out = out
        # Source folder (.java)
        self.src = src
        self.out_dir = f"{base_dir}/{self.out}"
        self.src_dir = f"{base_dir}/{self.src}"

        # If not specified, will read from root (src_dir)
        self.package = tests.get("package", "")
        self.package = "/".join(self.package.split("."))

        # Create out_dir if not exists
        if not os.path.isdir(self.out_dir):
            os.makedirs(self.out_dir, exist_ok=True)

        self.load_info_from_folder(f"testcases/java/files")


    def load_info_from_folder(self, folder_dir):
        for exercise in self.exercises:
            name = exercise.get("name")
            if not name:
                print(f"{Fore.RED}Error! No s'ha especificat la clau \"name\" en algun exercici.{Fore.RESET}")
                exit(1)

            exercise_dir = f"{folder_dir}/{name}"
            exercise.setdefault("tests",[]).extend(
                    self.load_folder_tests(exercise_dir))
        # utils.prettify_dict(self.exercises)


    # Load tests from a specific folder
    def load_folder_tests(self, folder_dir):
        # print(folder_dir)
        tests_path = folder_dir + "/tests"
        tests = []
        if os.path.isdir(tests_path):
            filenames = dict()
            for name in os.listdir(tests_path):
                name, ext = os.path.splitext(name)
                filenames.setdefault(name,[]).append(ext)

            for name, exts in filenames.items():
                file_path = "{}/{}".format(tests_path, name)
                test = {"name": name}

                for ext in exts:
                    test_path = "{}{}".format(file_path, ext)
                    # print(test_path)
                    if os.path.isfile(test_path):
                        data = utils.load_file(test_path)
                        if ext == ".in":
                            test["input"] = data
                        elif ext == ".out":
                            test["output"] = data

                tests.append(test)

        return tests


    def judge(self, interactive=False):
        for exercise in self.exercises:
            self.judge_exercise(exercise, interactive)

        # Remove out/ folder
        remove_command = (
                f"docker run --rm -v {os.getcwd()}/{self.base_dir}:/app"
                f" -w /app -i openjdk:12 rm -r out/"
        )
        out = utils.run_or_exit(run_process, remove_command,
                err=f"Error cleaning {self.out} directory").stdout

    def build(self, name, java_package):
        # Build
        compile_command = (
                f"docker run --rm -v {os.getcwd()}/{self.base_dir}:/app"
                f" -w /app -i openjdk:12 javac -verbose"
                f" -cp {self.out}/ -sourcepath {self.src}/"
                f" -d {self.out}/ {self.src}/{java_package}.java"
        )
        # print(compile_command)

        out = run_process(compile_command).stderr

        # Look for sources in compile output and print them
        matches = re.findall(r"out/([^$\n]*)\.class", out)
        # print(out)
        # print(matches)

        sources = []
        for source in matches:
            source_file = f"{self.base_dir}/src/{source}.java"
            # print(source_file)
            sources.append(source_file)
        return sources


    def print_test(self, name, test_input, expected_output, output, status=None):
        colored_output, colored_expected_output, status = utils.colored_diff(output, expected_output, status)
        print("- test: {}".format(name))
        if len(test_input) > 0:
            print("  input:")
            for line in test_input.splitlines():
                print(Fore.CYAN + "    {}".format(line) + Fore.RESET)
        utils.column_print(colored_expected_output, colored_output, "expected_output:", "output:")
        print("- status: {}".format(status))


    def run_test(self, test, run_command):
        expected_output = test["output"]
        expected_output += '\n'
        test_input = test["input"]
        output = ""
        status = None
        try:
            output = run_process(run_command, stdin=test_input, timeout=5).stdout
            if len(output) == 0:
                status = "EMPTY"
        except TimeoutError:
            status = "TIMEOUT"
        except Exception:
            status = "RUNTIME"
        # output = run_process(run_command, stdin=test_input).stdout
        self.print_test(test["name"], test_input, expected_output, output, status)


    def run_exercise(self, exercise, java_package, interactive):
        # Volumes
        volumes_options = " ".join([f"-v {os.getcwd()}/{self.base_dir}/{volume}:/app/{volume}" for volume in self.volumes])
        run_command = f"docker run --rm -v {os.getcwd()}/{self.out_dir}:/app {volumes_options} -w /app -i openjdk:12 java {java_package}"
        # print(run_command)

        if interactive:
            print("Interactive mode")
            print("input:")
            print(f"{50 * '━'}")
            run_process_interactive(run_command)
        else:
            for test in exercise.get("tests", []):
                self.run_test(test, run_command)


    def print_source(self, source_content):
        utils.line_number_print(utils.highlight(source_content, "java"))

    def judge_exercise(self, exercise, interactive):
        name = exercise.get("name")

        # If the exercise is located in a subpackage inside self.package
        subpackage = exercise.get("subpackage", "")
        subpackage = "/".join([subpackage, name])
        source_path = f"{self.src_dir}/**/{self.package}/{subpackage}.java"

        print("=" * 20)
        print(name)
        print(source_path)
        print("=" * 20)

        source_file = next(iter(glob(source_path, recursive=True)), None)
        if not source_file:
            print(f"{Fore.RED}{name}: Not found{Fore.RESET}")
            return

        java_package = source_file.split(f"{self.src}/")[1].replace(".java", "")
        try:
            sources = self.build(name, java_package)
        except ExitCodeError:
            print(f"{Fore.RED}Error compiling: {name}.java {Fore.RESET}")
            return

        # print(sources)
        # Print sources
        for source in sources:
            print(source)
            with open(source) as f:
                self.print_source(f.read())
            print()
        self.run_exercise(exercise, java_package, interactive)



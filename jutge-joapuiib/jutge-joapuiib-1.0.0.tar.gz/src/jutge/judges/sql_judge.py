from glob import glob
import os
import re
from colorama import Fore
import time
import sys
import traceback
from .base_judge import BaseJudge
from ..status import Status
from ..process import run_process, run_process_interactive, TimeoutError, ExitCodeError
from .. import utils

class SQLJudge(BaseJudge):
    def __init__(self, base_dir, tests, args):
        super().__init__(base_dir, tests, args)

        # If not specified, will read from root (base_dir)
        self.package = tests.get("package", "")
        self.package = "/".join(self.package.split("."))

        # Docker image
        self.image = "mariadb:latest"

        # SQL docker container
        self.container = "sql_judge"

        self.user = "root"
        self.password = "1234"

        self.init_scripts = tests.get("init", [])
        self.post_scripts = tests.get("post", [])

        self.result = {}
        self.result["exercises"] = []

        self.light = args.light

        self.load_info_from_folder()


    def stop_database(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print(f"{Fore.RED}Error:{Fore.RESET}")
                print(e)
                print(traceback.format_exc())
                # self.delete_container()

        return wrapper


    def load_info_from_folder(self):
        pass


    def judge(self, interactive=False):
        if len(self.exercises) > 0:
            self.init_container()

            utils.run_or_exit(self.run_init_scripts,
                out=f"Running init scirpts...",
                err=f"Error running init scripts")

            # print(f"Interactive: {interactive}")
            for exercise in self.exercises:
                result_exercise = self.judge_exercise(exercise, interactive)
                self.result["exercises"].append(result_exercise)

            utils.run_or_exit(self.run_post_scripts,
                out=f"Running post scirpts...",
                err=f"Error running post scripts")

            return self.result

    def init_container(self):
        if not self.get_cointainer_id():
            self.delete_container()
            self.start_container()
        self.wait_until_container_healthy()


    def start_container(self):
        command = (f"docker run -d --name {self.container}"
                   # f" -e LANG=en_US.utf8"
                   f" -e MYSQL_ROOT_PASSWORD={self.password}"
                   f" --health-cmd=\'mysql -u{self.user} -p{self.password}\' --health-interval=2s"
                   f" {self.image}"
        )
        out = utils.run_or_exit(run_process, command,
                out=f"Init {self.image} {self.container} container...",
                err=f"Error initializing {self.image} container").stdout

    def get_cointainer_id(self):
        command = f"docker ps -q -f name={self.container}"
        container_id = run_process(command).stdout.strip()
        return container_id


    def wait_until_container_healthy(self):
        command = (f"docker inspect -f {{{{.State.Health.Status}}}} {self.container}")

        def wait_until_healthy():
            out = run_process(command).stdout.strip()
            while not out == "healthy":
                time.sleep(2)
                out = run_process(command).stdout.strip()
                print(out[0], end="", flush=True)

        utils.run_or_exit(wait_until_healthy,
            out=f"Waiting until {self.container} is ready... ",
            err=f"Error checking {self.container} is ready.")

    def delete_container(self):
        command = f"docker ps -q -f status=exited -f name={self.container}"
        container_id = run_process(command).stdout.strip()
        if container_id:
            command = f"docker rm -f {self.container}"
            out = utils.run_or_exit(run_process, command,
                    out=f"Removing {self.image} {self.container} container...",
                    err=f"Error removing {self.image} container").stdout


    def run_init_scripts(self):
        for init_script in self.init_scripts:
            self.run_query(init_script, timeout=10)
    def run_post_scripts(self):
        for post_script in self.post_scripts:
            self.run_query(post_script, timeout=10)


    def run_query(self, query, force=False, timeout=2):
        args = "-t --default-character-set=utf8"
        if force:
            args += " -f"

        command = (f"docker exec -i {self.container}"
                   f" mysql -B -u{self.user} -p{self.password} {args}"
        )
        # print(query)
        return run_process(command, stdin=query, timeout=timeout)


    def run_interactive(self):
        command = (f"docker exec -it {self.container}"
                   f" mysql -u{self.user} -p{self.password} --silent -t --default-character-set=utf8"
        )
        run_process_interactive(command)


    @stop_database
    def judge_exercise(self, exercise, interactive):
        name = exercise.get("name")
        if not name:
            print(f"{Fore.RED}Error! No s'ha especificat la clau \"name\" en algun exercici.{Fore.RESET}")
            raise Exception("No class name specified")

        result_exercise = {}
        result_exercise["name"] = name

        # If the exercise is located in a subpackage inside self.package
        subpackage = exercise.get("subpackage", "")
        subpackage = "/".join([subpackage, name])
        source_path = re.sub(r"/+", "/", f"{self.base_dir}/{self.package}/{subpackage}.sql")

        print("=" * 20)
        print(name)
        print(source_path)

        source_file = next(iter(glob(source_path, recursive=True)), None)
        if not source_file:
            print(f"{Fore.RED}{name}: Not found{Fore.RESET}")
            result_exercise["found"] = False
            result_exercise["source_file"] = source_path
            print(f"{Fore.RED}Error! No script found{Fore.RESET}")
            return result_exercise

        result_exercise["found"] = True
        result_exercise["source_file"] = source_file

        # Print sources
        with open(source_file) as f:
            source = f.read()
            result_exercise["source"] = source
            self.print_source(source)
            result = self.run_exercise(exercise, source, interactive)
            result_exercise = {**result_exercise, **result}
        print()
        return result_exercise


    def run_exercise(self, exercise, source, interactive):
        result_exercise = {}
        name = exercise.get("name")
        expected_output = exercise.get("output", "").strip()
        expected_stderr = exercise.get("stderr", "").strip()
        force = exercise.get("force", False)
        post = exercise.get("post", [])

        output = ""
        stderr = ""
        status = Status.PERFECT

        if not source.strip():
            status = Status.EMPTY
            print(f"  - status: {status}")
            result_exercise["status"] = status.name
            return result_exercise

        try:
            result_query = self.run_query(source, force=force)
            output = result_query.stdout.strip()
            stderr = re.sub(r" at line \d+", "", result_query.stderr.strip())
        except TimeoutError:
            status = Status.TIMEOUT
            print(f"  - status: {status}")
            result_exercise["status"] = status.name
            return result_exercise
        except ExitCodeError as e:
            stderr = re.sub(r" at line \d+", "", e.stderr).strip()
            if not expected_stderr:
                status = Status.RUNTIME
                print(f"  - status: {status}")
                print(f"    {Fore.RED}{stderr}{Fore.RESET}")
                result_exercise["status"] = status.name
                result_exercise["error"] = stderr
                return result_exercise

        if expected_stderr:
            output = stderr
            expected_output = expected_stderr

        if output:
            result_exercise["output"] = output

        if expected_output:
            result_exercise["expected_output"] = expected_output
            colored_output, colored_expected, status = utils.colored_diff(output, expected_output)
            unified_diff = utils.unified_diff(output, expected_output)
            if unified_diff:
                result_exercise["diff"] = unified_diff
            if status != Status.PERFECT:
                print("  - expected output:")
                utils.print_lines(colored_expected, start="    ")
                print("  - output:")
                utils.print_lines(colored_output, start="    ")
        elif output:
            print("  - output:")
            print(output)


        tests = exercise.get("tests", None)
        if tests:
            result_exercise["tests"] = []
            for test in tests:
                result_test, test_status = self.run_test(test)
                result_exercise["tests"].append(result_test)
                status = status.merge(test_status)

        result_exercise["status"] = status.name
        print(f"  STATUS {name}: {status}")


        if interactive:
            self.run_interactive()

        for post_script in post:
            try:
                self.run_query(post_script)
            except Exception as e:
                print(f"  {Fore.RED}Error running exercise post scripts:{Fore.RESET}")
                print(f"  {Fore.RED}{e}{Fore.RESET}")

        return result_exercise


    def run_test(self, test):
        result_test = {}
        name = test["name"]
        test_input = test["input"]
        force = test.get("force", False)
        post = test.get("post", [])
        expected_output = test.get("output", "").strip()
        expected_stderr = test.get("stderr", "").strip()

        result_test["name"] = name
        result_test["input"] = test_input

        output = ""
        stderr = ""
        status = Status.PERFECT

        try:
            result_query = self.run_query(test_input, force=force)
            output = result_query.stdout.strip()
            stderr = re.sub(r" at line \d+", "", result_query.stderr.strip())
        except TimeoutError:
            status = Status.TIMEOUT
            print(f"  - test: {name} - {status}")
            print(f"    {Fore.RED}TIMEOUT{Fore.RESET}")
            result_test["status"] = status.name
            return result_test, status
        except Exception as e:
            stderr = re.sub(r" at line \d+", "", e.stderr).strip()
            if not expected_stderr:
                status = Status.RUNTIME
                print(f"  - test: {name} - {status}")
                print(f"    {Fore.RED}{stderr}{Fore.RESET}")
                result_test["status"] = status.name
                result_test["error"] = stderr
                return result_test, status

        if expected_stderr:
            output = stderr
            expected_output = expected_stderr

        if expected_output:
            result_test["expected_output"] = expected_output
            if not output:
                status = Status.EMPTY
            else:
                result_test["output"] = output
                if expected_output:
                    colored_output, colored_expected_output, status = utils.colored_diff(output, expected_output)
                    unified_diff = utils.unified_diff(output, expected_output)
                    if unified_diff:
                        result_test["diff"] = unified_diff
                    output = colored_output
                    expected_output = colored_expected_output

        result_test["status"] = status.name
        print(f"  - test: {name} - {status}")
        # print(f"{status}\n{output}\n{expected_output}")
        if status != Status.PERFECT:
            self.print_test(name, test_input, expected_output, output, status)

        for post_script in post:
            self.run_query(post_script)

        return result_test, status


    def print_test(self, name, test_input, expected_output, output, status=None):
        if len(test_input) > 0:
            print("    input:")
            utils.print_lines(test_input, start=f"{Fore.CYAN}      ", end=Fore.RESET)

        if expected_output:
            print("    expected_output:")
            utils.print_lines(expected_output, start="      ")
        if output:
            print("    output:")
            utils.print_lines(output, start="      ")


    def print_source(self, source_content):
        utils.line_number_print(utils.highlight(source_content, "sql", self.light).strip())

def prettify_sql_output(text, headers=True):
    table = []
    max_length = []
    for line in text.strip().splitlines():
        row = line.split("\t")
        table.append(row)
        for i, el in enumerate(row):
            if i >= len(max_length):
                max_length.append(len(el))
            else:
                max_length[i] = max(max_length[i], len(el))

    def print_separator(max_length):
        text = ""
        text += "+"
        for el in max_length:
            text += "-"*(el+2)
            text += "+"
        text += "\n"
        return text

    def print_line(items, max_length):
        text = "|"
        for i, el in enumerate(items):
            text += f" {el}"
            text += " " * (max_length[i] - len(el))
            text += " |"
        text += "\n"
        return text

    text = print_separator(max_length)
    for i, line in enumerate(table):
        text += print_line(line, max_length)
        if headers and i == 0:
            text += print_separator(max_length)
    text += print_separator(max_length)
    text += f"{len(table) - 1 if headers else 0} rows in set"
    return text

import sys
import argparse
from pathlib import Path
import copy
import pathlib

path_to_hermes = pathlib.Path(__file__).parent.resolve().joinpath("..")
sys.path.append(str(path_to_hermes))
from ..core import settings as st
from ..core.execution_directives import ExecDirectives

# todo: include the add to dictionary method from settings


def bool2str(s):
    if s.lower() in ["0", "false", "f"]:
        return False
    elif s.lower() in ["1", "true", "t"]:
        return True


class ExecutionFile:

    option_parser = argparse.ArgumentParser()
    option_parser.add_argument(
        "-ca",
        action="append",
        help="Add a file to be copied after execution",
        required=False,
    )
    option_parser.add_argument(
        "-cb",
        action="append",
        help="Add a file to be copied before execution",
        required=False,
    )
    option_parser.add_argument(
        "-ma",
        action="append",
        help="Add a file to be moved after execution",
        required=False,
    )
    option_parser.add_argument(
        "-l",
        "--log",
        type=bool2str,
        required=False,
        default="True",
        help="Store stdout and stderr in log files",
    )
    option_parser.add_argument(
        "-c",
        "--comment",
        action="append",
        help="Optional comment to be stored in hermes.info",
        required=False,
    )
    option_parser.add_argument(
        "-m",
        "--message",
        help="Send telegram message after job is done",
        default=False,
        action="store_true",
    )

    @staticmethod
    def write_pre(f=None, **pre_dict):
        """Write the PRE section of a hermes file given the info in pre_dict.
        If f is given write it to this file, else return a string.

        :param f: Optional file object
        :param pre_dict: A dictionary with entries "setting:value"
        """
        res = ["PRE"]
        for setting, value in pre_dict.items():
            res.append("%s:%s" % (setting, str(value)))
        res = "\n".join(res) + "\n"
        if f:
            f.write(res)
        else:
            return res

    @staticmethod
    def write_std(f=None, **std_dict):
        """Write the STD section of a hermes file given the info in std_dict.
        If f is given write it to this file, else return a string.

        :param f: Optional file object
        :param pre_dict: A dictionary with entries "flag:value"
        """
        res = ["STD"]
        for flag, value in std_dict.items():
            res.append("-%s %s" % (flag, str(value)))
        res = "\n".join(res) + "\n"
        if f:
            f.write(res)
        else:
            return res

    @staticmethod
    def write_exec(script_names, script_options_list, hermes_options_list, f=None):
        """Write the EXEC part of an .hermes file to f if given else return it a string.

        :param script_names: A list of script names as strings
        :param script_options_list: A list of dictionaries with entries "flag(str):value" describing script options.
               Flags should not include the '-' sign.
        :param hermes_options_list: A list of dictionaries with enrties "flag(str):value" describing hermes options.
               Flags should not include the '-' sign.
        :param f: (Optional) file object
        """
        res = ["EXEC"]
        line_format = "[[python, {scriptname}, {scriptoptions}],[{hermesoptions}]]"
        for scriptname, script_options, hermes_options in zip(
            script_names, script_options_list, hermes_options_list
        ):
            scriptoptions = ",".join(
                "-%s %s" % (flag, str(value)) for flag, value in script_options.items()
            )
            hermesoptions = ",".join(
                "-%s %s" % (flag, str(value)) for flag, value in hermes_options.items()
            )
            res.append(
                line_format.format(
                    scriptname=scriptname,
                    scriptoptions=scriptoptions,
                    hermesoptions=hermesoptions,
                )
            )
        res = "\n".join(res)
        if f:
            f.write(res)
        else:
            return res

    def get_std_args(self):
        return self.std_arguments

    def get_hermes_options(self, id):
        assert id < len(self.executions), (
            "Execution with id " + str(id) + "doesn't exist"
        )

        return self.executions[id][1]

    def get_exec_arguments(self, id):
        assert id < len(self.executions), (
            "Execution with id " + str(id) + "doesn't exist"
        )

        cmd = self.executions[id][0]

        if cmd[0].startswith("./"):
            args = cmd[1:]
        elif cmd[0].startswith("python"):
            args = cmd[2:]
        else:
            raise ValueError("Unexpected cmd in exec options: %s" % str(cmd))

        # add the std args
        args += self.std_arguments

        options = {}
        flags = []
        positional = []

        for arg in args:
            # positional argument
            if not arg.startswith("-"):
                positional.append(arg)
            else:
                split_arg = arg.split(" ")
                # flag
                if len(split_arg) == 1:
                    flags.append(arg)
                # option
                elif len(split_arg) == 2:
                    option, value = split_arg
                    options[option] = value
                # option with several args
                elif len(split_arg) > 2:
                    option = split_arg[0]
                    value = " ".join(split_arg[1:])
                    options[option] = value
                else:
                    raise ValueError("Could not parse exec argument %s" % arg)

        return positional, flags, options

    # make the magic happen -> check whether the option exists and parse it to the wanted type
    def parse_hermes_option(self, options):
        if not isinstance(options, list):
            options = [options]
        options = [opt for opt in options if opt != ""]
        if len(options) > 0:
            try:
                option_parser_input = [item.lstrip().rstrip() for item in options]
                option_parser_input = " ".join(option_parser_input)
                option_parser_input = option_parser_input.split(" ")
            except AttributeError:
                raise ValueError("Line: %s\n does not match EXEC convention")
            args = ExecutionFile.option_parser.parse_args(option_parser_input)
        else:
            args = ExecutionFile.option_parser.parse_args([])
        if not hasattr(args, "ca") or not args.ca:
            args.ca = []
        if not hasattr(args, "cb") or not args.cb:
            args.cb = []
        if not hasattr(args, "ma") or not args.ma:
            args.ma = []
        if not hasattr(args, "comment") or not args.comment:
            args.comment = []
        return args

    def parse_pre(self, lines):
        # parse the pre section of the file and update the settings
        for i, line in enumerate(lines):
            st.add_to_dictionary(self.settings, line, ":", i)

    def parse_std(self, stdh_lines, stde_lines):
        self.std_options = self.parse_hermes_option(stdh_lines)
        self.std_arguments = stde_lines

    def parse_exec_line(self, line):
        # split when closing the first bracket
        line_array = line.split("]")
        # remove the resulting empty strings and cast back to list
        line_array = list(filter(None, line_array))
        # make sure there are exactly two different elements left
        assert len(line_array) == 2, (
            "execution line did not fit our convention:\n%s" % line
        )

        # take cmd, delete opening braces
        cmd = line_array[0][2:]
        # parse to an actual list
        cmd = [itm.rstrip().lstrip() for itm in cmd.split(",")]

        # extract hermes options
        options_line = line_array[1].split(",")
        options_line = list(filter(None, options_line))

        options = [0 for _ in range(len(options_line))]
        for i, option in enumerate(options_line):
            tbrs = ["(", ")", "[", "]"]
            for tbr in tbrs:
                option = option.replace(tbr, "")
            options[i] = option

        options = self.parse_hermes_option(options)

        return cmd, options

    # so far, there is only the archive file option which can be added possibly multiple times
    # Thus, the union function only need to concatenate the options
    def union_options(self, standard_options, other_options):
        options = copy.deepcopy(standard_options)
        options.ca.extend(other_options.ca)
        options.cb.extend(other_options.cb)
        options.ma.extend(other_options.ma)
        options.comment.extend(other_options.comment)
        options.message = standard_options.message or other_options.message

        return options

    def parse_exec(self, lines):

        executions = [0 for _ in range(len(lines))]
        for i, line in enumerate(lines):
            cmd, options = self.parse_exec_line(line)

            options = self.union_options(self.std_options, options)

            executions[i] = (cmd, options)

        self.executions = executions

    def __init__(self, path_to_execution_file, comment=[], path_to_root=None):
        self.path_to_execution_file = (
            Path(path_to_execution_file)
            if isinstance(path_to_execution_file, str)
            else path_to_execution_file
        )
        self.settings = st.load(path_to_root=path_to_root)
        self.parse()
        for execution in self.executions:
            execution[1].comment.extend(comment)

    def __str__(self):
        return str(self.path_to_execution_file)

    def create_single_execution_hermesfile(self, name, num_execution):
        with open(name, "w") as f:
            # todo check whether the ending must be added
            for line in self.filelines[: self.exec_index + 1]:
                f.write(line + "\n")
            f.write(self.filelines[self.exec_index + num_execution + 1])

    def create_example_hermesfile(self, name="example.hermes"):
        pass
        # todo when format is really (!) finished )
        # else we will redo this a thousand times

    def parse(self):
        with open(self.path_to_execution_file, "r") as f:
            self.filelines = f.read().splitlines()

        # resolve exec directives into exec lines
        changes = True
        while changes:
            new_lines = []
            changes = False
            for line in self.filelines:
                compilation, had_effect = ExecDirectives.resolve(line)
                new_lines.extend(compilation)
                changes = changes or had_effect
            self.filelines = new_lines

        self.pre_index = self.filelines.index("PRE")
        self.stdh_index = self.filelines.index("STD-H")
        self.stde_index = self.filelines.index("STD-E")
        self.exec_index = self.filelines.index("EXEC")

        # parse pre
        self.parse_pre(self.filelines[self.pre_index + 1 : self.stdh_index])

        # parse std
        self.parse_std(
            self.filelines[self.stdh_index + 1 : self.stde_index],
            self.filelines[self.stde_index + 1 : self.exec_index],
        )

        # parse exec
        self.parse_exec(self.filelines[self.exec_index + 1 :])

    def print_lines(self):
        for line in self.filelines:
            print(line)

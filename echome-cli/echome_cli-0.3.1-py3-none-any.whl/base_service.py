import sys
import argparse
import json
import operator
from functools import reduce
from tabulate import tabulate
from echome.session import Session
from .defaults import APP_NAME, DEFAULT_FORMAT


class BaseService:
    session:Session

    parser = None
    root_parser = None

    output_flag_args = ["--output", "-o"]
    output_flag_kwargs = {
        'help': 'Output format as JSON or Table',
        'choices': ["table", "json"],
        'default': DEFAULT_FORMAT
    }

    wide_flag_args = ["--wide", "-w"]
    wide_flags_kwargs = {
        'help': 'Show more columns when additional data in Table view.',
        'action': 'store_true',
        'default': False
    }

    exclusions = []

    def parent_service_argparse(self):
        """Parent service argument parser"""

        parser = argparse.ArgumentParser(
            description=f"Interact with the {self.parent_full_name} service", 
            prog=f"{APP_NAME} {self.parent_service}",
            usage=self.usage()
        )

        parser.add_argument('subcommand', help=f"Subcommand for the {self.parent_service} service.")
        self.parser = parser
        args = parser.parse_args(sys.argv[2:3])
        subcommand = str(args.subcommand).replace("-", "_")

        # Set the default output (if not set by the user)
        #self.output_flag_kwargs["default"] = self.session.config.config_value

        if not hasattr(self, subcommand):
            print('Unrecognized subcommand')
            parser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, subcommand)()


    def usage(self):
        """Return CLI usage string with all available commands"""
        commands = self.get_list_of_commands()
        usage  = f"{APP_NAME} {self.parent_service} [command] [subcommands] <options>\n\n"
        usage += f"Available {self.parent_service} commands:\n"
        for cmd in commands:
            usage += f"  {cmd}\n"
        usage += " \n"
        
        return usage


    def get_list_of_commands(self, exclude=[]):
        """
        Gets the list of public methods for the class. 
        
        Converts underscores to dashes to automatically add into the ArgumentParser's choices variable
        """
        method_list = [func for func in dir(self) if callable(getattr(self, func))]
        exclude += [
            "usage",
            "get_list_of_commands",
            "parent_service_argparse",
            "get_from_dict",
            "print_table",
            "print_output",
            "get_from_nested_list",
        ] + self.exclusions

        methods = []
        for method in method_list:
            if not method.startswith("_") and not method in exclude:
                methods.append(method.replace("_", "-"))

        return methods
    
    @staticmethod
    def get_from_dict(dict, mapList):
        """Traverse a dictionary to get a nested value from a list """
        return reduce(operator.getitem, mapList, dict)
    

    @staticmethod
    def get_from_nested_list(dictionary, keys):
        items = []
        for val in dictionary[keys[0]]:
            if val:
                items.append(val[keys[1]])

        return ",".join(items)


    def print_table(self, objlist, header=None, data_columns=None, wide:bool=False):
        """
        Generic function for printing a Tabulate table.

        Classes that inherit from this base class
        should set __init__ variables: self.table_headers, self.data_columns with information for 
        that resource. But they can be overwritten by setting parameters.
        Nested dictionary items should be a list, e.g. '[dict_key1, ["dict_key2", "nested_key1"], dict_key3]'
        """
        if not header:
            header = self.table_headers + self.extra_table_headers if wide else self.table_headers
        
        if not data_columns:
            data_columns = self.data_columns + self.extra_data_columns if wide else self.data_columns
        
        all_rows = []
        for row in objlist:
            formatted_row = []
            for col in data_columns:
                if isinstance(col, list):
                    try:
                        res = self.get_from_dict(row, col)
                    except TypeError:
                        try:
                            res = self.get_from_nested_list(row, col)
                        except Exception:
                            res = ""
                    except KeyError:
                        res = ""
                    
                else:
                    res = row[col]
                formatted_row.append(res)

            all_rows.append(formatted_row)

        print(tabulate(all_rows, header))
    

    def print_output(self, output, format, func = None, wide:bool = False):
        """Prints the output based on the provided format"""

        if func == None:
            func = self.print_table

        if format == "table":
            func(output, wide=wide)
        elif format == "json":
            print(json.dumps(output, indent=4))

"""run_label.py"""

from argparse import ArgumentParser
from tabulate import tabulate
from termcolor import colored
from taoist.read_project_dict import read_project_dict
from taoist.read_label_dict import read_label_dict


async def run_label(args: ArgumentParser) -> None:
    """
    Run the label command
    """

    # Read config and project list
    api, _ = await read_project_dict()

    # Read label list into dictionary
    label_dict = await read_label_dict(api)

    # Process subcommand
    if args.subcommand == "list":
        table_header = ["id", "name"]
        label_list = []
        for key, label in label_dict.items():
            row = [
                key,
                colored(label.name, 'white', attrs=['bold'])
            ]
            label_list.append(row)
        print(tabulate(label_list, headers=table_header))
    elif args.subcommand == "create":
        label_name = args.label_name if args.label_name else input("Enter new label name: ")
        try:
            label = await api.add_label(name=label_name)
        except Exception as error:
            raise error
        print(f"Successfully created label \"{label_name}\"")
    elif args.subcommand == "delete":
        label_id = args.label_id if args.label_id else int(input("Enter label ID: "))
        try:
            is_success = await api.delete_label(label_id=label_id)
        except Exception as error:
            raise error
        if is_success:
            print(f"Successfully deleted label \"{label_dict[label_id].name}\"")
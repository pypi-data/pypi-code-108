from os import path
from .utils import parse_params_values
from .cli_configs import BootstrapConfig
from ..pipeline.config import generate_nabu_configfile
from ..pipeline.fullfield.nabu_config import nabu_config as default_fullfield_config

def parse_sections(sections):
    sections = sections.lower()
    if sections == "all":
        return None
    sections = sections.replace(" ", "").split(",")
    return sections


def bootstrap():
    args = parse_params_values(
        BootstrapConfig,
        parser_description="Initialize a nabu configuration file"
    )

    do_bootstrap = bool(args["bootstrap"])
    do_convert = (args["convert"] != "")
    no_comments = bool(args["nocomments"])

    if do_convert: # do_convert
        print("The --convert option is deprecated. It will be removed in a future version")
        exit(1)
    if do_bootstrap:
        print("The --bootstrap option is now the default behavior of the nabu-config command. This option is therefore not needed anymore.")

    if path.isfile(args["output"]):
        rep = input("File %s already exists. Overwrite ? [y/N]" % args["output"])
        if rep.lower() != "y":
            print("Stopping")
            exit(0)

    prefilled_values = {}
    if args["dataset"] != "":
        prefilled_values["dataset"] = {}
        user_dataset = args["dataset"]
        if not path.isabs(user_dataset):
            user_dataset = path.abspath(user_dataset)
            print("Warning: using absolute dataset path %s" % user_dataset)
        if not path.exists(user_dataset):
            print("Error: cannot find the file or directory %s" % user_dataset)
            exit(1)
        prefilled_values["dataset"]["location"] = user_dataset

    generate_nabu_configfile(
        args["output"],
        default_fullfield_config,
        comments=not(no_comments),
        options_level=args["level"],
        prefilled_values=prefilled_values,
    )

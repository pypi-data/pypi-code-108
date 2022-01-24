from argparse import ArgumentParser

def parse_params_values(Params, parser_description=None, program_version=None):
    parser = ArgumentParser(description=parser_description)
    for param_name, vals in Params.items():
        optional = not(vals.pop("mandatory", False))
        if optional:
            param_name = "--" + param_name
        parser.add_argument(param_name, **vals)
    if program_version is not None:
        parser.add_argument('--version', '-V', action='version', version=program_version)
    args = parser.parse_args()
    args_dict = args.__dict__
    return args_dict

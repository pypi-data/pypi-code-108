import argparse
import os

import pkg_resources
import sys


def main():
    deploy_name = 'shyft.dashboard'

    all_entry_points = pkg_resources.get_entry_map(deploy_name, group='console_scripts')
    entry_points = {}
    entry_point_names_str = ''
    commands = []
    commands_doc = []
    x = len(deploy_name) + 1

    for e_name, ep in all_entry_points.items():
        if e_name == deploy_name:
            continue
        ep_func = ep.load()
        doc = ep_func.__doc__ or ''
        doc = doc.split(os.linesep)[0].strip()
        entry_point_names_str += f'    {e_name}\n    '
        command = e_name[x:]
        commands.append(command)
        commands_doc.append(doc)
        entry_points[command] = ep_func

    commands_str = ''
    max_command_length = max([len(c) for c in commands]) + 1
    for c, d in zip(commands, commands_doc):
        if d:
            commands_str += f'    {c:<{max_command_length}} : {d}\n    '
        else:
            commands_str += f'    {c:<{max_command_length}}\n    '
    h = f"""
    Welcome to {deploy_name.upper()} 
    
    This pkg provides a set of commands (below) which can be used like:
        {deploy_name} <command> --argument XXX -f
    
    All commands are:

    {commands_str}

    Use: `{deploy_name} <command> -h, --help` to get more information about each command.
    """
    parser = argparse.ArgumentParser(add_help=True, description=h,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     usage=f'{deploy_name} <command> [<args>]')
    parser.add_argument('command', help='Subcommand to run')
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args(sys.argv[1:2])
    if args.command not in entry_points:
        print('Unrecognized command')
        parser.print_help()
        exit(1)
    # use dispatch pattern to invoke method with same name
    entry_points[args.command](sys.argv[2:])


if __name__ == '__main__':
    main()

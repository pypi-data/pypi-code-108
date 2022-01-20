"""Parse through a list of 'changed inventory files' to determine an appropriate
playbook_limit variable. The inferred playbook_limit is printed to stdout."""
import configargparse

import ntsbuildtools.ansible.playbook.limit_reducer

def config_parser(parser: configargparse.ArgParser):
    parser.add_argument('source',
                        help='The path to the file that contains a list of paths (each separated by a  new line).')
    parser.add_argument('hosts',
                        help='The path to the relevant (`ini` styled) Ansible hosts file.')

def main(args: configargparse.Namespace):
    # Do the work of actually inferring the playbook limit from the pathnames listed in 'source' file
    playbook_limit = ntsbuildtools.ansible.playbook.limit_reducer.infer_playbook_limit(args.source, args.hosts)

    # Print the PLAYBOOK_LIMIT to stdout
    print(",".join(list(playbook_limit)))

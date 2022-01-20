#!/usr/bin/env python3

"""
TODO
In Transipedia, change type 'counts' by 'query' and 'indexes' by 'list'
and in this file 'to_send({'type'='counts', .....})' by 'to_send({'type'=type, .....})'
"""

""" Module doc """

import sys
import os
import argparse
import socket
import pickle

# sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import info
import common as stream



def main():
    """ Function doc """
    args = usage()
    # ~ print(f"SENT to {args.server}:{vars(args)}")
    received = ask_server(vars(args))
    # ~ print(f"RECEIVED from {args.server}: {received}")
    client = Client(args, received)
    client.handle_recv()


def ask_server(args):
    """
    args must be a dict(), containing:
        - 'server': the name or IP of rdeer-socket
        - 'port': the TCP port on which rdeer-socket listen
        - 'type' could be 'list', 'start', 'stop', 'query', 'check'
        - 'index' name of the index (mandatory when 'type' is 'start', 'stop', 'query', 'check')
        - 'query' path/file of a fasta file (mandatory when 'type' is 'query')
    """
    server = args['server']
    port = args['port']
    received = None
    ### Connection to server
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.settimeout(4)
        conn.connect((server, port))    # Connect to server
        conn.settimeout(None)
    except socket.timeout:
        received = {
                    'type': args['type'],
                    'status' : 'error',
                    'data': (f"ErrorConnection: unable to connect to {server} on port {port}"
                            " (server not responding on this port)."),
                    }
        return received
    except socket.gaierror:
        received = {
                    'type': args['type'],
                    'status' : 'error',
                    'data': f"ErrorConnection: unable to connect to {server} on port {port} (might a name resolution issue).",
                    }
        return received
    except ConnectionRefusedError:
        received = {
                    'type': args['type'],
                    'status' : 'error',
                    'data': f"Error: unable to connect to {server!r} on port {port}.",
                    }
        return received

    ### send request to rdeer-socket
    if args['type'] == 'query':
        ### when rdeer-client is used as a program, query is a string IO
        if hasattr(args['query'], 'read'):
            args['query'] = args['query'].read()
        ### query empty
        if not args['query']:
            received = {
                    'type': args['type'],
                    'status' : 'error',
                    'data': "query is empty.",
                    }
            return received
    ### send to rdeer-server, using lib/rdeer_common library
    to_send = pickle.dumps(args)
    stream.send_msg(conn, to_send)


    ### received from rdeer-server
    received = stream.recv_msg(conn)
    received = pickle.loads(received)

    ### close connexion
    conn.close()

    ### some controls
    check_data(received)
    received['version'] = info.VERSION

    return received


def check_data(received):
    """ Control some stuff """
    ### Sometimes, rdeer-server send only header (because problem with index)
    if received['type'] == 'query':
        data = received['data']
        ## if rdeer-server return only header
        n = data.find('\n')
        if len(data) <= n+2:
            received['status'] = 'error'
            received['data'] = {
                                "rdeer found the index but only header was returned (no counts)."
                                "Try again and contact the administrator if the issue still occurs."
                                }


class Client:

    def __init__(self, args, received):
        """ Function doc """
        self.args = args
        self.received = received

    def handle_recv(self):
        """ Function doc """
        received = self.received
        ### Depending on the request to the server and its response, handle received data
        if received['status'] == 'success':
            try:
                getattr(self, received['type'])()
            except KeyError:
                sys.exit(f"{color.RED}Error: unknown type {received['type']!r}.")
        else:
            try:
                getattr(self, received['status'])()
            except KeyError:
                sys.exit(f"{color.RED}Error: unknown status {received['status']!r}.")


    def list(self):
        """Return the list of indexes"""
        if self.args.all:
            LOADCOL  = "\033[1m\033[5;36m"    # blinking and bold cyan
            RUNCOL   ='\033[1;32m'            # green
            AVAILCOL = '\033[1;34m'           # blue
            ERRORCOL = '\033[1;31m'           # red
            color_status = { 'available': AVAILCOL, 'running' : RUNCOL, 'loading': LOADCOL, 'error': ERRORCOL }
            gap = max([len(index) for index in self.received['data']])
            print('\n'.join([ f"{k.ljust(gap)}  [{color_status[v['status']]}{v['status'].center(9)}{color.END}]" for k,v in sorted(self.received['data'].items(), key=lambda v: (v[0].casefold()))]))
        else:
            print('\n'.join([k for k,v in sorted(self.received['data'].items()) if v['status'] == 'running']))

    def start(self):
        print(f"{self.args.index} is now {self.received['data']['status']}")


    def stop(self):
        print(self.received['data'])


    def check(self):
        print(self.received['data'])


    def query(self):
        """ If output file is not specified, print to stdout """
        if not self.args.outfile:
            print(self.received['data'], end='')
        else:
            try:
                with open(self.args.outfile, 'w') as fh:
                    fh.write(self.received['data'])
            except FileNotFoundError:
                sys.exit(f"{color.RED}Error: no such directory {os.path.dirname(self.args.outfile)!r}{color.END}.")
            print(f"{self.args.outfile!r} created succesfully.")


    def error(self):
        """ Function doc """
        print(self.received['data'])



class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def usage():
    """
    Help function with argument parser.
    https://docs.python.org/3/howto/argparse.html?highlight=argparse
    """
    # build parser
    parser = argparse.ArgumentParser(prog=info.APPNAME)
    global_parser = argparse.ArgumentParser(add_help=False)
    index_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()
    subparsers.dest = 'type'
    subparsers.required = True
    # Global arguments
    global_parser.add_argument("-s", "--server",
                        help="SRV: server who hosting index (default localhost)",
                        metavar="SRV",
                        default='localhost',
                       )
    global_parser.add_argument("-p", "--port",
                        help="PORT: listening tcp port (default 12800)",
                        default=12800,
                        metavar='PORT',
                        choices=list(range(1,65537)),
                        type=int,
                       )
    index_parser.add_argument('index',
                        help="INDEX: Reindeer index",
                        metavar="INDEX",
                        # required=True,
                        )
    # create subparser for the "list" command
    parser_list = subparsers.add_parser("list",
                        # ~ aliases=['li'],
                        parents = [global_parser],
                        help="List all running index",
                        )
    parser_list.add_argument('-a', '--all',
                        action="store_true",
                        help="show all indexes and their status, instead of running indexes only",
                       )
    # create subparser for the "query" command
    parser_query = subparsers.add_parser("query",
                        # ~ aliases=['qu'],
                        parents = [index_parser, global_parser],
                        help="Send a request to a specified index",
                        )
    parser_query.add_argument('-q', '--query',
                        type=argparse.FileType('r'),
                        required=True,
                        help="QUERY: query file as fasta format",
                        )
    parser_query.add_argument('-o', '--outfile',
                        help="OUTFILE: outfile name",
                        )
    parser_query.add_argument('-t', '--threshold',
                        help="THRESHOLD: minimum mean of kmers in dataset (see Reindeer help)",
                        )
    parser_query.add_argument('-n', '--normalize',
                        action="store_true",
                        help="Normalize results, fos.txt must contains counts (see fos_buider.py command)",
                       )
    # create subparser for the "check" command
    parser_check = subparsers.add_parser("check",
                        # ~ aliases=['ch'],
                        parents=[global_parser],
                        help="check specified index (all indexes by default)",
                        )
    parser_check.add_argument('index',
                        help="INDEX: index to check (default: all)",
                        metavar="INDEX",
                        )
    # create subparser for the "start" command
    parser_start = subparsers.add_parser("start",
                        parents=[index_parser, global_parser],
                        help="Start specifed index",
                        )
    # create subparser for the "stop" command
    parser_start = subparsers.add_parser("stop",
                        parents=[index_parser, global_parser],
                        help="Stop specifed index",
                        )
    # arguments with special action
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f"{parser.prog} v{info.VERSION}",
                       )


    ### Go to "usage()" without arguments or stdin
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    return parser.parse_args()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3


'''
rdeer-socket is the server part of rdeer-service.
It handle Reindeer running in socket mode.

at start up
- rdeer-server listening for the client
- An instance of Rdeer is created
    - launch a thread scanning the root directory of indexes
    - received clients requests


Starting a Reindeer socket
- When index starting:
    - lance un Reindeer query sur un port réseau distinct avec subprocess.Popen()
    - ajoute dans un dictionnaire dict['nom de l'index'] = {'status': 'loading', 'port': 'n°'}
    - qui scanne toute les secondes si le port réseau est ouvert
    - lorsque le port réseau est ouvert
        - se connecter en client sur l'index Reindeer
            - vérifier si l'index fonctionne
            - modifier l'entrée du dictionnaire dict['nom de l'index'] = {'status': 'running', 'port': 'n°'}
            - rester en attente
'''

import os
import sys
import pathlib
import socket
import argparse
import threading
import pickle
import shutil
# ~ import psutil
import tempfile
import signal
import subprocess
import time
from datetime import datetime
from functools import partial

import common as stream
import info



DEFAULT_PORT       = 12800
REINDEER           = 'Reindeer-socket'
INDEX_FILE         = "reindeer_matrix_eqc.gz"
BASE_TMPFILES      = '/tmp'
WATCHER_SLEEP_TIME = 8
NORM               = 1000000000     # Normalisation factor
### Allowed request types
ALLOWED_TYPES = ['list', 'start', 'stop', 'query', 'check']
### Do not change (unless using another file)
FOS                 = 'fos.txt'     # used to header and normalization
### do not change (unless Reindeer-socket is modified)
class RDSock_Mesg:
    HELP  = ' * HELP'
    INDEX = 'INDEX'
    QUERY = 'DONE'
    QUIT  = 'See you soon'

timestamp = lambda: datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def main():
    args = usage()

    ### Localize full path or index directory (verify if rdeer-socket is a symlink)
    args.index_dir = os.path.join(os.getcwd(), args.index_dir.rstrip('/'))

    ### object rdeer manipulate indexes (list, start stop, query, check)
    rdeer = Rdeer(args)

    ### Stops running indexes on exit (Ctrl C, kill -15)
    exit_graceful = partial(exit_gracefully, rdeer=rdeer)
    signal.signal(signal.SIGINT, exit_graceful)
    signal.signal(signal.SIGTERM, exit_graceful)

    ### server listen for clients
    run_server(args, rdeer)


def exit_gracefully(signal, frame, rdeer):
        for index, values in rdeer.indexes.items():
            if values['status'] == 'running':
                getattr(rdeer, 'stop')({'index':index})
        sys.exit(f"{timestamp()}: Server {socket.gethostname()!r} interrupted by signal {signal}.")


def run_server(args, rdeer):
    """ Function doc """
    port = args.port
    ### run server
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.bind(('', port))
    except OSError:
        sys.exit(f"Error: Address already in use (port: {port}).")
    conn.listen(10)
    ### timestamps server startup
    print(f"{timestamp()}: Server {socket.gethostname()!r} listening on port {port}.", file=sys.stdout)

    while True:
        client, addr = conn.accept()
        ### receive data stream. It won't accept data packet greater than 1024 bytes
        try:
            received = stream.recv_msg(client)
            received = pickle.loads(received)
            print(f"{timestamp()} client:{addr[0]} type:{received['type']}", file=sys.stdout)
            print(f"RECEIVED FROM CLT: {repr(received)} (debug)")
        except pickle.UnpicklingError:
            stream.send_msg(client, b"Error: data sent too big.")
            continue
        except EOFError:
            stream.send_msg(client, b"Error: ran out of input")
            continue
        except TypeError:
            msg = "Error: no data to send to client (Maybe issue comes from client)."
            print(msg, file=sys.stderr)
            stream.send_msg(client, msg.encode())
            continue

        ### call rdeer method corresponding to the type of request
        if received['type'] not in ALLOWED_TYPES:
            msg = "Error: request type not handled (Maybe check version between rdeer-client and rdeer server)."
            print(msg, file=sys.stderr)
            stream.send_msg(client, msg.encode())
            continue

        response = getattr(rdeer, received['type'])(received, addr)

        ## If Error message
        if response['status'] == 'Error':
            print(f"{response['status']}: {response['msg']}", file=sys.stderr, flush=True)
            stream.send_msg(client, pickle.dumps(response))

        ### Send response to client
        stream.send_msg(client, pickle.dumps(response))

    client.close()
    conn.close()



class Rdeer:
    """ Class doc """

    def __init__(self, args):
        """ Class initialiser """
        self.index_dir = args.index_dir
        self.args = args
        ### controls if Reindeer found
        if not shutil.which(REINDEER):
            sys.exit(f"Error: {REINDEER!r} not found")
        ### loop to maintain index info
        self.indexes = {}               # states of all indexes
        self.sockets = {}               # opened sockets
        watcher = threading.Thread(target=self._watcher, name='watcher')
        watcher.daemon = True
        watcher.start()


    def _watcher(self):
        """
        start threading to scan available Reindeer indexes.
        needed :
            - index directory (args)
            - representative index file
        """
        path = self.index_dir
        try:
            os.listdir(path)
        except FileNotFoundError:
            sys.exit(f"Error: directory {path!r} not found.")
        while True:
            ### find available indexes
            found_dirs = []                                     # new indexes
            index_list = [index for index in self.indexes]      # list of current indexes
            ### find all available indexes
            for dir in os.listdir(path):
                subpath = os.path.join(path, dir)
                if os.path.isdir(subpath) and INDEX_FILE in os.listdir(subpath):
                    found_dirs.append(dir)
            ### find for new available indexes
            for dir in found_dirs:
                if not dir in self.indexes:
                    self.indexes[dir] = {'status':'available', 'port':None}
                    print(f"Index found: {dir}")
            ### find for removed indexes
            for dir in index_list:
                if not dir in found_dirs:
                    self.indexes.pop(dir)
                    print(f"Removed index: {dir!r}")

            ### check for running or loading indexes
            for index, value in self.indexes.items():
                # ~ print(f"CHECK {index} (value: {value['status']})")
                if value['status'] == 'loading':
                    # ~ print(f"{index} IS MARKED AS 'loading' --> CHECK IF RUNNING")
                    self._connect_index(index, value['port'])

            time.sleep(WATCHER_SLEEP_TIME)


    def list(self, received, addr=None):
        response = {'type': received['type'], 'status': 'success', 'data': self.indexes}
        return response


    def start(self, received, addr=None):
        '''
        Start a Reindeer Index
        '''
        index = received['index']
        ### Check if index is in list and no still started
        if not index in self.indexes:
            print(f"{timestamp()} Error: unable to start index {index} from {addr[0]} (not found).", file=sys.stdout)
            return {'type':'start', 'status':'error', 'data':f'index {index} not found'}
        if self.indexes[index]['status'] in ['running', 'loading']:
            print(f"{timestamp()} Error: unable to start index {index} from {addr[0]} (still running or loading).", file=sys.stdout)
            return {'type':'start', 'status':'error', 'data':f'index {index} still running or loading.'}
        ### pick free port number
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        ### Launch new instance of Reindeer
        if 'disk-query' in os.listdir(os.path.join(self.args.index_dir, index)):
            cmd = f'{REINDEER} --query -l {os.path.join(self.args.index_dir, index)} -q {port} --disk-query &'
        else :
            cmd = f'{REINDEER} --query -l {os.path.join(self.args.index_dir, index)} -q {port} &'
        try:
            subprocess.check_call(cmd, shell=True)
            # ~ proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError:
            msg = f"Error: index {index} could not be loaded"
            return {'type': received['type'], 'status':'error', 'data': msg}
        self.indexes[index]['status'] = 'loading'
        self.indexes[index]['port'] = port
        ### send
        print(f"{timestamp()} Index {index} started", file=sys.stdout)
        data = self.indexes[index]
        return {'type': received['type'], 'status':'success', 'data': data}


    def stop(self, received, addr=None):
        index = received['index']
        response = self._ask_index(index, b'QUIT', RDSock_Mesg.QUIT)
        if response['status'] == 'success':
            self.sockets[index].shutdown(socket.SHUT_RDWR)
            self.sockets[index].close()
            del(self.sockets[index])
            self.indexes[index]['status'] = 'available'
            self.indexes[index]['port'] = None
            return {'type':'stop', 'status':'success','data':f"Index {index!r} sent: {response['data']!r}."}
        else:
            return {'type':'stop', 'status':'error','data':response['data']}


    def query(self, received, addr=None):
        index = received['index']
        ### define/create tmp dir/files
        tmp_dir = tempfile.mkdtemp(prefix="rdeer-", dir=BASE_TMPFILES)
        infile = os.path.join(tmp_dir, 'query.fa')
        outfile = os.path.join(tmp_dir, 'reindeer.out')
        ### create query fasta file
        with open(infile, 'w') as fh:
            fh.write(received['query'])
        ### build query
        threshold = ':THRESHOLD:' + received['threshold'] if received['threshold'] else ''
        mesg = f"FILE:{infile}{threshold}:OUTFILE:{outfile}".encode()
        ### ask Reindeer
        response = self._ask_index(index, mesg, RDSock_Mesg.QUERY)
        if response['status'] == 'success':
            ### translate Reindeer outfile format to tsv, including headers
            data = self._out_to_tsv(received, response)
            shutil.rmtree(tmp_dir, ignore_errors=True)  # delete tempory files
            ### response to return to client
            return {'type':'query', 'status':response['status'], 'data':data}
        else:
            return {'type':'query', 'status':'error','data':response['data']}


    def check(self, received, addr=None):
        index = received['index']
        response = self._ask_index(index, b'INDEX', RDSock_Mesg.INDEX)
        if response['status'] == 'success':
            return {'type':'check', 'status':'success','data':f"Index {index!r} is working."}
        else:
            return {'type':'check', 'status':'error','data':response['data']}


    def _ask_index(self, index, mesg, control):
        """ Function doc """
        print(f"MESG SEND TO REINDEER: {mesg} (index {index!r}).")
        if index in self.indexes:
            if self.indexes[index]['status'] == 'running':
                try:
                    self.sockets[index].send(mesg)
                    self.sockets[index].settimeout(None)
                    recv = self.sockets[index].recv(1024)
                    # ~ self.sockets[index].settimeout(None)
                except:
                    if self._index_is_crashed(index):
                        print(f"{timestamp()} Error: the index {index!r} crashed during a query", file=sys.stdout)
                    return {'status':'error','data':f'Unable to query the {index!r} index.'}
                recv = recv.decode().rstrip('\n')
                print(f"RECV: {recv} --- CONTROL: {control}")
                if recv.startswith(control):
                    return {'status':'success','data':recv}
                else:
                    return {'status':'error','data':f'Unknow message returned by Reindeer ({recv!r}).'}
            else:
                return {'status':'error','data':f"Index not running (status: {self.indexes[index]['status']!r})"}
        else:
            return {'status':'error','data':f'Index {index!r} not found'}


    def _index_is_crashed(self, index):
        ### check if Reindeer process running, otherwise, probably it is crashed
        port = self.indexes[index]['port']
        cmd = f'Reindeer-socket --query -l {os.path.join(self.args.index_dir, index)} -q *{port}'
        proc = subprocess.run(f"ps -ef | grep '{cmd}'", shell=True, stdout=subprocess.PIPE)
        if proc.returncode:
            self.indexes[index]['status'] = 'error'
            return True
        return False


    def _connect_index(self, index, port):
        """ Function doc """

        if self._index_is_crashed(index):
            print(f'{timestamp()} Error: index {index} crashed during loading', file=sys.stdout)

        ### check if Reindeer process running, otherwise, probably it is crashed
        # ~ cmd = f'Reindeer-socket --query -l {os.path.join(self.args.index_dir, index)} -q *{port}'
        # ~ proc = subprocess.run(f"ps -ef | grep '{cmd}'", shell=True, stdout=subprocess.PIPE)
        # ~ if proc.returncode:
            # ~ print(f'error: index {index} crashed during loading')


        ### try to connect
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # ~ print(f'TRY TO CONNECT TO {index} on port {port}')
        try:
            s.settimeout(1)
            s.connect(('', int(port)))    # Connect to running Reindeer
            # ~ s.settimeout(None)
            self.indexes[index]['status'] = 'running'
            self.sockets[index] = s
            ### evacuate WELCOME and INDEX message
            welcome = s.recv(1024)
            print(f"FIRST MESG: {welcome}")
            index = s.recv(1024)
            print(f"SECOND MESG: {index}")
            s.settimeout(None)
        except ConnectionRefusedError:
            ### try to connect during loading time  (with s.connect(('', int(port)))
            pass
        except OSError:
            ### try to connect during loading time  (with s.connect(('', int(port)))
            pass


    def _out_to_tsv(self, received, response):
        """
        1. reduce counts to one number value,
        2. normalize counts (if asked by client)
        """
        print('_OUT_TO_TSV BEGIN')
        index = received['index']
        normalize = received['normalize']
        samples = []
        kmers_found = []

        ### Add header to data from FOS file (File of Samples)
        header = 'seq_name\t'
        data = []
        try:
            with open(os.path.join(self.args.index_dir, index, FOS)) as fh:
                for line in fh:
                    sample, *kmers = line.split()
                    if kmers: kmers_found.append(kmers[0])
                    samples.append(sample)
                header = header + '\t'.join(samples)
        except FileNotFoundError:
            return f"Error: file {FOS} not found on {socket.gethostname()}:{os.path.join(self.args.index_dir, index)} location."
        header += '\n'       # Add newline at EOL

        ### open Reindeer outfile
        outfile = response['data'].split(':')[1]

        ### if unitig_counts option is set, the output of Reindeer is requered, not TSV file
        if "unitig_counts" in received and received["unitig_counts"]:
            with open(outfile) as fh:
                for line in fh:
                    data.append(line[1:])
            data = ''.join(data)
        else:
            ### Reduce complex values of Reindeer output to single count
            with open(outfile) as fh:
                for line in fh:  # i --> sequence
                    seq_name, *counts = line.rstrip('\n').lstrip('>').split('\t')
                    for j,count in enumerate(counts):           # j --> sample/count
                        if count != '*':
                            counts[j] = [c.split(':')[1] for c in count.split(",")]
                            ### average of untigs counts - but stars  ('*') must be removed
                            counts[j] = sum([int(c) for c in counts[j] if c != '*']) // len(counts[j])
                            ### NORMALIZE if kmers counts are present in file of samples (fos.txt)
                            if normalize and kmers_found:
                                counts[j] = round(NORM * counts[j] / int(kmers_found[j]),2)
                            elif normalize and not kmers_found:
                                response['status'] = 'error'
                                return(f"unable to normalize counts on {index}, it could be that {FOS} does not contain counts.")
                            counts[j] = str(counts[j])
                        else:
                            counts[j] = '0'
                    data.append(seq_name + '\t' + '\t'.join(counts))
            data = '\n'.join(data) + '\n'

        ### join header and counts
        data = header + data
        # ~ print(f"TSV:\n{data[:200]}....")

        return data



def usage():
    """
    Help function with argument parser.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("index_dir",
                        type=_dir_path,
                        help="base directory of Reindeer indexes",
                        metavar=('index_dir'),
                       )
    parser.add_argument("-p", "--port",
                        help=f"port on which the server is listening (default: {DEFAULT_PORT})",
                        metavar="port",
                        default=DEFAULT_PORT,
                        type=int,
                       )
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f"{parser.prog} v{info.VERSION}",
                       )
    parser.add_argument('--help',
                        action='help',
                        default=argparse.SUPPRESS,
                        help=argparse._('show this help message and exit')
                        )
    ### Go to "usage()" without arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    return parser.parse_args()


def _dir_path(string):
    ### for usage(), test if argument is a directory
    if os.path.isdir(string):
        return string
    else:
        sys.exit(f"NotADirectoryError ({string}).")


if __name__ == "__main__":
    main()

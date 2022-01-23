from sys import platform
import sys
import yaml
import json
import os
import socket as sc
import time

from datetime import datetime, timedelta
from socket import socket

from subprocess import call, Popen, PIPE
from io import StringIO


class Middleware:
    '''
    Manages dependencies for 'phobos cli'

    1. gcloud       check installation, install, auth, set-project, import datalab credentials.
    2. kubectl      check installation, install, switch context, update datalab credentials.
    3. polyaxon     port-forward for local/datalab, close-port-forward.
    4. setup        ready-check, install missing dependencies.
    5. exec         PIPE, sys.std(out/in/err) support with wait and comminicatate support.
    '''
    def __init__(self):
        '''
        Initializes setup_list for installation and ready-check order,
        Initializes .phobos in home directory

        '''
        self.local_port = 31833
        self.datalab_port = 8000

    def exec(self, command, forward=False, pipe=True, in_=""):
        '''
        Popen support with input,out and error support 
        
        Params:
        ---
        command: string     Command to execute.
        forward: bool       Doen't wait for command to complete.
        pipe: bool          If True runs command in backend, else truns command interactively.     
        in_: string         Stdin for PIPEd process call.
        '''
        if pipe:
            stdout, stdin, stderr = PIPE, PIPE, PIPE
        else:
            stdout = sys.stdout
            stdin = sys.stdin
            stderr = sys.stderr
        while True:
            p = Popen(command, shell=True, stdout=stdout, stderr=stderr, stdin=stdin)
            out, err = "", ""
            if not pipe:
                p.wait()
                return out, err
            if len(in_) > 0:
                out, err = p.communicate(input=in_.encode('utf-8'))
                out, err = out.decode('utf-8'), err.decode('utf-8')
                if "pip install" in out.lower():
                    continue
                return out, err
            if not forward and len(in_) == 0:
                p.wait()
                out, err = p.stdout.read().decode('utf-8'), p.stderr.read().decode('utf-8')
                return out, err
            else:
                time.sleep(1)
                return "", ""

    def polyaxon_forward_check(self, mode):
        '''Checks if port corresponding to mode is occupied or not'''
        if not self.datalab_config_check():
            self.request_setup()
            return
        socket_ = socket(sc.AF_INET, sc.SOCK_STREAM)
        port = self.local_port if mode == 'local' else self.datalab_port
        out = socket_.connect_ex(('127.0.0.1', port))
        if out == 0:
            socket_.close()
            return True
        else:
            socket_.close()
            return False

    def close_port(self, mode):
        '''Kills process on port corresponding to mode'''
        if mode == "local":
            self.exec(f"kill -9 $(lsof -i TCP:{self.local_port} | grep LISTEN | awk '{{print $2}}')")
        else:
            self.exec(f"kill -9 $(lsof -i TCP:{self.datalab_port} | grep LISTEN | awk '{{print $2}}')")

    def polyaxon_forward(self, mode):
        '''polyaxon-port forward depending on mode=datalab/local. Kills process running on required port'''
        if mode == "local":
            if not self.polyaxon_forward_check(mode):
                self.close_port(mode)
            if not self.kubectl_switch_context(mode):
                raise Exception("Unable to switch kubectl context, Try manually!")
            out, err = self.exec("polyaxon port-forward -t minikube &", forward=True)
            if len(err) == 0:
                pass
            else:
                raise Exception(f"Error in occupying {self.local_port}")
        else:
            if not self.datalab_config_check():
                self.request_setup()
                return
            if not self.polyaxon_forward_check(mode):
                self.close_port(mode)
            if not self.kubectl_switch_context(mode):
                raise Exception("Unable to switch kubectl context, Try manually!")
            out, err = self.exec("polyaxon port-forward &", forward=True)
            if len(err) == 0:
                pass
            else:
                raise Exception(f"Error in occupying port {self.datalab_port}")

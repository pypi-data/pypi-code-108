import json
import asyncio
import socket
import datetime
import hashlib
import requests
import base64
import inspect
import urllib.error
import urllib.request
from itertools import chain
from pathlib import Path, PurePath
from typing import Generator, Tuple, Union
import ipykernel
from jupyter_core.paths import jupyter_runtime_dir

FILE_ERROR = "Can't identify the notebook {}."
CONN_ERROR = "Unable to access server;\n" \
           + "ipynbname requires either no security or token based security."

class tracker:
    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.DISTML_SERVER_IP = "127.0.0.1"
        self.api_endpoint = ""
        self.payload = ""
        self.experiment_id = ""
        self.instance_name = ""
        self.logger_id = ""
        self.data_file = ""
        self.salt = "distml-man"
        self.token = ""
        self.run_type = ""
        self.project = ""
        self.model_name = ""
        self.track = ""
        self.notebook_path = ""
        
    
    def setup(self, config, project_name, model_name, track):
        self.payload = ""
        self.experiment_id = ""
        self.instance_name = ""
        self.logger_id = ""
        self.data_file = ""
        self.salt = "distml-man"
        self.project = project_name
        self.model_name = model_name
        self.track = track
        try:
            with open(config) as f:
                data = f.readlines()
                if len(data)==0:
                    return "Config File is Empty"
            
            with open(config) as f:
                data = json.load(f)
                self.token = data['token']
                self.run_type = data['run_type'] 
                if 'chaya_server_ip' in data:
                    self.DISTML_SERVER_IP = data['chaya_server_ip'] 
                else:
                    self.DISTML_SERVER_IP = "https://chaya.ai"
            print("Setup succesfull")
            self.api_endpoint = str(self.DISTML_SERVER_IP) +"/track/remote_distml_client"
            frame = inspect.stack()[1]
            filename = frame[0].f_code.co_filename
            connection_file = Path(ipykernel.get_connection_file()).stem
            kernel_id = connection_file.split('-', 1)[1]
            runtime_dir = jupyter_runtime_dir()
            runtime_dir = Path(runtime_dir)

            list_maybe_running_servers = []
            if runtime_dir.is_dir():
                for file_name in chain(
                    runtime_dir.glob('nbserver-*.json'),  # jupyter notebook (or lab 2)
                    runtime_dir.glob('jpserver-*.json'),  # jupyterlab 3
                ):
                    list_maybe_running_servers.append(json.loads(file_name.read_bytes()))

            for srv in list_maybe_running_servers:
                try:
                    sessions = self.get_sessions(srv)
                    
                    for sess in sessions:
                        if sess['kernel']['id'] == kernel_id:
                            notebook_file = srv["notebook_dir"] + "/" + sess['notebook']['path']
                            self.notebook_path = notebook_file
                except Exception as e:
                    pass  # There may be stale entries in the runtime directory

        except Exception as err:
            return "Config missing or corrupt"

    def distml_print(self):
        print('api_endpoint %s ' % self.api_endpoint)
        print('payload %s ' % self.payload)

    def distml_setup(self):
        with open('/var/log/distml/metadata/distml.json') as f:
            data = f.readlines()
            if len(data)==0:
                return
        #read metadata
        with open('/var/log/distml/metadata/distml.json') as f:
            data = json.load(f)
            self.api_endpoint = data['distml_api_endpoint']
            self.experiment_id = data['experiment_id']
            self.instance_name = socket.gethostname()
            
        self.logger_id = "distml-manager"
        self.data_file = None
        
    def distml_setup(self, data_path):
        with open('/var/log/distml/metadata/distml.json') as f:
            data = f.readlines()
            if len(data)==0:
                return
        #read metadata
        with open('/var/log/distml/metadata/distml.json') as f:
            data = json.load(f)
            self.api_endpoint = data['distml_api_endpoint']
            self.experiment_id = data['experiment_id']
            self.instance_name = socket.gethostname()
        
        proc_id = hashlib.md5(str(data_path + self.salt).encode('utf-8')).hexdigest()
        self.logger_id=str(proc_id) 
        self.data_file = str(data_path)
        init_ping = None
        if data_path=="distml-manager":
            init_ping = {"status":"init","client_dist_ml_manager":"1"}
        else:
            init_ping = {"status":"init"}
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.send(init_ping))
        loop.close()
        return 0

    def distml_logit(self, data):
        if self.api_endpoint == "":
            return
        # using asyncio to send it
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.send(data))
        loop.close()
        return 0

    def get_sessions(self, srv):
        try:
            qry_str = ""
            token = srv['token']
            if token:
                qry_str = f"?token={token}"
            url = f"{srv['url']}api/sessions{qry_str}"
            with urllib.request.urlopen(url) as req:
                return json.load(req)
        except Exception:
            raise urllib.error.HTTPError(CONN_ERROR)

    def save(self, data):
        if self.api_endpoint == "":
            print("distml api not setup")
            return
        data["project"] = self.project
        data["model_name"] = self.model_name
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["track_metrics"] = self.track 
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        headers = {'content-type': 'application/json'}
        nb_send = False
        data_poll = json.dumps(data)

        if "metrics" in data:
            for metric in data["metrics"].keys():
                metrics_to_track = self.track["end_tag"]["metrics"]
                if metric in metrics_to_track:
                    nb_send = True
        
        if nb_send == True:
            data["detect_recv_notebook"] = True
            data["metrics"] = str(data["metrics"])
            data["metric_type"] = data["metric_type"]
        
        try:
            if nb_send == True:
                data_files = {
                    "nb_file": open(self.notebook_path, "rb")
                }
                response = requests.post(self.api_endpoint, data = data, files = data_files, verify=False)
            else:
                response = requests.post(self.api_endpoint, data_poll, headers=headers, verify=False)
            
            return 

        except Exception:
            raise "unable to connect to noval server"
            
    def saveplot(self, plotfile):
        print(plotfile)
        data = {}
        data["project"] = self.project
        data["model_name"] = self.model_name
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["track_metrics"] = self.track 
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["filename"] = plotfile
        headers = {'content-type': 'application/json'}

        with open(plotfile, 'rb') as img:
            
            response = requests.post(
                url=self.api_endpoint,
                verify=False,
                data={
                    "data": json.dumps(data),
                    "image": base64.b64encode(img.read()),
                    "headers" : headers
                }
            )

        return

    def detect_drift(self, train_data, test_data):
        data = {}
        data["project"] = self.project
        data["model_name"] = self.model_name
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["track_metrics"] = self.track 
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["detect_drift"] = True

        train_file = str(self.project) +"_" + self.model_name + "_train_data.csv"
        train_data.to_csv(train_file,index = False, header=True)
        test_file = str(self.project) +"_" + self.model_name + "_test_data.csv"
        test_data.to_csv(test_file,index = False, header=True)
        
        data_files = {
            "train_file": open(train_file, "rb"),
            "test_file": open(test_file, "rb")
        }

        response = requests.post(self.api_endpoint, data = data, files = data_files, verify=False)

        return

    def distml_train_data_path(self, data_path):
        if self.api_endpoint == "":
            return
        proc_id = hashlib.md5(str(data_path + self.salt).encode('utf-8')).hexdigest()
        self.logger_id=str(proc_id) 
        self.data_file = str(data_path)
        return
 
        


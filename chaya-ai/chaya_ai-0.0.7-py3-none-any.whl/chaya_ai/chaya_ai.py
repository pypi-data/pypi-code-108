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
import urllib3
urllib3.disable_warnings()
from requests.structures import CaseInsensitiveDict
import os
import dbutils
import iplotter
from IPython.core.display import HTML
from iplotter import ChartJSPlotter
from tabulate import tabulate
import pandas as pd
from jinja2 import Template
from IPython.display import IFrame, HTML
from IPython.core.magic import (register_line_magic, register_cell_magic,register_line_cell_magic)

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
        self.notebook_track = True
        self.db_url = ""
        self.db_token = ""
        
    
    def setup(self, config, project_name, track):
        self.payload = ""
        self.experiment_id = ""
        self.instance_name = ""
        self.logger_id = ""
        self.data_file = ""
        self.salt = "distml-man"
        self.project = project_name
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
                    self.DISTML_SERVER_IP = "https://app.chaya.ai"
                if self.run_type == 'databricks' and 'db_url' in data:
                    self.db_url = data["db_url"]
                if self.run_type == 'databricks' and 'db_token' in data:
                    self.db_token = data["db_token"]

            print("Setup succesfull")
            self.api_endpoint = str(self.DISTML_SERVER_IP) +"/track/remote_distml_client"
            if self.run_type == 'local':
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
            elif self.run_type == 'databricks':
                
                db_nb_path = str(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
                db_url = self.db_url
                db_token = self.db_token
                data = {"path": '"'+str(db_nb_path) + '"',"format":"JUPYTER"}
                headers = CaseInsensitiveDict()
                headers["Accept"] = "application/json"
                headers["Authorization"] = "Bearer " + str(db_token)

                resp = requests.get(db_url, headers=headers, params = data)

                cwd = os.getcwd()
                db_nb_name = db_nb_path.split("/")
                f = open(cwd+"/"+ str(db_nb_name[len(db_nb_name)-1]) +'.ipynb', 'w+')
                f.write(base64.b64decode(resp.json()['content']).decode("utf-8"))
                f.close()
            else:
                pass

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
            if nb_send == True :
                data_files = {}
                if self.notebook_track:
                    try:
                        if self.run_type == "local" :
                            data_files["nb_file"] = open(self.notebook_path, "rb")
                        elif self.run_type == 'databricks':
                            db_nb_path = str(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
                            db_url = self.db_url
                            db_token = self.db_token
                            data = {"path": '"'+str(db_nb_path) + '"',"format":"JUPYTER"}
                            headers = CaseInsensitiveDict()
                            headers["Accept"] = "application/json"
                            headers["Authorization"] = "Bearer " + str(db_token)
                            resp = requests.get(db_url, headers=headers, params = data)
                            cwd = os.getcwd()
                            db_nb_name = db_nb_path.split("/")
                            f = open(cwd+"/"+ str(db_nb_name[len(db_nb_name)-1]) +'.ipynb', 'w+')
                            f.write(base64.b64decode(resp.json()['content']).decode("utf-8"))
                            f.close()
                            data_files["nb_file"] = open(cwd+"/"+ str(db_nb_name[len(db_nb_name)-1]) +'.ipynb', "rb")
                    except:
                        print("unable to detect notebook in your env, supported either in self installed cloud vm or local notebooks, google collab or other env is not supported yet, your metrics data send is saved and is available at https://app.chaya.ai")
                        self.notebook_track=False
                        data["detect_recv_notebook"] = False
                else:
                    data["detect_recv_notebook"] = False

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

        try:
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
        except Exception as e:
            print("file not found, please provide the location of the file with full directory path")
            print(e)

        return

    def detect_drift(self, train_data, test_data, categorical_features = ""):
        data = {}
        data["project"] = self.project
        data["model_name"] = self.model_name
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["track_metrics"] = self.track 
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["detect_drift"] = True
        data["categorical_features"] = categorical_features

        try:
            train_file = str(self.project) +"_" + self.model_name + "_train_data.csv"
            train_data.to_csv(train_file,index = False, header=True)
            test_file = str(self.project) +"_" + self.model_name + "_test_data.csv"
            test_data.to_csv(test_file,index = False, header=True)
            
            data_files = {
                "train_file": open(train_file, "rb"),
                "test_file": open(test_file, "rb")
            }

            response = requests.post(self.api_endpoint, data = data, files = data_files, verify=False)
        except Exception as e:
            print("Only pandas dataframes supported with current version, other dtypes will be supported in future")
            print(e)
            None
        # clear the files after transfer
        return

    def save_model(self, model_file):
        data = {}
        data["project"] = self.project
        data["model_name"] = self.model_name
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["track_metrics"] = self.track 
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["model_path"] = True

        try:
            model_file = {
                "model_file": open(model_file, "rb"),
            }

            response = requests.post(self.api_endpoint, data = data, files = model_file, verify=False)
        except Exception as e:
            print("unable to locate model file, please provide full directory path")
            print(e)

        return

    def plot_history(self, keys):
        data = {}
        data["project"] = self.project
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["plot_history"] = True
        for key in keys:
            data[key] = keys[key]

        try:
            response = requests.post(self.api_endpoint, data = data, verify=False)
            chart_d = response.content.decode("utf-8")

            head = """
                <!-- Load Charts.js -->
                <script src='https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.bundle.min.js'></script>
                """

            template = """
                <canvas id='{{div_id}}'></canvas>
                <script>
                    var ctx = document.getElementById('{{div_id}}').getContext('2d');
                    ctx.canvas.width  = {{w}} - (.1 * {{w}});
                    ctx.canvas.height = {{h}} - (.15 * {{h}});
                    var myNewChart = new Chart(ctx,{ type: '{{chart_type}}', data: {{data}}, options: {{options}} });
                </script>
            """

            def render(data,
                        chart_type,
                        options=None,
                        div_id="chart",
                        head="",
                        w=800,
                        h=420):
            

                return Template(head + template).render(
                        div_id=div_id.replace(" ", "_"),
                        data=json.dumps(
                            data, indent=4).replace("'", "\\'").replace('"', "'"),
                        chart_type=chart_type,
                        options=json.dumps(
                            options, indent=4).replace("'", "\\'").replace('"', "'"),
                        w=w,
                        h=h)

            iframe = '<iframe srcdoc="{source}" src="" width="{w}" height="{h}" frameborder="0" sandbox="allow-scripts"></iframe>'

            def plot(data, chart_type, options=None, w=800, h=420):
                """Output an iframe containing the plot in the notebook without saving."""
                return HTML(
                        iframe.format(
                            source=render(
                                data=data,
                                chart_type=chart_type,
                                options=options,
                                head=head,
                                w=w,
                                h=h),
                            w=w,
                            h=h))

            
            return plot(json.loads(chart_d), 'line', options=json.loads(chart_d)["options"])

        except Exception as e:
            print("Unable to reach chaya server, please try again, check status at %s " % self.api_endpoint)
            print(e)
        return

    def show_dataset_changepoints(self, keys):
        data = {}
        data["project"] = self.project
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["get_dataset_changepoints"] = True
        for key in keys:
            data[key] = keys[key]

        try:
            response = requests.post(self.api_endpoint, data = data, verify=False)
            chart_d = response.content.decode("utf-8")
            head = """
                <!-- Load Charts.js -->
                <script src='https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.bundle.min.js'></script>
                """

            template = """
                <canvas id='{{div_id}}'></canvas>
                <script>
                    var ctx = document.getElementById('{{div_id}}').getContext('2d');
                    ctx.canvas.width  = {{w}} - (.1 * {{w}});
                    ctx.canvas.height = {{h}} - (.15 * {{h}});
                    var myNewChart = new Chart(ctx,{ type: '{{chart_type}}', data: {{data}}, options: {{options}} });
                </script>
            """

            def render(data,
                        chart_type,
                        options=None,
                        div_id="chart",
                        head="",
                        w=800,
                        h=420):
            

                return Template(head + template).render(
                        div_id=div_id.replace(" ", "_"),
                        data=json.dumps(
                            data, indent=4).replace("'", "\\'").replace('"', "'"),
                        chart_type=chart_type,
                        options=json.dumps(
                            options, indent=4).replace("'", "\\'").replace('"', "'"),
                        w=w,
                        h=h)

            iframe = '<iframe srcdoc="{source}" src="" width="{w}" height="{h}" frameborder="0" sandbox="allow-scripts"></iframe>'

            def plot(data, chart_type, options=None, w=800, h=420):
                """Output an iframe containing the plot in the notebook without saving."""
                return HTML(
                        iframe.format(
                            source=render(
                                data=data,
                                chart_type=chart_type,
                                options=options,
                                head=head,
                                w=w,
                                h=h),
                            w=w,
                            h=h))

           
            return plot(json.loads(chart_d), 'line', options=json.loads(chart_d)["options"])
        except Exception as e:
            print("Unable to reach chaya server, please try again, check status at %s " % self.api_endpoint)
            print(e)
        return

    def get_history(self, keys):
        data = {}
        data["project"] = self.project
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["plot_history"] = True
        for key in keys:
            data[key] = keys[key]

        try:
            response = requests.post(self.api_endpoint, data = data, verify=False)
            chart_d = response.content.decode("utf-8")

            head = """
                <!-- Load Charts.js -->
                <script src='https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.bundle.min.js'></script>
                """

            template = """
                <canvas id='{{div_id}}'></canvas>
                <script>
                    var ctx = document.getElementById('{{div_id}}').getContext('2d');
                    ctx.canvas.width  = {{w}} - (.1 * {{w}});
                    ctx.canvas.height = {{h}} - (.15 * {{h}});
                    var myNewChart = new Chart(ctx,{ type: '{{chart_type}}', data: {{data}}, options: {{options}} });
                </script>
            """

            def render(data,
                        chart_type,
                        options=None,
                        div_id="chart",
                        head="",
                        w=800,
                        h=420):
            

                return Template(head + template).render(
                        div_id=div_id.replace(" ", "_"),
                        data=json.dumps(
                            data, indent=4).replace("'", "\\'").replace('"', "'"),
                        chart_type=chart_type,
                        options=json.dumps(
                            options, indent=4).replace("'", "\\'").replace('"', "'"),
                        w=w,
                        h=h)

            iframe = '<iframe srcdoc="{source}" src="" width="{w}" height="{h}" frameborder="0" sandbox="allow-scripts"></iframe>'

            def plot(data, chart_type, options=None, w=800, h=420):
                """Output an iframe containing the plot in the notebook without saving."""
                return HTML(
                        iframe.format(
                            source=render(
                                data=data,
                                chart_type=chart_type,
                                options=options,
                                head=head,
                                w=w,
                                h=h),
                            w=w,
                            h=h))

            return json.loads(chart_d), json.loads(chart_d)["options"]
            

        except Exception as e:
            print("Unable to reach chaya server, please try again, check status at %s " % self.api_endpoint)
            print(e)
        return

    def get_dataset_changepoints(self, keys):
        data = {}
        data["project"] = self.project
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["get_dataset_changepoints"] = True
        for key in keys:
            data[key] = keys[key]

        try:
            response = requests.post(self.api_endpoint, data = data, verify=False)
            chart_d = response.content.decode("utf-8")
            head = """
                <!-- Load Charts.js -->
                <script src='https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.bundle.min.js'></script>
                """

            template = """
                <canvas id='{{div_id}}'></canvas>
                <script>
                    var ctx = document.getElementById('{{div_id}}').getContext('2d');
                    ctx.canvas.width  = {{w}} - (.1 * {{w}});
                    ctx.canvas.height = {{h}} - (.15 * {{h}});
                    var myNewChart = new Chart(ctx,{ type: '{{chart_type}}', data: {{data}}, options: {{options}} });
                </script>
            """

            def render(data,
                        chart_type,
                        options=None,
                        div_id="chart",
                        head="",
                        w=800,
                        h=420):
            

                return Template(head + template).render(
                        div_id=div_id.replace(" ", "_"),
                        data=json.dumps(
                            data, indent=4).replace("'", "\\'").replace('"', "'"),
                        chart_type=chart_type,
                        options=json.dumps(
                            options, indent=4).replace("'", "\\'").replace('"', "'"),
                        w=w,
                        h=h)

            iframe = '<iframe srcdoc="{source}" src="" width="{w}" height="{h}" frameborder="0" sandbox="allow-scripts"></iframe>'

            def plot(data, chart_type, options=None, w=800, h=420):
                """Output an iframe containing the plot in the notebook without saving."""
                return HTML(
                        iframe.format(
                            source=render(
                                data=data,
                                chart_type=chart_type,
                                options=options,
                                head=head,
                                w=w,
                                h=h),
                            w=w,
                            h=h))

            return json.loads(chart_d), json.loads(chart_d)["options"]

        except Exception as e:
            print("Unable to reach chaya server, please try again, check status at %s " % self.api_endpoint)
            print(e)
        return

    def show_feature_drifts_dataset_version(self, filter_keys):
        data = {}
        data["project"] = self.project
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["get_feature_drifts_dataset_version"] = True
        for key in filter_keys:
            data[key] = filter_keys[key]

        try:
            response = requests.post(self.api_endpoint, data = data, verify=False)
            features = json.loads(response.content.decode("utf-8"))
            type = []
            drift = []
            value = []
            feature = []
            p_value = []
            for fp in range(0, len(features)):
                type.append(features[fp]["type"])
                drift.append(features[fp]["drift"])
                value.append(features[fp]["value"])
                feature.append(features[fp]["feature"])
                p_value.append(features[fp]["p_value"])
                
            dict = {
                'feature' : feature,
                'type': type,
                'drift': drift,
                'value': value,
                'p_value' : p_value
            }

            df = pd.DataFrame(dict)
            df = df.sort_values(by=['drift','value'], ascending=[False, False])
            return tabulate(df, headers = 'keys', tablefmt = 'html')

        except Exception as e:
            print("Unable to reach chaya server, please try again, check status at %s " % self.api_endpoint)
            print(e)
        return

    def get_feature_drifts_dataset_version(self, filter_keys):
        data = {}
        data["project"] = self.project
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["get_feature_drifts_dataset_version"] = True
        for key in filter_keys:
            data[key] = filter_keys[key]

        try:
            response = requests.post(self.api_endpoint, data = data, verify=False)
            features = json.loads(response.content.decode("utf-8"))
            type = []
            drift = []
            value = []
            feature = []
            p_value = []
            for fp in range(0, len(features)):
                type.append(features[fp]["type"])
                drift.append(features[fp]["drift"])
                value.append(features[fp]["value"])
                feature.append(features[fp]["feature"])
                p_value.append(features[fp]["p_value"])
                
            dict = {
                'feature' : feature,
                'type': type,
                'drift': drift,
                'value': value,
                'p_value' : p_value
            }

            df = pd.DataFrame(dict)
            df = df.sort_values(by=['drift','value'], ascending=[False, False])
            return df

        except Exception as e:
            print("Unable to reach chaya server, please try again, check status at %s " % self.api_endpoint)
            print(e)
        return

    def distml_train_data_path(self, data_path):
        if self.api_endpoint == "":
            return
        proc_id = hashlib.md5(str(data_path + self.salt).encode('utf-8')).hexdigest()
        self.logger_id=str(proc_id) 
        self.data_file = str(data_path)
        return

    def create_deploy_config(self, filter_keys):
        data = {}
        data["project"] = self.project
        data["client_ip"] = "None"
        data["track_type"] = "local"
        data["token"] = self.token
        data["client_report_time"] = str(datetime.datetime.now(datetime.timezone.utc))
        data["create_deploy_config"] = True

        for key in filter_keys:
            data[key] = filter_keys[key]

        try:
            response = requests.post(self.api_endpoint, data = data, verify=False)
            return response

        except Exception as e:
            print("Unable to reach chaya server, please try again, check status at %s " % self.api_endpoint)
            print(e)
        return

    @register_line_magic
    def chaya_annotate(line):
        "chaya_annotate magic"
        return line

    @register_cell_magic
    def chaya_annotate(line, cell):
        "chaya_annotate cell magic"
        return line, cell

    @register_line_cell_magic
    def chaya_annotate(line, cell=None):
        "Magic that works both as %chaya_annotate_cell and as %%chaya_annotate_cell"
        if cell is None:
            pass
        else:
            pass
 
        


import os
import pandas as pd
import yaml
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import uuid
import getpass
import logging

root_dir = os.path.abspath(os.path.dirname(__file__))
yaml_path = os.path.join(root_dir, '../askdata/askdata_config/base_url.yaml')
with open(yaml_path, 'r') as file:
    url_list = yaml.load(file, Loader=yaml.FullLoader)

_LOG_FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] - %(asctime)s --> %(message)s"
g_logger = logging.getLogger()
logging.basicConfig(format=_LOG_FORMAT)
g_logger.setLevel(logging.INFO)

@pd.api.extensions.register_dataframe_accessor("askdata")
class AskdataPandasExtension:
    def __init__(self, pandas_df):
        self._df:pd.DataFrame = pandas_df

        if(not hasattr(self, '_env')):
            self._env = input('Askdata Enviroment: ').lower()

        if self._env == 'dev':
            self.base_url_security = url_list['BASE_URL_SECURITY_DEV']

        if self._env == 'qa':
            self.base_url_security = url_list['BASE_URL_SECURITY_QA']

        if self._env == 'prod':
            self.base_url_security = url_list['BASE_URL_SECURITY_PROD']

        username = input('Askdata Username: ')

        password = getpass.getpass(prompt='Askdata Password: ')

        self.username = username

        data = {
            "grant_type": "password",
            "username": self.username,
            "password": password
        }

        headers = {
            "Authorization": "Basic YXNrZGF0YS1zZGs6YXNrZGF0YS1zZGs=",
            "Content-Type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache,no-cache"
        }

        authentication_url = self.base_url_security + '/domain/askdata/oauth/token'

        # request token for the user
        s = requests.Session()
        s.keep_alive = False
        r1 = s.post(url=authentication_url, data=data, headers=headers)
        r1.raise_for_status()
        self._token = r1.json()['access_token']
        self.r1 = r1

    def normalize_columns(self):

        problematicChars = [",", ";", ":", "{", "}", "(", ")", "=", ">", "<", "."]
        new_cols = {}
        for column in self._df.columns:

            columnName = column.lower()

            for p_char in problematicChars:
                columnName = columnName.replace(p_char, "")

            columnName = columnName.replace(" ", "_")
            columnName = columnName.replace("-", "_")
            columnName = columnName.strip()

            for p_char in problematicChars:
                columnName = columnName.replace(p_char, "")

            new_cols[column] = columnName

        return self._df.rename(columns=new_cols, inplace=True)


    def save_dataset(self, workspace:str, dataset_slug="", replace=False, dataset_name="", locale="en"):

        self._df = self._df.where(pd.notnull(self._df), None)

        for col in self._df.columns:
            if (self._df[col].dtypes == "datetime64[ns]"):
                self._df[col] = self._df[col].astype("str")

        if self._env.lower() == 'dev':
            askdata_url = url_list['BASE_URL_ASKDATA_DEV']
        elif self._env.lower() == 'qa':
            askdata_url = url_list['BASE_URL_ASKDATA_QA']
        elif self._env.lower() == 'prod':
            askdata_url = url_list['BASE_URL_ASKDATA_PROD']

        if "/" in workspace:
            agentSlug = workspace.split("/")[0]
            datasetSlug = workspace.split("/")[1]
        else:
            agentSlug = workspace
            if dataset_slug == "":
                datasetSlug = "parquet_" + uuid.uuid4().__str__()
            else:
                datasetSlug = dataset_slug

        url = askdata_url + "/smartbot/agents/{}/datasets/{}/data_table".format(agentSlug, datasetSlug)

        fields= []
        for column in self._df.columns:
            fields.append({"name": column})

        schema = {"fields": fields}

        body = {
            "data": self._df.to_dict(orient="record"),
            "schema": schema,
            "locale": locale
        }

        if(replace):

            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            response = s.put(url=url, json=body, headers=headers)
            response.raise_for_status()
            dataset = response.json()
            dataset_id = dataset["id"]

        else:
            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            response = s.post(url=url, json=body, headers=headers)
            response.raise_for_status()
            dataset = response.json()
            dataset_id = dataset["id"]

        if(dataset_name!=""):
            url = askdata_url + "/smartbot/agents/"+dataset["agents"][0]+"/datasets/"+dataset_id+"/settings"
            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            response = s.get(url=url, headers=headers)
            response.raise_for_status()
            settings = response.json()

            settings["label"] = dataset_name

            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            response = s.put(url=url,json=settings , headers=headers)
            response.raise_for_status()

        #Execute sync
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        dataset_url = askdata_url + '/smartdataset/datasets/' + dataset_id + '/sync'
        r = requests.post(url=dataset_url, headers=headers)
        r.raise_for_status()


    def join(self, with_query:str, workspace:str, how="inner", on=None, left_on=None, right_on=None, lang="en"):

        if self._env.lower() == 'dev':
            askdata_url = url_list['BASE_URL_ASKDATA_DEV']
        elif self._env.lower() == 'qa':
            askdata_url = url_list['BASE_URL_ASKDATA_QA']
        elif self._env.lower() == 'prod':
            askdata_url = url_list['BASE_URL_ASKDATA_PROD']

        if(on==None and (left_on== None and right_on==None)):
            logging.error("Pleanse insert either 'on' condition or right_on and left_on conditions!")
            return

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        authentication_url = askdata_url + '/smartbot/agents/agentslug/' + workspace

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=authentication_url, headers=headers)
        response.raise_for_status()
        r = response.json()
        agent_id = r["agentId"]

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        authentication_url = askdata_url + '/security/me'

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=authentication_url, headers=headers)
        response.raise_for_status()
        r = response.json()
        self.user_id = r["id"]

        url = askdata_url + "/smartbot/agents/" + agent_id + "/ask"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        body = {
            "message": with_query,
            "language": lang.lower(),
            "userId": self.user_id
        }

        response = s.post(url=url, json=body, headers=headers)
        response.raise_for_status()
        result = response.json()["result"]
        df_query = pd.DataFrame(data=result[0]["attachment"]["body"][0]["details"]["rows"],
                                columns=result[0]["attachment"]["body"][0]["details"]["columns"])

        return self._df.merge(df_query, how, on, left_on, right_on)



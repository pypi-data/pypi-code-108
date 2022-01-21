import requests
import yaml
import os
import pandas as pd
import numpy as np
import logging
import getpass
import json
import uuid
from askdata.insight import Insight
from askdata.channel import Channel
from askdata.catalog import Catalog
from askdata.dataset import Dataset
from askdata.insight_definition import Insight_Definition
from askdata.security import SignUp
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import TYPE_CHECKING
from IPython.core.display import display, HTML

if TYPE_CHECKING:
    from askdata.askdata_client import Askdata

_LOG_FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] - %(asctime)s --> %(message)s"
g_logger = logging.getLogger()
logging.basicConfig(format=_LOG_FORMAT)
g_logger.setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.dirname(__file__))
# retrieving base url
yaml_path = os.path.join(root_dir, '../askdata/askdata_config/base_url.yaml')
with open(yaml_path, 'r') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    url_list = yaml.load(file, Loader=yaml.FullLoader)


class Agent(Insight, Channel, Catalog, Dataset):
    '''
    Agent Object
    '''

    def __init__(self, askdata: 'Askdata', slug='', agent_name='', agent_id=''):

        self.username = askdata.username
        self.userid = askdata.userid
        self._domainlogin = askdata._domainlogin
        self._env = askdata._env
        self._token = askdata._token
        self.df_agents = askdata.agents_dataframe()

        self._headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        if self._env == 'dev':
            self.smart_insight_url = url_list['BASE_URL_INSIGHT_DEV']
        if self._env == 'qa':
            self.smart_insight_url = url_list['BASE_URL_INSIGHT_QA']
        if self._env == 'prod':
            self.smart_insight_url = url_list['BASE_URL_INSIGHT_PROD']

        try:
            if slug != '':
                agent = self.df_agents[self.df_agents['slug'] == slug.lower()]
            elif agent_id != '':
                agent = self.df_agents[self.df_agents['id'] == agent_id]
            else:
                agent = self.df_agents[self.df_agents['name'] == agent_name]

            self._agentId = agent.iloc[0]['id']
            self._domain = agent.iloc[0]['domain']
            self._language = agent.iloc[0]['language']
            self._agent_name = agent.iloc[0]['name']
            if(slug!=''):
                self._slug=slug
            else:
                self._slug = agent.iloc[0]['slug']

        except Exception as ex:
            raise NameError('Agent slug/name/id not exsist or not insert')

        Insight.__init__(self, self._env, self._token)
        Channel.__init__(self, self._env, self._token, self._agentId, self._domain)
        Catalog.__init__(self, self._env, self._token)
        #Dataset.__init__(self, self._env, self._token, self._agentId)

    def __str__(self):
        return '{}'.format(self._agentId)

    def Dataset(self, dataset_slug):
        return Dataset(self._env, self._token, self._agentId, dataset_slug)



    def switch_agent(self):

        data = {
            "agent_id": self._agentId
        }

        if self._env == 'dev':
            self._base_url = url_list['BASE_URL_FEED_DEV']
        if self._env == 'qa':
            self._base_url = url_list['BASE_URL_FEED_QA']
        if self._env == 'prod':
            self._base_url = url_list['BASE_URL_FEED_PROD']

        if self._env == 'dev':
            self._base_url_ch = url_list['BASE_URL_FEED_DEV']
        if self._env == 'qa':
            self._base_url_ch = url_list['BASE_URL_FEED_QA']
        if self._env == 'prod':
            self._base_url_ch = url_list['BASE_URL_FEED_PROD']

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        authentication_url = self._base_url + '/' + self._domain + '/agent/switch'
        r = s.post(url=authentication_url, headers=self._headers, json=data)
        r.raise_for_status()

        return r

    def ask(self, text, payload=''):

        data = {
            "text": text,
            "payload": payload
        }

        if self._env == 'dev':
            request_agent_url = url_list['BASE_URL_FEED_DEV'] + '/' + self._domain + '/agent/' + self._agentId + '/'
        if self._env == 'qa':
            request_agent_url = url_list['BASE_URL_FEED_QA'] + '/' + self._domain + '/agent/' + self._agentId + '/'
        if self._env == 'prod':
            request_agent_url = url_list['BASE_URL_FEED_PROD'] + '/' + self._domain + '/agent/' + self._agentId + '/'

        response = requests.post(url=request_agent_url, headers=self._headers, json=data)
        response.raise_for_status()
        r = response.json()
        # dataframe creation
        df = pd.DataFrame(np.array(r[0]['attachment']['body'][0]['details']['rows']),
                          columns=r[0]['attachment']['body'][0]['details']['columns'])

        return df

    def ask_as_json(self, text, payload=''):

        data = {
            "text": text,
            "payload": payload
        }

        if self._env == 'dev':
            request_agent_url = url_list['BASE_URL_FEED_DEV'] + '/' + self._domain + '/agent/' + self._agentId + '/'
        if self._env == 'qa':
            request_agent_url = url_list['BASE_URL_FEED_QA'] + '/' + self._domain + '/agent/' + self._agentId + '/'
        if self._env == 'prod':
            request_agent_url = url_list['BASE_URL_FEED_PROD'] + '/' + self._domain + '/agent/' + self._agentId + '/'

        response = requests.post(url=request_agent_url, headers=self._headers, json=data)
        response.raise_for_status()
        r = response.json()

        return r

    def dataset(self, slug):
        """
        set in the agent object the properties of specific dataset

        :param slug: str, identification of the dataset
        :return: None
        """
        self._get_info_dataset_by_slug(slug)
        return self


    def query(self, dataset_slug="", fields:list=[], filters=None, sorted_by=None,  dataset_id="", limit=50, offset=0, pivot=[]):
        """
        Pivot columns MUST be contained in field list
        """
        if(fields==[]):
            print("SELECT FIELDS")
            return

        if sorted_by is None:
            sorted_by = []

        if filters is None:
            filters = []

        if(dataset_id=="" and dataset_slug!=""):
            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            url = self._base_url_askdata + '/smartbot/agents/agentslug/' + self._slug + '/datasetslug/' + dataset_slug

            headers = {"Authorization": "Bearer" + " " + self._token}
            response = s.get(url=url, headers=headers)
            response.raise_for_status()
            r = response.json()

            datasetId = r["datasetId"]

        elif(dataset_id!=""):
            datasetId=dataset_id
        else:
            print("SPECIFY A DATASET ID OR SLUG")
            return

        body = {
            "agentId": self._agentId,
            "datasetId": datasetId,
            "fields": fields,
            "sortedBy": sorted_by,
            "filters": filters,
            "limit": limit,
            "offset": offset,
            "pivot": pivot
        }

        url = self.smart_insight_url + "/composed_queries/sdk"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=url, json=body, headers=headers)
        response.raise_for_status()

        qc_id = response.json()["id"]

        preview_url = self.smart_insight_url + "/composed_queries/" + qc_id + "/preview"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=preview_url, json={}, headers=headers)
        response.raise_for_status()

        r = response.json()
        codes = []
        columns = []
        for col in r["schema"]:
            codes.append(col["code"])
            if col["name"] != '':
                columns.append(col["name"])
            else:
                columns.append(col["code"])
        df = pd.DataFrame(columns=codes, data=r["data"])
        df.columns = columns
        return df


    def update_dataset_name(self, dataset_slug, dataset_name):

        body = {"name": dataset_name}

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_askdata + '/smartdataset/datasets/' + dataset_slug + '/sdk'
        logging.info("AUTH URL {}".format(authentication_url))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        response = s.put(url=authentication_url, json=body, headers=headers)
        response.raise_for_status()

    def create_parquet_dataset(self, agent_slug, dataset_slug, file_path):

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_askdata + '/smartbot/agents/' + agent_slug + '/datasets/' + dataset_slug + '/parquet'
        logging.info("AUTH URL {}".format(authentication_url))
        file = {'file': open(file_path, 'rb')}
        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=authentication_url, files=file, headers=headers)
        response.raise_for_status()
        r = response.json()


    def update_parquet_dataset(self, agent_slug, dataset_id, file_path, strategy):

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_askdata + '/smartbot/agents/' + agent_slug + '/datasets/' + dataset_id + '/parquet?strategy=' + strategy
        logging.info("AUTH URL {}".format(authentication_url))
        file = {'file': open(file_path, 'rb')}
        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.put(url=authentication_url, files=file, headers=headers)
        response.raise_for_status()
        r = response.json()

    def _load_dataset(self, dataset_id):

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_askdata + '/smartdataset/datasets/' + dataset_id + '/grid/data'
        logging.info("AUTH URL {}".format(authentication_url))

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=authentication_url, headers=headers)
        response.raise_for_status()
        r = response.json()
        return pd.DataFrame(r['payload']['data'])

    def get_dataset_by_slug(self, agent_slug, slug: str):
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        try:
            authentication_url = self._base_url_askdata + '/smartbot/agents/agentslug/' + agent_slug + '/datasetslug/' + slug
            logging.info("AUTH URL {}".format(authentication_url))

            headers = {"Authorization": "Bearer" + " " + self._token}
            response = s.get(url=authentication_url, headers=headers)
            response.raise_for_status()
            r = response.json()
            return r["datasetId"]
        except:
            return None

    def __update_dataset_icon(self, dataset_id, icon_url):

        url = self._base_url_askdata + "/smartdataset/datasets/" + dataset_id + "/settings"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        logging.info("AUTH URL {}".format(url))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        response = s.get(url=url, headers=headers)
        response.raise_for_status()

        settings = response.json()

        settings["icon"] = icon_url

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        logging.info("AUTH URL {}".format(url))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        response = s.put(url=url, json=settings, headers=headers)
        response.raise_for_status()

    def create_dataset(self, dataframe: pd.DataFrame, dataset_name: str, slug: str, icon_url=None,
                       settings: dict = None):

        for col in dataframe.columns:
            if (dataframe[col].dtypes == "datetime64[ns]"):
                dataframe[col] = dataframe[col].astype("str")

        body = {"label": dataset_name, "rows": dataframe.to_dict(orient="record")}

        settings_list = []
        if (settings != None):
            for key in settings.keys():
                settings[key]["column_name"] = key
                settings_list.append(settings[key])
            body["settings"] = settings_list

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = self._base_url_askdata + '/smartbot/agents/' + self._agentId + '/datasets/' + slug + '/sdk'
        logging.info("AUTH URL {}".format(url))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        response = s.post(url=url, json=body, headers=headers)
        response.raise_for_status()

        dataset_id = response.json()["id"]

        if (icon_url != None):
            self.__update_dataset_icon(dataset_id, icon_url)

    def update_dataset(self, dataframe: pd.DataFrame, dataset_name: str, slug: str, icon_url=None,
                       settings: dict = None):

        for col in dataframe.columns:
            if (dataframe[col].dtypes == "datetime64[ns]"):
                dataframe[col] = dataframe[col].astype("str")

        body = {"label": dataset_name, "rows": dataframe.to_dict(orient="records")}

        settings_list = []
        if (settings != None):
            for key in settings.keys():
                settings[key]["column_name"] = key
                settings_list.append(settings[key])
            body["settings"] = settings_list

        s = requests.Session()

        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = self._base_url_askdata + '/smartbot/agents/' + self._agentId + '/datasets/' + slug + '/sdk'
        logging.info("AUTH URL {}".format(url))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        response = s.put(url=url, json=body, headers=headers)

        response.raise_for_status()
        dataset_id = response.json()["id"]

        if (icon_url != None):
            self.__update_dataset_icon(dataset_id, icon_url)


    def check_dataset_columns(self, dataframe: pd.DataFrame, dataset_id):

        body = dataframe.to_dict(orient="record")

        url = self._base_url_askdata + '/smartdataset/datasets/'+dataset_id+'/sdk/check'

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        logging.info("AUTH URL {}".format(url))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        response = s.post(url=url, json=body, headers=headers)
        response.raise_for_status()
        r = response.json()

        if(r["hasDifference"]):
            for differece in r["differences"]:
                logging.info("Column {} is being {}".format(differece["columnName"], differece["differenceType"]))
        return r["hasDifference"]

    '''La prima chiave è la stringa colonna del dataframe. Per ogni chiave ho dei setting:
    name stringa
    type(dimension o measure)
    isDate booleano
    synonyms: [] array di stringhe
    dateFormat(pattern della data)
    numberFormat
    defaultAggregation(sum, avg..)

    {
        "column_name": {
            "name": "column_name",
            "type": "Dimension",
            "isDate": False,
            "synonyms": [],
            "dateFormat",
            "numberFormat": "",
            "defaultAggregation": "sum"
        }
    }
    '''
    def create_or_replace_dataset(self, dataframe: pd.DataFrame, dataset_name: str, slug: str, icon_url=None,
                                  settings: dict = None):
        # Check if dataset exists
        dataset_id = self.get_dataset_by_slug(self._slug, slug)

        dataframe = dataframe.replace({np.nan: None})

        if(dataset_id != None):
            #If it exists update it
            self.update_dataset(dataframe, dataset_name, slug, icon_url, settings)
        else:
            # If not exists create a new one
            self.create_dataset(dataframe, dataset_name, slug, icon_url, settings)


    def delete_dataset(self, slug='', dataset_id=''):

        if slug != '':
            self._get_info_dataset_by_slug(slug)
            self._delete_dataset(self._dataset_id)
            logging.info("---- dataset '{}' deleted ----- ".format(slug))
        elif dataset_id != '' and slug == '':
            self._delete_dataset(dataset_id)
            logging.info("---- dataset '{}' deleted ----- ".format(dataset_id))
        else:
            raise Exception('Please give either a dataset id or a dataset slug')

    def create_datacard(self, channel_name: str, title: str, search: str = "", slug: str = None, skin_code:str = None, replace: bool = False):

        if (replace == True and slug != None):
            try:
                datacard = self.get_datacard(slug)
                datacard.delete()
            except:
                pass
        elif (replace == True and slug != None):
            print("Please specify a datacard slug to replace!")
            return

        channel = self.get_channel(channel_name)
        if channel is not None:
            channel_id = channel["id"]
        else:
            channel_id = self.create_channel(channel_name)

        body = {
            "agentId": self._agentId,
            "channelId": channel_id,
            "name": title,
            "slug": slug
        }

        if skin_code is not None:
            body["ui"]= {"skin" : skin_code}

        if self._env == 'dev':
            smart_insight_url = url_list['BASE_URL_INSIGHT_DEV']
        if self._env == 'qa':
            smart_insight_url = url_list['BASE_URL_INSIGHT_QA']
        if self._env == 'prod':
            smart_insight_url = url_list['BASE_URL_INSIGHT_PROD']

        url = smart_insight_url + '/definitions'

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
        definition = response.json()

        if (search != ""):
            body_query = {"nl": search, "language": "en"}

            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            query_url = smart_insight_url + '/definitions/' + definition["id"] + '/nl_queries/' + \
                        definition["components"][0]["id"] + '/nl'
            logging.info("QUERY URL {}".format(query_url))
            r = s.put(url=query_url, json=body_query, headers=headers)

        logging.info("DATACARD {} CREATED".format(slug))

        return Insight_Definition(self._env, self._token, self._slug, definition)

    def get_datacard(self, slug):

        url = self.smart_insight_url + "/definitions/agent/" + self._agentId + "/slug/" + slug

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        r = s.get(url=url, headers=self._headers)
        r.raise_for_status()

        definition = r.json()
        return Insight_Definition(self._env, self._token, self._slug, definition)

    def create_channel(self, name, icon='https://storage.googleapis.com/askdata/smartfeed/icons/Channel@2x.png',
                       visibility='PRIVATE'):

        data = {
            "userId": self.userid,
            "name": name,
            "icon": icon,
            "agentId": self._agentId,
            "visibility": visibility,
            "code": name,
            "autofollow": True
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_ch + '/channels'
        r = s.post(url=authentication_url, headers=self._headers, json=data)
        r.raise_for_status()
        return r.json()['id']

    def delete_channel(self, channel_slug):
        channel_id = self.get_channel(channel_slug)["id"]
        url = "{}/smartfeed/channels/{}".format(self._base_url_askdata, channel_id)

        r = requests.delete(url=url, headers=self._headers)
        r.raise_for_status()
        return r

    def execute_dataset_sync(self, dataset_slug):

        dataset_id = self.get_dataset_by_slug(self._slug, dataset_slug)

        dataset_url = self._base_url_askdata + '/smartdataset/datasets/' + dataset_id + '/sync'
        r = requests.post(url=dataset_url, headers=self._headers)
        r.raise_for_status()
        return r


    def __get_user_by_email(self, user_email):

        url = self._base_url_askdata + "/smartbot/share/principals?q=" + user_email
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        r = s.get(url=url, headers=self._headers)
        r.raise_for_status()
        if (r != None and r.json() != []):
            user_id = r.json()[0]["id"]
            return user_id
        else:
            print("Please insert valid email")
            return None

    '''
    role: VIEW/EDIT
    '''
    def add_user_to_workspace(self, user_email, role="VIEW"):
        user_id = self.__get_user_by_email(user_email)

        data = {
            "principals": [
                {
                    "id": user_id,
                    "type": "USER"
                }
            ],
            "permission": role
        }

        url = self._base_url_askdata+"/smartbot/agents/{}/share/entries".format(self._agentId)
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        r = s.post(url=url, headers=self._headers, json=data)
        r.raise_for_status()


    '''
    role: FOLLOWER/ADMIN
    '''
    def add_user_to_channel(self, channel_slug, user_email, role="FOLLOWER"):

        user_id = self.__get_user_by_email(user_email)

        channel_id = self.get_channel(channel_slug)["id"]
        self.__add_user_to_ch(channel_id, user_id, role)

    def __add_user_to_ch(self, channel_id, user_id, role="FOLLOWER"):

        data = {
            "userId":user_id,
            "role":role,
            "mute":"none"
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_askdata + "/smartfeed/channels/{}/users".format(channel_id)
        r = s.post(url=authentication_url, headers=self._headers, json=data)
        r.raise_for_status()
        #return r


    def get_channel(self, channel_code):

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = self._base_url_ch + '/channels?agentId=' + self._agentId + '&slug=' + channel_code
        r = s.get(url=url, headers=self._headers)
        r.raise_for_status()
        if (r != None and r.json() != []):
            return r.json()[0]
        else:
            return None

    def get_dataset_slug_from_id(self, dataset_id: str) -> str:
        """
        get dataset slug by the dataset id instantiated with slug
        :param dataset_id: str
        :return: slug: str
        """

        list_dataset = self.list_datasets()

        if list_dataset[list_dataset['id'] == dataset_id].empty:
            raise Exception('The dataset with id: {} not exist'.format(dataset_id))
        else:
            slug = list_dataset[list_dataset['id'] == dataset_id].loc[:, 'slug'].item()

        return slug

    def list_datasets(self):

        if self._env == 'dev':
            self._base_url_dataset = url_list['BASE_URL_DATASET_DEV']
        elif self._env == 'qa':
            self._base_url_dataset = url_list['BASE_URL_DATASET_QA']
        elif self._env == 'prod':
            self._base_url_dataset = url_list['BASE_URL_DATASET_PROD']

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        dataset_url = self._base_url_dataset + '/datasets?agentId=' + self._agentId
        response = s.get(url=dataset_url, headers=self._headers)
        response.raise_for_status()
        r = response.json()
        r_df = pd.DataFrame(r)

        try:
            if r_df.empty:
                raise Exception('No datasets in the agent {}'.format(self._agentId))
            else:
                datasets_df = r_df.loc[:, ['id', 'domain', 'type', 'code', 'name', 'slug', 'description', 'createdBy', 'isActive',
                                     'accessType', 'icon', 'version', 'syncCount', 'visible', 'public', 'createdAt']]
        except Exception as e:
            datasets_df = r_df
            logging.info(e)

        return datasets_df


class Askdata(SignUp):
    '''
    Authentication Object
    '''

    def __init__(self, username='', password='', domainlogin='askdata', env='prod', token=''):

        with requests.Session() as s:

            self._token = token
            self._domainlogin = domainlogin.upper()
            self._env = env.lower()

            if self._env == 'dev':
                self.base_url_security = url_list['BASE_URL_SECURITY_DEV']
            elif self._env == 'qa':
                self.base_url_security = url_list['BASE_URL_SECURITY_QA']
            elif self._env == 'prod':
                self.base_url_security = url_list['BASE_URL_SECURITY_PROD']

            if self._env == 'dev':
                self.base_url = url_list['BASE_URL_ASKDATA_DEV']
            elif self._env == 'qa':
                self.base_url = url_list['BASE_URL_ASKDATA_QA']
            elif self._env == 'prod':
                self.base_url = url_list['BASE_URL_ASKDATA_PROD']

            if token == '':

                if username == '':
                    # add control email like
                    username = input('Askdata Username: ')
                if password == '':
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

                authentication_url = self.base_url_security + '/domain/' + self._domainlogin.lower() + '/oauth/token'

                # request token for the user
                r1 = s.post(url=authentication_url, data=data, headers=headers)
                r1.raise_for_status()
                self._token = r1.json()['access_token']
                self.r1 = r1

            authentication_url_userid = self.base_url_security + '/me'
            self._headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }

            # request userId of the user
            r_userid = s.get(url=authentication_url_userid, headers=self._headers)
            r_userid.raise_for_status()
            self.userid = r_userid.json()['id']
            self.username = r_userid.json()['userName']

    def agent(self, slug="", agent_id='') -> 'Agent':
        # Agent.__init__(self, self, slug=slug)
        return Agent(self, slug=slug, agent_id=agent_id)

    def get_token(self, username, password):
        return self._token

    def normalize_columns(self, df:pd.DataFrame):

        from askdata import integration as ig
        return ig.normalize_columns(df)

    def save_dataset(self, df:pd.DataFrame, workspace: str, dataset_slug="", replace=True, dataset_name="", locale="en", skip_import_values=False):


        for col in df.columns:
            if (df[col].dtypes == "datetime64[ns]"):
                df[col] = df[col].astype("str")

        df = df.where(pd.notnull(df), None)


        if "/" in workspace:
            agentSlug = workspace.split("/")[0]
            datasetSlug = workspace.split("/")[1]
        else:
            agentSlug = workspace
            if dataset_slug == "":
                datasetSlug = "parquet_" + uuid.uuid4().__str__()
            else:
                datasetSlug = dataset_slug

        url = self.base_url + "/smartbot/agents/{}/datasets/{}/data_table".format(agentSlug, datasetSlug)

        fields = []
        for column in df.columns:
            fields.append({"name": column})

        schema = {"fields": fields}

        body = {
            "data": df.to_dict(orient="record"),
            "schema": schema,
            "locale": locale,
            "defaultImportValues": (not skip_import_values)
        }

        if (replace):

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

        if (dataset_name != ""):
            url = self.base_url + "/smartbot/agents/" + dataset["agents"][0] + "/datasets/" + dataset_id + "/settings"
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
            response = s.put(url=url, json=settings, headers=headers)
            response.raise_for_status()

            # Execute sync
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            dataset_url = self.base_url + '/smartdataset/datasets/' + dataset_id + '/sync'
            r = requests.post(url=dataset_url, headers=headers)
            r.raise_for_status()

    def delete_agent(self, agent_slug):
        agent = self.agents_dataframe()[self.agents_dataframe()['slug'] == agent_slug.lower()]
        url = self.base_url + "/smartbot/agents/"+ agent.iloc[0]['id']
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.delete(url=url, headers=headers)
        r.raise_for_status()

    def join(self, df:pd.DataFrame, with_query:str, workspace:str, how="inner", on=None, left_on=None, right_on=None, lang="en"):

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        authentication_url = self.base_url + '/smartbot/agents/agentslug/' + workspace

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=authentication_url, headers=headers)
        response.raise_for_status()
        r = response.json()
        agent_id = r["agentId"]

        url = self.base_url + "/smartbot/agents/"+agent_id+"/ask"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        body = {
            "message": with_query,
            "language": lang.lower(),
            "userId": self.userid
        }

        response = s.post(url=url, json=body, headers=self._headers)
        response.raise_for_status()
        result = response.json()["result"]
        df_query = pd.DataFrame(data=result[0]["attachment"]["body"][0]["details"]["rows"], columns=result[0]["attachment"]["body"][0]["details"]["columns"])

        if (on == None and (left_on == None and right_on == None)):
            join_conditions = self.__get_join_info(df, df_query)
            left_conditions = []
            right_conditions = []
            for condition in join_conditions:
                left_conditions.append(condition["left_on"])
                right_conditions.append(condition["right_on"])
            #left_conditions = self.__retrieve_og_columns(left_conditions, df)
            #right_conditions = self.__retrieve_og_columns(right_conditions, df_query)
            return df.merge(df_query, how, None, left_conditions, right_conditions)

        return df.merge(df_query, how, on, left_on, right_on)

    def load_dataset(self, workspace_slug, dataset_slug, logs=True):
        all_fields = list(self.get_columns(workspace=workspace_slug, dataset=dataset_slug)["code"])
        limit = 1000
        df = self.query(workspace=workspace_slug, dataset=dataset_slug, fields=all_fields, limit=limit)
        if(len(df.index) < 1000):
            print("Downloaded {} rows".format(len(df.index)))
            return df
        else:
            final_df = df
            while(len(df.index) == 1000):
                df = self.query(workspace=workspace_slug, dataset=dataset_slug, fields=all_fields, limit=1000, offset=limit)
                final_df = final_df.append(df)
                if(limit%10000 == 0 and logs):
                    print("Downloaded {} rows".format(limit))

                limit+=1000
            print("Downloaded {} rows".format(len(final_df.index)))
            return final_df

    def __retrieve_og_columns(self, conditions:list, df:pd.DataFrame):
        formatted_conditions = []
        for condition in conditions:
            for column in df.columns:
                if condition in column.lower():
                    formatted_conditions.append(column)

        return formatted_conditions

    def get_join_info(self, df1: pd.DataFrame, df2: pd.DataFrame):
        return self.__get_join_info(df1, df2)

    def __get_join_info(self, df1:pd.DataFrame, df2:pd.DataFrame):

        columns = []
        for field in json.loads(df1.to_json(orient="table", index=False))["schema"]["fields"]:
            field["label"] = field.pop("name")
            field["type"] = self.__choose_type(field.pop("type"))
            columns.append(field)


        columns2 = []
        for field in json.loads(df2.to_json(orient="table", index=False))["schema"]["fields"]:
            field["label"] = field.pop("name")
            field["type"] = self.__choose_type(field.pop("type"))
            columns2.append(field)


        table_left = {
            "columns": columns,
            "values": json.loads(df1.to_json(orient="values"))[:5]
        }
        table_right = {
            "columns": columns2,
            "values": json.loads(df2.to_json(orient="values"))[:5]
        }
        tables = {
            "tables": {
                "table_left": table_left,
                "table_right": table_right
            }
        }
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = self.base_url + '/cfc/smartjoin'

        r = s.post(url=url, headers=self._headers, json=tables)
        r.raise_for_status()

        try:
            return r.json()["join_list"]
        except:
            logging.error(r.json())

    def __choose_type(self, var):
        if "int" in var or "num" in var or "real" in var or "double" in var or "decimal" in var or "float" in var:
            return "numeric"
        elif "text" in var or "varchar" in var or "char" in var or "default" in var:
            return "string"
        elif "date" in var or "year" in var:
            return "datetime"
        elif "time" in var:
            return "timestamp"
        elif "bool" in var or "bit" in var:
            return "bool"
        elif "blob" in var:
            return "blob"
        else:
            return var

    def get_columns(self, dataset, workspace=''):

        if(workspace==''):
            if('/' in dataset):
                workspace=dataset.split("/")[0]
                slug = dataset.split("/")[1]
        else:
            slug=dataset

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = self.base_url + '/smartbot/agents/agentslug/' + workspace + '/datasetslug/' + slug

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=url, headers=headers)
        response.raise_for_status()
        r = response.json()
        agent_id = r["agentId"]
        dataset_id = r["datasetId"]

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = self.base_url + '/smartdataset/datasets/' + dataset_id + '/measures'

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=url, headers=headers)
        response.raise_for_status()
        measures = response.json()
        columns=[]
        for measure in measures:
            columns.append({
                "code": measure["code"],
                "name": measure["name"],
                "type": "MEASURE",
                "internalType": measure["schemaMetaData"]["dataType"]
            })
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = self.base_url + '/smartdataset/datasets/' + dataset_id + '/entityTypes'

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=url, headers=headers)
        response.raise_for_status()
        entityTypes = response.json()

        for entityType in entityTypes:
            columns.append({
                "code": entityType["code"],
                "name": entityType["name"],
                "type": "ENTITY_TYPE",
                "internalType": entityType["schemaMetaData"]["dataType"]
            })
        return pd.DataFrame(data=columns)

    def query(self, workspace='', dataset='', fields:list=[], filters=None, sorted_by=None, limit=50, offset=0, pivot=[]):

        if (workspace == ''):
            if ('/' in dataset):
                workspace = dataset.split("/")[0]
                dataset = dataset.split("/")[1]



        agent = self.agent(slug=workspace)
        return agent.query(dataset, fields, filters, sorted_by, limit=limit, offset=offset, pivot=pivot)


    def get(self, query, workspace='', dataset='', lang="en", fields:list=[], filters=None, sorted_by=None, get_raw_data=False):


        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        if(workspace == '' and dataset==''):
            logging.error("Please insert a dataset or a workspace")
        elif(workspace != '' and dataset==''):
            dataset_id = ''
            try:
                authentication_url = self.base_url+ '/smartbot/agents/agentslug/' + workspace

                headers = {"Authorization": "Bearer" + " " + self._token}
                response = s.get(url=authentication_url, headers=headers)
                response.raise_for_status()
                r = response.json()
                agent_id = r["agentId"]
            except Exception as e:
                logging.error("{}".format(e.__str__()))
                logging.error("{} workspace not found".format(workspace))
                return None
        else:
            # Get agent_id and dataset_id
            try:
                workspace=dataset.split("/")[0]
                slug=dataset.split("/")[1]

                authentication_url = self.base_url+'/smartbot/agents/agentslug/'+workspace + '/datasetslug/' + slug

                headers = {"Authorization": "Bearer" + " " + self._token}
                response = s.get(url=authentication_url, headers=headers)
                response.raise_for_status()
                r = response.json()
                agent_id = r["agentId"]
                dataset_id = r["datasetId"]
            except Exception as e:
                logging.error("{}".format(e.__str__()))
                logging.error("{} workspace not found".format(workspace))
                return None


        url = self.base_url + "/smartbot/agent-slugs/"+workspace+"/v2/ask"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        body = {
            "message": query,
            "language": lang.lower(),
            "userId": self.userid,
            "fields": fields,
            "filters": filters,
            "sorting": sorted_by,
            "getRawData": get_raw_data
        }

        response = s.post(url=url, json=body, headers=self._headers)
        response.raise_for_status()
        result = response.json()["cards"]
        try:
            if(dataset_id!=''):
                filtered_result = []
                for r in result:
                    if(r["attachment"]["body"][0]["details"]["datasetId"]==dataset_id):
                        filtered_result.append(r)
            else:
                filtered_result = result

            if self._env == 'dev':
                app_url = url_list['BASE_URL_APP_DEV']
            elif self._env == 'qa':
                app_url = url_list['BASE_URL_APP_QA']
            elif self._env == 'prod':
                app_url = url_list['BASE_URL_APP_PROD']

            url_1 = app_url + "/" + workspace+"/"+filtered_result[0]["attachment"]["body"][0]["details"]["datasetSlug"]
            display(HTML('<p>{} from the dataset: {} / {} : (<a href="{}" target="_blank">{}</a>) <- Use this source</p>'.format(self.extract_fields(filtered_result[0]["attachment"]["body"][0]["details"]["columns"]), workspace, filtered_result[0]["attachment"]["body"][0]["details"]["datasetName"], url_1, url_1)))
            if(len(filtered_result[0]["attachment"]["body"])>1):
                display(HTML("<p>Filtered by: {}</p>".format(filtered_result[0]["attachment"]["body"][1]["details"]["text"])))
            if(len(filtered_result)>1):
                display(HTML("<p>{} Alternatives:</p>".format(len(filtered_result)-1)))
                for r in filtered_result[1:]:
                    url_i = app_url + "/" + workspace + "/" + r["attachment"]["body"][0]["details"]["datasetSlug"]
                    display(HTML('<p>     {} from the dataset: {} / {} ((<a href="{}" target="_blank">{}</a>)) <- Use this source</p>'.format(self.extract_fields(r["attachment"]["body"][0]["details"]["columns"]), workspace, r["attachment"]["body"][0]["details"]["datasetName"], url_i, url_i)))
            if get_raw_data:
                df = pd.DataFrame(data=filtered_result[0]["attachment"]["body"][0]["details"]["rawData"], columns=filtered_result[0]["attachment"]["body"][0]["details"]["columns"])
            else:
                df = pd.DataFrame(data=filtered_result[0]["attachment"]["body"][0]["details"]["rows"], columns=filtered_result[0]["attachment"]["body"][0]["details"]["columns"])
            return df
        except Exception as e:
            logging.error("Query did not produce any result")
            logging.error(e.__str__())

    def load_agents(self):

        if self._env == 'dev':
            authentication_url = url_list['BASE_URL_AGENT_DEV']

        if self._env == 'qa':
            authentication_url = url_list['BASE_URL_AGENT_QA']

        if self._env == 'prod':
            authentication_url = url_list['BASE_URL_AGENT_PROD']

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        # request of all agents of the user/token
        response = s.get(url=authentication_url, headers=self._headers)
        response.raise_for_status()

        return response.json()

    def agents_dataframe(self):
        return pd.DataFrame(self.load_agents())

    def signup_user(self, username, password, firstname='-', secondname='-', title='-'):
        response = super().signup_user(username, password, firstname, secondname, title)
        return response


    def create_agent(self, agent_name):

        data = {
            "name": agent_name,
            "language": "en"
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        authentication_url = self.base_url + '/smartbot/agents'
        r = s.post(url=authentication_url, headers=self._headers, json=data)
        r.raise_for_status()

        return r

    def extract_fields(self, fields:list)->str:
        column_names = ""
        for field in fields:
            column_names+=(field+ " , ")
        return column_names[:-3]

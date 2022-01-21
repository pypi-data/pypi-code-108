import requests
import yaml
import os
import logging
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import TYPE_CHECKING
from IPython.display import Image, display, HTML
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

class Insight_Definition:


    def __init__(self, env:str, token, agent_slug, definition):

        self.definition_id = definition["id"]
        self.agent_id = definition["agentId"]
        self.agent_slug = agent_slug
        self.collection_id = definition["collectionId"]
        self.name = definition["name"]
        self.slug = definition["slug"]
        self.icon = definition["icon"]
        self.components: list = definition["components"]
        self._env = env
        self._token = token

        if env.lower() == 'dev':
            self._base_url_askdata = url_list['BASE_URL_ASKDATA_DEV']
            self.smart_insight_url = url_list['BASE_URL_INSIGHT_DEV']
            self.app_url = "https://app-dev.askdata.com"
        if env.lower() == 'qa':
            self._base_url_askdata = url_list['BASE_URL_ASKDATA_QA']
            self.smart_insight_url = url_list['BASE_URL_INSIGHT_QA']
            self.app_url = "https://app-qa.askdata.com"
        if env.lower() == 'prod':
            self._base_url_askdata = url_list['BASE_URL_ASKDATA_PROD']
            self.smart_insight_url = url_list['BASE_URL_INSIGHT_PROD']
            self.app_url = "https://app.askdata.com"


    def add_skin(self, skin_code:str):
        body = {

            "name": self.name,
            "slug": self.slug,
            "ui": {
                "skin": skin_code
            }
        }

        url = self.smart_insight_url+"/definitions/"+self.definition_id

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

    def add_widget(self, widget_type: str, query_ids:list=[], settings:dict={}, values:dict={}, texts:dict={}, charts:list=[]):
        position = (len(self.components))
        widget_id = self.__create_widget(position, widget_type)
        if(query_ids!=[]):
            self.edit_widget(widget_id, widget_type,query_ids, settings, values, texts, charts)
        return widget_id

    def edit_widget(self, widget_id, widget_type: str, query_ids:list, field_codes:dict, values:dict={}, texts:dict={}, charts:list=[]):

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/widgets/"+widget_id

        columns = self.__get_columns(query_ids)

        settings = {}
        for field in field_codes.keys():
            found = False
            for column in columns:
                if(column["code"] in field_codes[field]):
                    for query in query_ids:
                        if(str(field_codes[field]).startswith(query)):
                           if(str(column["id"]).startswith(query)):
                               settings[field + "_id"] = column["id"]
                               found = True
                               break
                           else:
                               continue
                        else:
                            found = True
                            settings[field + "_id"] = column["id"]
                            break

        for key in values.keys():
            settings[key + "_id"] = values[key]

        body = {
            "id" : widget_id,
            "type": "widget",
            "name": "Widget",
            "customName": False,
            "dependsOn": [],
            "widgetType": widget_type,
            "queryIds": query_ids,
            "settings": settings,
            "texts": texts,
            "charts": charts,
            "valid": True,
            "queryComponent": False
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

    def __get_columns(self, query_ids) -> list:

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/queries/columns"
        body = {"queryIds": query_ids}
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.post(url=url, json=body, headers=headers)
        r.raise_for_status()
        return r.json()

    def display_card_img(self):
        display(Image(data=self.__get_card_img()))


    def download_card_img(self, image_path:str):
        with open(image_path, 'wb') as f:
            f.write(self.__get_card_img())


    def get_card_url(self):
        return self.__get_card__url()


    def __get_card__url(self):

        url = self.app_url + "/"+self.agent_slug+"/card/" + self.slug
        return url

    def preview(self):

        url = self.app_url+"/card/"+self.__get_card_id()
        display(HTML('<iframe src="'+url+'" height="300" width="300" title="'+self.slug+'"></iframe>'))

    def __get_card_id(self):

        url = self._base_url_askdata+"/smartfeed/agents/"+self.agent_id+"/insights/insightslug/"+self.slug
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.get(url=url, headers=headers)
        r.raise_for_status()
        cards = r.json()
        for card in cards:
            try:
                if(card["insightSlug"]==self.slug):
                    return card["id"]
            except KeyError:
                pass

        logging.error("Card not found")
        return None

    def __get_card_img(self):

        card_id = self.__get_card_id()

        if(card_id != None):

            url = self._base_url_askdata+"/smartinsight/insights/"+card_id+"/data?type=image"
            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            r = s.get(url=url, headers=headers)
            r.raise_for_status()
            return r.content
        else:
            return None


    def __create_widget(self, position, widget_type):

        body = {"type": "widget", "position": position, "widgetType": widget_type}

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        query_url = self.smart_insight_url + '/definitions/' + self.definition_id + '/components/'
        #logging.info("URL {}".format(query_url))
        r = s.post(url=query_url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]
        return self.components[position]["id"]

    def add_table(self, query="", columns=[]):

        position = (len(self.components))
        body = {"type": "table", "position": position}
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        query_url = self.smart_insight_url + '/definitions/' + self.definition_id + '/components/'
        r = s.post(url=query_url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

        if(query != "" and columns!=[]):
            self.edit_table(self.components[position]["id"], query, columns)

        return self.components[position]["id"]


    def edit_table(self, table_id, query="", columns=[]):

        url = self.smart_insight_url + "/definitions/" + self.definition_id + "/tables/"+ table_id

        body = {
            "id": table_id,
            "type": "table",
            "name": "Table",
            "customName":False,
            "dependsOn": ["q1"],
            "queryId": query,
            "columns": columns,
            "maxResults":50,
            "valid":True,
            "queryComponent":False
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]


    def get_result_set(self, query_id):

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/queries/resultset/"+query_id

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.get(url=url, headers=headers)
        r.raise_for_status()
        response = r.json()
        columns = []
        for column in response["schema"]:
            columns.append(column["name"])

        result_set = {}

        for i in range(len(columns)):
            row = []
            for temp_row in response["data"]:
                row.append(temp_row["cells"][i]["rawValue"])
            result_set[columns[i]] = row

        return pd.DataFrame(data=result_set)


    def add_chart(self, type:str, query:str, params:list, title = "Chart"):
        position = (len(self.components))
        body = {"type": "chart", "position": position}

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        query_url = self.smart_insight_url + '/definitions/' + self.definition_id + '/components/'
        #logging.info("URL {}".format(query_url))
        r = s.post(url=query_url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

        self.edit_chart(self.components[position]["id"], type, query, params, title)


        return self.components[position]["id"]


    def edit_chart(self, chart_id, chart_type:str, query:str, params, title = "Chart"):

        '''url = self._base_url_askdata+"/smartinsight/definitions/"+self.definition_id+"/queries/"+query.lower()+"/columns"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.get(url=url, headers=headers)
        r.raise_for_status()
        columns = r.json()

        while(columns == []):
            url = self._base_url_askdata + "/smartinsight/definitions/" + self.definition_id + "/queries/" + query.lower() + "/columns"

            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            r = s.get(url=url, headers=headers)
            r.raise_for_status()
            columns = r.json()
        '''

        qc = self.get_component(query)

        url_preview = self.smart_insight_url+"/composed_queries/"+qc["settings"]["qc"]+"/preview?limit=100"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=url_preview, json={}, headers=headers)
        response.raise_for_status()
        r = response.json()
        columns = r["schema"]

        upper_params = []
        for param in params:
            for column in columns:
                if((param in column["code"]) or (param == column["code"])):
                    upper_params.append(column["code"])

        url = self.smart_insight_url + "/definitions/" + self.definition_id + "/charts/" + chart_id


        body = {
            "chartType": chart_type.upper(),
            "customName": False,
            "dependsOn": [],
            "id": chart_id,
            "name": title,
            "params": upper_params,
            "queryComponent": False,
            "queryId": query,
            "type": "chart",
            "valid": True
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]


    def add_list(self, query_id, title_parameter, description_parameter, action_enabled, action_label,
                  action_url, max_results,list_name="List"):
        position = (len(self.components))
        list_id = self.add_component(type="list", position=position)
        self.edit_list(list_id, query_id, title_parameter,
                       description_parameter, action_enabled, action_label, action_url, max_results, list_name)
        return list_id


    def edit_list(self, list_id, query_id, title_parameter, description_parameter, action_enabled, action_label,
                  action_url, max_results,list_name="List"):

        url = self.smart_insight_url + "/definitions/" + self.definition_id + "/lists/" + list_id
        body = {
            "id":list_id,
            "type":"list",
            "name":list_name,
            "customName":True,
            "dependsOn":[],
            "queryId":query_id,
            "title":title_parameter,
            "description":description_parameter,
            "actionEnabled": action_enabled,
            "actionLabel": action_label,
            "actionUrl":action_url,
            "maxResults":max_results,
            "valid":True,
            "queryComponent":False
        }


        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

    def add_data(self, df:pd.DataFrame, parameters_settings:list=[]):
        position = (len(self.components))
        data_id = self.add_component("data", position)
        self.edit_data(data_id, df)
        if(parameters_settings!=[]):
            for i in range(len(parameters_settings)):
               self.edit_data_entity(data_id, i, parameters_settings[i])
        return data_id


    def add_join_to_qc(self, qc_id, new_dataset_slug, new_fields, left_on:list, right_on:list, type:str ,filters:list=[], sorted_by= None, limit=50, offset=0, pivot=[]):

        new_qc = self.create_qc(new_dataset_slug, new_fields, filters, sorted_by, limit= limit, pivot=pivot, offset=offset)

        url = self.smart_insight_url+"/composed_queries/{}".format(qc_id)

        qc = self.get_qc(qc_id)
        qc = qc["settings"]["qcSettings"]
        qc["joinedSmartQuery"]= {
            "smartQueryId": new_qc["id"]
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=qc, headers=headers)
        r.raise_for_status()
        response = r.json()

        right_fields = []
        left_fields = []
        for field in new_qc["fields"]:
            if field["column"] in right_on:
                right_fields.append(field)
        for field in qc["fields"]:
            if field["column"] in left_on:
                left_fields.append(field)

        joinable_fields = response["joinedSmartQuery"]["joinableFields"]

        qc["joinedSmartQuery"]["smartQueryId"] = new_qc["id"]
        qc["joinedSmartQuery"]["joinType"] = type.upper()
        qc["joinedSmartQuery"]["leftFields"] = left_fields
        qc["joinedSmartQuery"]["rightFields"] = right_fields
        qc["joinedSmartQuery"]["joinableFields"] = joinable_fields
        qc["joinedSmartQuery"]["dataset"] = {
            "id": new_qc["datasets"][0]["dataset"],
            "slug": new_dataset_slug
        }


        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=qc, headers=headers)
        r.raise_for_status()
        response = r.json()



    def get_qc(self, qc_id):
        for component in self.components:
            if component["id"].startswith("qcomp"):
                if component["settings"]["qc"] == qc_id:
                    return component

    def add_query_composer(self, dataset_slug="", fields:list=[], filters=None, sorted_by=None,  dataset_id="", limit=50, offset=0, pivot=[]):

        qc_id = self.create_qc(dataset_slug, fields, filters, sorted_by, dataset_id, limit, offset, pivot)["id"]

        position = (len(self.components))
        qc_post_url = self.smart_insight_url + "/definitions/" + self.definition_id + "/query_composers"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        body = {"type": "query_composer", "position": position, "qc": qc_id}

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=qc_post_url, json=body, headers=headers)
        response.raise_for_status()
        query = response.json()
        self.components = query["components"]

        return {
            "qc_id": qc_id,
            "component_id": query["components"][position]["id"]
        }


    def create_qc(self, dataset_slug="", fields:list=[], filters=None, sorted_by=None,  dataset_id="", limit=50, offset=0, pivot=[]):
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

            url = self._base_url_askdata + '/smartbot/agents/agentslug/' + self.agent_slug + '/datasetslug/' + dataset_slug

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
            "agentId": self.agent_id,
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

        return response.json()

    def get_component(self, component_id):
        for component in self.components:
            if (component["id"] == component_id):
                return component


    def add_query_composer_to_data_component(self, data_id, dataset_slug="", fields:list=[], filters=None, sorted_by=None,  dataset_id="", limit=50, offset=0, pivot=[]):

        qc_id = self.create_qc(dataset_slug, fields, filters, sorted_by, dataset_id, limit, offset, pivot)["id"]
        name = self.get_component(data_id)["settings"]["name"]
        variable_name = self.get_component(data_id)["settings"]["variableName"]
        body = {
            "name": name,
            "variableName": variable_name,
            "qcId": qc_id
        }
        url = self._base_url_askdata+"/smartinsight/definitions/"+self.definition_id+"/data_queries/"+data_id
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

    def edit_data(self, data_id: str, df: pd.DataFrame, index:bool=False, qc_id=None):

        body = df.to_json(orient="table", index=index)
        if(qc_id!=None):
            body["qcId"] = qc_id

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/data_queries/"+data_id+"/data"
        #logging.info("URL: {}".format(url))
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, data=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]


    def load_data_entities(self, data_id):
        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/queries"
        #logging.info("URL {}".format(url))
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=url, headers=headers)
        response.raise_for_status()
        r = response.json()
        for query in r:
            if(query["id"]==data_id):
                query_data = query
                return query_data["entities"]
        logging.info("No query with id {} found".format(data_id))
        return []

    #TODO Metodo per ottenere una specifica entity e relativa posizione

    def edit_data_entity(self, data_id, entity_position:int, entity_settings:dict):

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/queries/"+data_id+"/columns/"+str(entity_position)

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=entity_settings, headers=headers)
        r.raise_for_status()

    def edit_data_name(self, data_id, component_name):
        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/data_queries/"+data_id
        body = {
            "name": component_name
        }
        #logging.info("URL: {}".format(url))

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

    def add_cta(self, cta_label, cta_url):
        position = (len(self.components))
        cta_id = self.add_component("cta", position)
        self.edit_cta(cta_id, cta_label, cta_url)
        return cta_id

    def edit_cta(self, id, label, cta_url):

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/ctas/"+id
        body = {
            "id":id,
            "type":"cta",
            "name":"Cta 1",
            "customName":False,
            "dependsOn":[],
            "valid":True,
            "queryComponent":False,
            "label":label,
            "link":cta_url
        }

        #logging.info("URL: {}".format(url))

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

    def add_compare(self, name, second_item_enabled, query_id_1, measure_1, label_1, description_1,
                     query_id_2, measure_2, label_2, description_2, formatter_type="HIGH"):
        position = (len(self.components))
        compare_id = self.add_component("comparison", position)
        self.edit_compare(compare_id, name, second_item_enabled, query_id_1, measure_1, label_1, description_1,
                     query_id_2, measure_2, label_2, description_2, formatter_type)
        return compare_id

    def edit_compare(self, compare_id, name, second_item_enabled, query_id_1, measure_1, label_1, description_1,
                     query_id_2, measure_2, label_2, description_2, formatter_type="HIGH"):

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/comparisons/"+compare_id
        body = {
            "name": name,
            "itemA": {
                "queryId": query_id_1,
                "measure":measure_1,
                "label":label_1,
                "description":description_1,
                "measureComparator":None
            },
            "itemB": {
                "queryId":query_id_2,
                "measure":measure_2,
                "label":label_2,
                "description": description_2,
                "measureComparator":None
            },
            "secondItemEnabled": second_item_enabled,
            "formatterType":formatter_type
        }
        #logging.info("URL: {}".format(url))

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]


    def add_text(self, text):
        position = (len(self.components))
        text_id = self.add_component("text", position)
        self.edit_text(text_id, text)
        return text_id


    def edit_text(self, text_id , text, name="Text"):

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/texts/"+text_id

        body = {
            "customName": False,
            "dependsOn": [],
            "id": text_id,
            "name": name,
            "queryComponent": False,
            "text": text,
            "type": "text",
            "valid": True
        }

        #logging.info("URL: {}".format(url))

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]


    def add_html(self, code):
        position = (len(self.components))
        html_id = self.add_component("html", position)
        self.edit_html(html_id, code)
        return html_id


    def edit_html(self, html_id, code):

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/htmls/"+html_id+"/content"

        body = {
            "html": code
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]


    def add_script(self, script):
        position = (len(self.components))
        script_id = self.add_component("script", position)
        self.edit_script(script_id, script)
        return script_id


    def edit_script(self, script_id, script):

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/scripts/"+script_id+"/content"

        body = {
            "script": script
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

    def add_map(self):
        position = (len(self.components))
        map_id = self.add_component("map", position)
        return map_id

    def add_image(self, image, cta):
        position = (len(self.components))
        image_id = self.add_component("image", position)
        image_url = self.upload_image(image)
        self.edit_image(image_id, image_url, cta)
        return image_id


    def upload_image(self, image):

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_askdata+'/smartconfiguration/icons?folder=insightdefinition'

        file = {'file': image}
        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=authentication_url, files=file, headers=headers)
        response.raise_for_status()
        return response.json()["url"]

    def edit_image(self, image_id, image_url, cta, image_name="Image 1"):

        body = {
            "id":image_id,
            "type":"image",
            "name":image_name,
            "customName":False,
            "dependsOn":[],
            "valid":True,
            "queryComponent":False,
            "link": cta,
            "image": image_url
        }

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/images/"+image_id

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]

    def add_sql_query(self, query_sql, dataset_slug, is_native = False):

        position = (len(self.components))

        sql_id = self.add_component("sql_query", position)

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_askdata + '/smartdataset/datasets/slug/' + self.agent_id + '/' + dataset_slug
        #logging.info("AUTH URL {}".format(authentication_url))

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=authentication_url, headers=headers)
        response.raise_for_status()
        r = response.json()
        dataset_id = r["dataset"]["id"]

        url_put = self.smart_insight_url + "/definitions/" + self.definition_id + "/sql_queries/" + sql_id
        body2 = {
            "datasetId": dataset_id,
            "sql": query_sql,
            "id": sql_id,
            "nativeType": is_native,
            "queryComponent": True,
            "type": "sql_query",
            "valid": True,
            "variableName": sql_id + "Result"
        }
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url_put, json=body2, headers=headers)
        r.raise_for_status()

        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/sql_queries/"+self.components[position]["id"]+"/sql"

        body = {
            "datasetId": dataset_id,
            "sql": query_sql,
        }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()

        self.components = r.json()["components"]

        hasResultSet = True

        for component in r.json()["components"]:
            if component["id"] == sql_id:
                if component["preview"] == []:
                    hasResultSet = False
                elif component["preview"][0]["details"]["rows"] == []:
                    hasResultSet = False

        return sql_id , hasResultSet


    def delete(self):

        url= self.smart_insight_url+"/definitions/"+self.definition_id+"?final=true"
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


    def add_query(self, dataset_slug, fields):

        '''
        fields = [{column: "STATUS_HISTORY_NUOVO_TIME", aggregation: null,…}}
        '''

        position = (len(self.components))

        # Get dataset_id
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        authentication_url = self._base_url_askdata + '/smartdataset/datasets/slug/' + \
                             self.agent_id + '/' + dataset_slug

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=authentication_url, headers=headers)
        response.raise_for_status()
        r = response.json()

        try:
            dataset_id = r["dataset"]["id"]
        except:
            logging.error("DATASET NOT FOUND")
            return

        url_get = self.smart_insight_url + "/composed_queries?datasetId=" + dataset_id

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.get(url=url_get, headers=headers)
        response.raise_for_status()
        r = response.json()

        query_composer = r["qc"]

        url_preview = self.smart_insight_url+"/composed_queries/"+query_composer["id"]+"/preview?limit=100"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=url_preview, json={}, headers=headers)
        response.raise_for_status()
        r = response.json()
        qc_fields = query_composer["fields"]

        new_fields = []

        for qc_field in qc_fields:
            for field in fields:
                if (field["column"] == qc_field["column"] or field["column"] == qc_field["alias"]):
                    qc_field["aggregation"] = field["aggregation"]
                    del qc_field["internalDataType"]
                    new_fields.append(qc_field)

        query_composer["fields"] = new_fields
        del query_composer["relationships"]
        query_composer["where"] = []
        query_composer["orderBy"] = []

        post_url = self.smart_insight_url+"/composed_queries"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=post_url, json=query_composer, headers=headers)
        response.raise_for_status()

        qc_post_url = self.smart_insight_url+"/definitions/"+self.definition_id+"/query_composers"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        body = {"type": "query_composer", "position": position, "qc": query_composer["id"]}

        headers = {"Authorization": "Bearer" + " " + self._token}
        response = s.post(url=qc_post_url, json=body, headers=headers)
        response.raise_for_status()
        r = response.json()


    def add_search_query(self, query):

        position = (len(self.components))
        query_id = self.add_component("nl_query", position)

        body_query = {"nl": query, "language": "en"}

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        query_url = self.smart_insight_url +'/definitions/'+ self.definition_id +'/nl_queries/'+ query_id + '/nl'

        #logging.info("QUERY URL {}".format(query_url))
        r = s.put(url=query_url, json=body_query, headers=headers)

        self.components = r.json()["components"]

        return self.components[position]["id"]


    def add_component(self, type, position):

        body = {"type": type, "position": position}

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        query_url = self.smart_insight_url + '/definitions/' + self.definition_id + '/components/'
        #logging.info("URL {}".format(query_url))
        r = s.post(url=query_url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]
        return self.components[position]["id"]


    def get_url(self):
        url = self.app_url

        get_url = self._base_url_askdata+"/smartbot/agents/"+self.agent_id

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.get(url=get_url, headers=headers)
        r.raise_for_status()

        agent_slug = r.json()["slug"]

        url += agent_slug

        url += "/card/"
        url += self.slug
        return url

    def add_admin(self, admin_email):

        get_url = self._base_url_askdata+"/smartbot/share/principals?q="+admin_email

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.get(url=get_url, headers=headers)
        r.raise_for_status()
        if(r.json()!=[]):
            body = {
                "role": "ADMIN",
                "userId": r.json()[0]["id"]
            }

            url = self.smart_insight_url+"/insights/8a09ec79-8e1e-401a-bdec-70d33c9c1543/users"

            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            query_url = self.smart_insight_url + '/definitions/' + self.definition_id + '/components/'
            #logging.info("URL {}".format(query_url))
            r = s.post(url=url, json=body, headers=headers)
            r.raise_for_status()
        else:
            logging.error("EMAIL ERRATA: Inserire una email corrispondente ad un utente Askdata")


    def add_follower(self, follower_email):

        get_url = self._base_url_askdata+"/smartbot/share/principals?q="+follower_email

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.get(url=get_url, headers=headers)
        r.raise_for_status()
        if(r.json()!=[]):
            body = {
                "role": "FOLLOWER",
                "userId": r.json()[0]["id"]
            }

            url = self.smart_insight_url+"/insights/8a09ec79-8e1e-401a-bdec-70d33c9c1543/users"

            s = requests.Session()
            s.keep_alive = False
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer" + " " + self._token
            }
            query_url = self.smart_insight_url + '/definitions/' + self.definition_id + '/components/'
            #logging.info("URL {}".format(query_url))
            r = s.post(url=url, json=body, headers=headers)
            r.raise_for_status()
        else:
            logging.error("EMAIL ERRATA: Inserire una email corrispondente ad un utente Askdata")


    def edit_card(self, icon="", name=""):

        if(icon==""):
            icon = self.icon
        else:
            self.icon=icon

        if(name==""):
            name = self.name
        else:
            self.name=name

        body={
            "icon": icon,
            "name": name,
            "slug": self.slug
        }

        url = self.smart_insight_url+"/definitions/"+self.definition_id

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()
        self.components = r.json()["components"]


    def get(self):

        get_url = self.smart_insight_url+"/definitions/"+self.definition_id+"/card"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.get(url=get_url, headers=headers)
        r.raise_for_status()


        return r.json()["attachment"]

    def delete_component(self, component_id):

        for component in self.components:
            if(component["id"]==component_id):
                self.components.remove(component)

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        query_url = self.smart_insight_url + '/definitions/' + self.definition_id + '/components/'+component_id
        logging.info("DELETE URL {}".format(query_url))
        r = s.delete(url=query_url, headers=headers)
        r.raise_for_status()


    def set_on_demand(self, enabled=True):

        body = {"enabled":enabled}

        url = self.smart_insight_url + "/definitions/" + self.definition_id+ "/intents/status"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()

    def add_on_demand_queries(self, queries):

        body = {"userQuery": queries}

        url = self.smart_insight_url + "/definitions/" + self.definition_id + "/intents"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.put(url=url, json=body, headers=headers)
        r.raise_for_status()

    def schedule_daily(self, channel_slug, hours, minutues, seconds):

        cron = seconds + " " + minutues + " " + hours + " * * *"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        url = self._base_url_askdata + '/smartfeed/channels?agentId=' + self.agent_id + '&slug=' + channel_slug
        r = s.get(url=url, headers=headers)
        r.raise_for_status()

        channel_id = r.json()[0]["id"]

        url = self.smart_insight_url + "/definitions/" + self.definition_id + "/publishing/"

        body = {
            "schedulingCron": cron,
            "enabled": True,
            "destination": {"channels":[channel_id],"code":None,"name":None,"icon":None,"visibility":None,"queryId":None,"empty":None},
            "condition": "always",
            "advancedConditions": None}


        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.post(url=url, json=body, headers=headers)
        r.raise_for_status()


    def schedule_monthly(self, channel_slug, day_of_month, hours, minutues, seconds):

        """day_of_week: day of the week in format MON, TUE, WED, THU, FRI, SAT, SUN"""

        cron = seconds + " " + minutues + " " + hours + day_of_month + " * ?"

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        url = self._base_url_askdata + '/smartfeed/channels?agentId=' + self.agent_id + '&slug=' + channel_slug
        r = s.get(url=url, headers=headers)
        r.raise_for_status()

        channel_id = r.json()[0]["id"]

        url = self.smart_insight_url + "/definitions/" + self.definition_id + "/publishing/"

        body = {
            "schedulingCron": cron,
            "enabled": True,
            "destination": {"channels":[channel_id],"code":None,"name":None,"icon":None,"visibility":None,"queryId":None,"empty":None},
            "condition": "always",
            "advancedConditions": None}


        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.post(url=url, json=body, headers=headers)
        r.raise_for_status()

    def schedule_weekly(self, channel_slug, day_of_week, hours, minutues, seconds):
        """day_of_week: day of the week in format MON, TUE, WED, THU, FRI, SAT, SUN"""

        cron = seconds + " " + minutues + " " + hours + " ? * " + day_of_week

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }
        url = self._base_url_askdata + '/smartfeed/channels?agentId=' + self.agent_id + '&slug=' + channel_slug
        r = s.get(url=url, headers=headers)
        r.raise_for_status()

        channel_id = r.json()[0]["id"]

        url = self.smart_insight_url + "/definitions/" + self.definition_id + "/publishing/"

        body = {
            "schedulingCron": cron,
            "enabled": True,
            "destination": {"channels": [channel_id], "code": None, "name": None, "icon": None, "visibility": None,
                            "queryId": None, "empty": None},
            "condition": "always",
            "advancedConditions": None}

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.post(url=url, json=body, headers=headers)
        r.raise_for_status()

    def clone(self, channel_id, card_name="", card_slug=None):

        if card_name == "":
            card_name = "Copy of " + self.name

        if card_slug != None:
            try:
                url = self.smart_insight_url + "/definitions/agent/" + self.agent_id + "/slug/" + card_slug

                s = requests.Session()
                s.keep_alive = False
                retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
                s.mount('https://', HTTPAdapter(max_retries=retries))

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer" + " " + self._token
                }
                r = s.get(url=url, headers=headers)
                r.raise_for_status()

                definition = r.json()
                insight_definition = Insight_Definition(self._env, self._token, self.agent_slug, definition)
                insight_definition.delete()
            except Exception as e:
                logging.info("{} card not found... creating new one".format(card_slug))
                logging.info("{}".format(e.__str__()))


        url = self.smart_insight_url+"/definitions/"+self.definition_id+"/clone"
        body = {
            "agentId": self.agent_id,
            "name": card_name,
            "slug": card_slug,
            "channelId": channel_id
            }

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer" + " " + self._token
        }

        r = s.post(url=url, json=body, headers=headers)
        r.raise_for_status()
import chunk
import time
import codecs
import json
import base64
#import sys
from datetime import datetime, timedelta
import requests
# from .logger import Logger


class API:
    _host = ""
    _access_token = ""
    _api_version = "1.0"
    _authenticated = False
    _logger = None

    def __init__(self, host: str = "https://api.antcde.io/", logging:bool = False):
        self._host = host
        self._logging = logging
        self._remainingRequests = 10

    def login(self, client_id: str, client_secret: str, username: str, password: str) -> bool:
        """ Login into ANT"""
        self._authenticated = False
        self._client_id = client_id
        self._client_secret = client_secret
        response = self._make_request('oauth/token', 'POST', {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret
        })
        if self._logging:
            print('New login call at {}, returned with code {}'.format(datetime.now(), response.status_code))
        if response.status_code != 200:
            print("The response was: {}".format(response.status_code))
            return False
        else:
            parsed_response = response.json()
            # print(parsed_response)
            if 'access_token' not in parsed_response:
                raise SystemError("Please check credentials")
            now = datetime.now()
            self._access_token = parsed_response['access_token']
            self._refresh_token = parsed_response['refresh_token']
            self._expires_at = now + timedelta(seconds=parsed_response['expires_in'])
            self._authenticated = True
            return True

    def _make_api_request(self, path: str, method: str,
                          parameters: dict = None, delete_data: dict = None) -> dict:
        parameters = {} if parameters is None else parameters
        if not self._authenticated:
            raise SystemError("You are not authenticated, please use login first.")

        if datetime.now() >= self._expires_at:
                print('Unauthorised, we try to refresh token')
                self.refresh_token()
                if not self._authenticated:
                    return False

        data = parameters if method in ['GET', 'DELETE'] else json.dumps(
            parameters)
        url = 'api/{}/{}'.format(self._api_version, path)
        #If rate limit is not reached
        if self._remainingRequests == 0:
            remaining_seconds = (self._RateLimitRefreshAt - datetime.now()).total_seconds()
            if self._logging:
                print('Sleeping {} seconds, API rate limit reached'.format(remaining_seconds))
            time.sleep(remaining_seconds)

        response = self._make_request(
            url,
            method,
            data,
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer {}".format(
                    self._access_token)
            }, 
            delete_data)
        # set new time
        if not 'x-ratelimit-remaining' in response.headers:
            response.headers['x-ratelimit-remaining'] = 40 #Set the value to a fictional number to continue with the loop
            print('x-ratelimit-remainig not found in API call: {}'.format(url) )
        if int(self._remainingRequests) < int(response.headers['x-ratelimit-remaining']):
            self._RateLimitRefreshAt = datetime.now() + timedelta(seconds=60)
            print('Reset time to: {}'.format(self._RateLimitRefreshAt))
        
        self._remainingRequests = int(response.headers['x-ratelimit-remaining'])

        if self._logging:
            print('New API call at {}, returned with code {}'.format(datetime.now(), response.status_code))
            if int(response.headers['x-ratelimit-remaining']) < 10:
                print('Warning, you are reaching the API_rate_limit, {} calls left this minute'.format(response.headers['x-ratelimit-remaining']))
        if response.status_code == 401:
            print('You are not authenticated for this API call')
            return False

        if response.text == '':
            print("response was empty")
            return ''
        # print(response.text)
        parsed_response = response.json()
        if 'message' in parsed_response:
            if parsed_response['message'] == 'Unauthenticated.':
                raise PermissionError('Unauthenticated')
            if parsed_response['message'] == "Too Many Attempts.":
                raise ProcessLookupError("Too many requests attempted")
        return parsed_response

    def _make_request(self, path: str, method: str, parameters: dict = None,
                      headers: dict = None, data: dict = None) -> requests.Response:
        parameters = {} if parameters is None else parameters
        headers = {} if headers is None else headers
        url = '{}{}'.format(self._host, path)
        if method == 'GET':
            return requests.get(
                url, params=parameters, headers=headers, verify=True)
        if method == 'PUT':
            return requests.put(
                url, data=parameters, headers=headers, verify=True)
        if method == 'DELETE':
            return requests.delete(
                url, data=data, params=parameters, headers=headers, verify=True)
        if method == 'POST':
            return requests.post(
                url, data=parameters, headers=headers, verify=True)
        raise NotImplementedError("http method not implemented")

    def refresh_token(self):
        body = {'grant_type':'refresh_token', 'refresh_token': self._refresh_token, 'client_id': self._client_id, 'client_secret': self._client_secret, 'scope': ''}
        url = '{}oauth/token'.format(self._host)
        response = requests.post(url, data=body)
        if self._logging:
            print('New login call at {}, returned with code {}'.format(datetime.now(), response.status_code))
        if response.status_code != 200:
            print('something went wrong with receiving new access_token')
            self._authenticated = False
        else:
            now = datetime.now()
            parsed_response = response.json()
            self._access_token = parsed_response['access_token']
            self._refresh_token = parsed_response['refresh_token']
            self._expires_at = now + timedelta(seconds=parsed_response['expires_in'])
            print('token successfully refreshed')

    def projects_read(self):
        """ List all your projects"""
        path = 'projects'
        return self._make_api_request(path, 'GET')

    def project_create(self,licenseid: str, name: str, number:str = '', description:str = '', imageName:str = '', imageExtension:str = '', imageData:str = '') -> dict:
        """ Create a new project """
        path = 'project'
        if(imageExtension == ''):
            project = {
                "name": name,
                "number": number,
                "description": description,
                "license": licenseid,
            }
        else:
            project = {
            "name": name,
            "number": number,
            "description": description,
            "license": licenseid,
            "image": {
                "name": imageName,
                "extension": imageExtension,
                "data": imageData
            }
        }
        return self._make_api_request(path, 'POST', project)

    def project_read(self, project_id: str) -> dict:
        """ Get project details """
        path = 'project/{}'.format(project_id)
        return self._make_api_request(path, 'GET')

    def project_Update(self, project_id: str, name: str) -> dict:
        """ Get project update """
        path = 'project/{}'.format(project_id)
        return self._make_api_request(path, 'PUT', {
            "name": name
        })

    def project_delete(self, project_id: str) -> dict:
        """ Get project delete """
        path = 'project/{}'.format(project_id)
        return self._make_api_request(path, 'DELETE')

    def tables_read(self, project_id: str):
        """ Get tables in a project """
        path = 'tables'
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id
        })

    def table_create(self, project_id: str, name: str) -> dict:
        """ Create a table in a project """
        path = 'table'
        return self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "name": name
        })

    def table_read(self, project_id: str, table_id: str) -> dict:
        """ Get details of a table in a project """
        path = 'table/{}'.format(table_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id
        })

    def table_update(self, project_id: str, table_id: str, name: str) -> dict:
        """ Update a table in a project """
        path = 'table/{}'.format(table_id)
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "name": name
        })

    def table_delete(self, project_id: str, table_id: str) -> dict:
        """ Delete a table in a project """
        path = 'table/{}'.format(table_id)
        return self._make_api_request(path, 'DELETE', {
            "project[id]": project_id
        })

    def columns_read(self, project_id: str, table_id: str):
        """ Get all columns in a table """
        path = 'columns'
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def column_create(self, project_id: str, table_id: str, name: str,
                      fieldType: str, defaultValue: str = "",
                      options: list = None, required: bool = True, ordinal: int = "") -> dict:
        """ Create a column in a table """
        options = [] if options is None else options
        path = 'column'
        return self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "name": name,
            "type": fieldType,
            "options": options,
            "default": defaultValue,
            "required": required,
            "ordinal": ordinal
        })

    def column_read(self, project_id: str, table_id: str, column_id):
        """ Get details for a specific column in a table """
        path = 'column/{}'.format(column_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def column_update(self, project_id: str, table_id: str, column_id: str,
                      name: str, defaultValue: str = "",
                      options: list = None, required: bool = True, ordinal: int = 0) -> dict:
        """ Update details for a specific column in a table """
        path = 'column/{}'.format(column_id)
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "name": name,
            "required": required,
            "options": options,
            "default": defaultValue,
            "ordinal": ordinal
        })

    def column_delete(self,
                      project_id: str, table_id: str, column_id: str) -> dict:
        """ Delete column in a table """
        path = 'column/{}'.format(column_id)
        return self._make_api_request(path, 'DELETE', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def records_create_csv(self, project_id: str, table_id: str,
                       records_csv: str, session: str = ""):
        """ Import a csv file into a table """
        path = 'records/import'
        with codecs.open(records_csv, mode="r", encoding='utf-8') as csv_file:
            encoded_csv = base64.b64encode(str.encode(csv_file.read()))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "session": {"id": session},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def records_create(self, project_id: str, table_id: str,
                       records: list, session: str = ""):
        """ Create multiple records into a table """
        path = 'records/import'
        encoded_csv = base64.b64encode(self.create_virtual_csv(records).encode("utf-8"))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "session": {"id": session},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def records_import(self, project_id: str, table_id: str,
                       records: list, session: str = ""):
        """ Create multiple records into a table """
        path = 'records/import'
        encoded_csv = base64.b64encode(self.create_virtual_csv_Addid(records).encode("utf-8"))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "session": {"id": session},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def records_read_chunk(self, project_id: str, table_id: str, limit: int = 0, offset: int = 0, session: str = "") -> dict:
        """ Get reords of table """
        path = 'records'
        record_data = self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id,
            "filter[limit]": limit,
            "filter[offset]":offset,
            "filter[session]":session,
        })
        return record_data

    def records_read(self, project_id: str, table_id: str, limit: int = 0, offset: int = 0, session: str = "") -> dict:
        """ Get reords of table """
        chunk_size = 10000
        record_data = self.records_read_chunk(project_id, table_id, chunk_size, offset, session)
        if(limit == 0 or limit > chunk_size):
            temp_limit = chunk_size
            # print(record_data)
            if len(record_data['records']) < temp_limit:
                return record_data['records']
            else:
                if 'metadata' in record_data:
                    chunks = (record_data['metadata']['count'] - offset) // temp_limit
                    if self._logging:
                        print("Total table is bigger ({}) than chunksize({}), splitting up in: {} additional calls".format(record_data['metadata']['count'] - offset, temp_limit, chunks))
                    all_records = record_data['records']
                    for i in range(1,chunks+1):
                        temp_offset = offset + ( i * temp_limit )
                        record_data = self.records_read_chunk(project_id, table_id, temp_limit, temp_offset, session)
                        all_records = all_records + record_data['records']
                return all_records
        else:
            temp_limit = limit
            return record_data['records']

    def records_search(self, projectId:str , tableId:str , searchFields:list, searchPrase:str, searchExact:str, searchRange:list, session:str):
        """Search in the records"""
        path = 'search'
        if range:
            package = {
                "project": {"id":projectId},
                "table": {"id": tableId},
                "search": {"min": range[0], "max": range[1]},
                "searchfields": [searchFields],
                "session": {"id": session},
            }   
        else:
            package = {
                "project": {"id":projectId},
                "table": {"id": tableId},
                "search": {"phrase": searchPrase, "exact": searchExact},
                "searchfields": [searchFields],
                "session": {"id": session},
            }
        result = self._make_api_request(path, 'POST', package)
        return result

    def records_by_revision(self, projectId:str , tableId:str, revisionId:str):
        """Get records of revision"""
        path = 'search'
        package = {
                "project": {"id":projectId},
                "table": {"id": tableId},
                "revision": revisionId
            }   
        return self._make_api_request(path, 'POST', package)

    def records_delete(self, project_id: str, table_id: str,
                       records_ids: list) -> dict:
        """ Delete records in table """
        path = 'records'
        data = {
            "project":{
                "id": project_id
            },
            "table": {
                "id": table_id
            },
            "records": records_ids
        }
        return self._make_api_request(path, 'DELETE', data)

    def records_verify_csv(self, project_id: str, table_id: str, records_csv: str) -> dict:
        """ Verify structure of CSV file against a table """
        path = 'records/verify'
        with codecs.open(records_csv, mode="r", encoding='utf-8') as csv_file:
            encoded_csv = base64.b64encode(str.encode(csv_file.read()))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def records_verify(self, project_id: str, table_id: str, records: list) -> dict:
        """ Verify structure of records against a table """
        path = 'records/verify'
        encoded_csv = base64.b64encode(self.create_virtual_csv(records).encode("utf-8"))
        result = self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "records": encoded_csv.decode("utf-8")
        })
        return result

    def record_create(self, project_id: str, table_id: str,
                      record_values: dict, session: str = "") -> dict:
        """ Create a single record into a table """           
        path = 'record'
        return self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "session": {"id": session},
            "record": record_values
        })

    def record_read(self, project_id: str, table_id: str,
                    record_id: str) -> dict:
        """ Read a specific record of a table """
        path = 'record/{}'.format(record_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def record_update(self, project_id: str, table_id: str, record_id: str,
                      updated_record_values: dict, session:str = "") -> dict:
        """ Update a specific record of a table """
        path = 'record/{}'.format(record_id)
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "session": {"id": session},
            "record": updated_record_values
        })

    def record_delete(self, project_id: str, table_id: str,
                      record_id: str) -> dict:
        """ Delete a specific record of a table """
        path = 'record/{}'.format(record_id)
        return self._make_api_request(path, 'DELETE', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def record_history(self, project_id: str, table_id: str,
                       record_id: str) -> dict:
        """ Get change record history a specific record of a table """
        path = 'record/{}'.format(record_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def revisions_read(self, project_id: str, table_id: str) -> dict:
        """ Get all revisions of a table """
        path = 'revisions'
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def revision_create(self, project_id: str, table_id: str,
                        name: str) -> dict:
        """ Create a new revisions for a table """
        path = 'revision'
        return self._make_api_request(path, 'POST', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "name": name,
            "timestamp": time.time()
        })

    def revision_read(self, project_id  : str, table_id: str,
                      revision_id: str) -> dict:
        """ Get details of a revisions for a table """
        path = 'revision/{}'.format(revision_id)
        return self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            
            "table[id]": table_id
        })

    def revision_update(self, project_id: str, table_id: str,
                        revision_id: str, name: str) -> dict:
        """ Update a revision for a table """
        path = 'revision/{}'.format(revision_id)
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "name": name,
            "timestamp": time.time()
        })

    def revision_delete(self: str, project_id: str, table_id: str,
                        revision_id: str) -> dict:
        """ Delete a revision for a table """
        path = 'revision/{}'.format(revision_id)
        return self._make_api_request(path, 'DELETE', {
            "project[id]": project_id,
            "table[id]": table_id
        })

    def upload_document(self, project_id: str, table_id: str, column_name: str, document_location, document_title: str = None, session:str = ""):
        """ Upload a document to a table. Creates a new record """
        if document_title is None:
            document_title = document_location.split("/")[-1]
        ext = document_title.split(".")[-1]
        path = 'record'
        with open(document_location, "rb") as image_file:
            encoded_file = base64.b64encode(image_file.read())
        dataset = {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "record": {
                column_name: {
                    "name": document_title,
                    "extension": ext,
                    "data": encoded_file.decode("utf-8")
                }
            },
            "session": {"id": session}
        }
        res = self._make_api_request(path, 'POST', dataset)
        if 'id' in res:
            return res
        else:
            return "Error"

    def attach_document(self, project_id: str, table_id: str, column_name: str, record_id: str, document_location, document_title: str = None, session:str = ""):
        """ Upload a document to an existing record. """
        if document_title is None:
            document_title = document_location.split("/")[-1]
        ext = document_location.split(".")[-1]
        path = 'record/{}'.format(record_id)
        with open(document_location, "rb") as image_file:
            encoded_file = base64.b64encode(image_file.read())
        dataset = {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "record": {
                column_name: {
                    "name": document_title,
                    "extension": ext,
                    "data": encoded_file.decode("utf-8")
                }
            },
            "session": {"id": session}
        }
        res = self._make_api_request(path, 'PUT', dataset)
        if 'id' in res:
            return res
        elif 'message' in res:
            return res['message']
        else:
            return "Error"

    def download_document(self, project_id: str, table_id: str, document_id: str, file_location: str, file_name: str = None):
        """ Download a document. Specify save location and filename """
        path = 'record/document/{}'.format(document_id)
        response = self._make_api_request(path, 'GET', {
            "project[id]": project_id,
            "table[id]": table_id
        },'')
        if 'file' in response[0]:
            if file_name is None:
                file_name = '{}.{}'.format(response[0]['name'], response[0]['extension'])
            content = base64.b64decode(response[0]['file'])
            try:
                file = open('{}/{}'.format(file_location, file_name), 'wb+')
                file.write(content)
                file.close()
            except Exception as ex:
                print('Error saving file: {}'.format(ex))

    # tasks
    def tasks_read(self, project_id: str = "", status: str = "", user: str = "") -> list:
        """ Get tasks"""
        path = 'tasks'
        return self._make_api_request(path, 'GET', {
            "filter[project]": project_id,
            "filter[status]": status,
            "filter[user]": user
        })

    def task_create(self, project_id: str, name: str, description: str, status: str, due_date: str, assigned_user: str, start_date: str, appendix: object = {}) -> dict:
        """ Create a task in a project """
        path = 'task'
        if appendix == {}:
            body = {
                "project": {"id": project_id},
                "name": name,
                "description": description,
                "status": status,
                "assigned_user": assigned_user,
                "due_date": due_date,
                "start_date": start_date
            }
        else:
            body = {
                "project": {"id": project_id},
                "name": name,
                "description": description,
                "status": status,
                "assigned_user": assigned_user,
                "due_date": due_date,
                "start_date": start_date,
                "appendix": appendix
            }
        return self._make_api_request(path, 'POST',body )

    def task_read(self, task_id: str) -> dict:
        """ Get details of a task"""
        path = 'task/{}'.format(task_id)
        return self._make_api_request(path, 'GET', {})

    def task_update_name(self, task_id: str,name: str) -> dict:
        """ Update a task name"""
        path = 'task/{}'.format(task_id)
        return self._make_api_request(path, 'PUT', {
            "name": name
        })

    def task_respond(self, task_id: str, response: str, assigned_user: str, status: str, due_date: str = "", appendix: object = {}) -> dict:
        """ Respond to a task"""
        path = 'task/{}/message'.format(task_id)
        if appendix == {}:
            body = {
                    "response": response,
                    "status": status,
                    "assigned_user": assigned_user,
                    "due_date": due_date,
            }
        else:
            body = {
                "response": response,
                "status": status,
                "assigned_user": assigned_user,
                "due_date": due_date,
                "appendix": appendix
            }
        return self._make_api_request(path, 'POST', body)

    def task_delete(self, task_id: str) -> dict:
        """ Delete a task"""
        path = 'task/{}'.format(task_id)
        return self._make_api_request(path, 'DELETE',{}) 

    def task_getJob(self, project_id: str, task_id:str) -> dict:
        """Get the job associated to the given task"""
        path = 'project/{}/task/{}/job'.format(project_id, task_id)
        return self._make_api_request(path, 'GET', {})

    ## CustomFunctions    
    def record_update_withdocument(self, project_id: str, table_id: str, record_id: str, updated_record_values: dict, document_column_name: str, document_location, document_title: str = None) -> dict:
        """Update record with a document"""
        path = 'record/{}'.format(record_id)
        if document_title is None:
            document_title = document_location.split("/")[-1]
        ext = document_location.split(".")[-1]
        with open(document_location, "rb") as image_file:
            encoded_file = base64.b64encode(image_file.read())
            updated_record_values[document_column_name] = {
                "name": document_title,
                "extension": ext,
                "data": encoded_file.decode("utf-8")
            }
        return self._make_api_request(path, 'PUT', {
            "project": {"id": project_id},
            "table": {"id": table_id},
            "record": updated_record_values
        })

    def create_virtual_csv(self, records: list):
        """Not for use. Create a virtual CSV of records"""
        encoded_csv = ",".join(records[0].keys())+"\n"
        for record in records:
            recs = []
            for key in record.keys():
                recs.append(record[key])
            encoded_csv += ",".join(recs)+"\n"
        return encoded_csv

    def create_virtual_csv_Addid(self, records: list):
        """Not for use. Create a virtual CSV of records"""
        encoded_csv = "id,"+",".join(records[0].keys())+"\n"
        for record in records:
            recs = []
            for key in record.keys():
                recs.append(record[key])
            encoded_csv += ","+",".join(recs)+"\n"
        return encoded_csv
    
    def parse_document(self, documentLocation, documentTitle:str = None):
        """Parse a document to the ANT Format."""
        if documentTitle is None:
            documentTitle = documentLocation.split("/")[-1]
        ext = documentTitle.split(".")[-1]
        with open(documentLocation, "rb") as image_file:
            encoded_file = base64.b64encode(image_file.read())
        document = {
            "name": documentTitle,
            "extension": ext,
            "data": encoded_file.decode('utf-8')
        }
        return document

    def parse_date(self, year: int, month: int, day: int, hour: int, minute: int, seconds: int):
        """Parse a date to the ANT Format."""
        date = str(year+"-"+month+"-"+day+" "+hour+":"+minute+":"+seconds)
        return date

    def task_download(self, task_id: str, document_id: str, file_location: str, file_name: str = None):
        """ Download a document. Specify save location and filename """
        path = 'task/document/{}'.format(document_id)
        response = self._make_api_request(path, 'GET',{"task[id]": task_id})
        if 'file' in response[0]:
            if file_name is None:
                file_name = '{}.{}'.format(response[0]['name'], response[0]['extension'])
            content = base64.b64decode(response[0]['file'])
            try:
                file = open('{}/{}'.format(file_location, file_name), 'wb+')
                file.write(content)
                file.close()
                return True
            except Exception as ex:
                print('Error saving file: {}'.format(ex))
                return False

    def job_finish(self, project_id: str, job_id: str) -> dict:
        """ Finish job (workflow task)"""
        path = 'project/{}/job/{}/finish'.format(project_id, job_id)
        return self._make_api_request(path, 'POST', {})


    # SBS Codes
    def sbs_codes(self, project_id: str) -> dict:
        """ Get all SBS codes """
        path = 'project/{}/sbs'.format(project_id)
        return self._make_api_request(path, 'GET', {})

    def sbs_getTree(self, project_id: str) -> dict:
        """ Get SBS Tree """
        path = 'project/{}/sbs-tree'.format(project_id)
        return self._make_api_request(path, 'GET', {})

    def sbs_addCode(self, project_id: str, code:str, parentCode: str = "", label: str = "") -> dict:
        """ Add SBS COde """
        path = 'project/{}/sbs'.format(project_id)
        return self._make_api_request(path, 'POST', {
            "code": code, "parent": parentCode, "label": label})

    def sbs_updateParent(self, project_id: str, sbsId:str, parent:str) -> dict:
        """ Update the parent of the SBSCode """
        path = 'project/{}/sbs/{}'.format(project_id, sbsId)
        return self._make_api_request(path, 'PUT', {
            "parent": parent})

    def sbs_updateLabel(self, project_id: str, sbsId:str, label:str) -> dict:
        """ Update the label of the SBS Code """
        path = 'project/{}/sbs/{}'.format(project_id, sbsId)
        return self._make_api_request(path, 'PUT', {
            "label": label})

    def sbs_removeCode(self, project_id: str, sbsId:str) -> dict:
        """ Remove the SBSCode """
        path = 'project/{}/sbs/{}'.format(project_id,sbsId)
        return self._make_api_request(path, 'DELETE', {})


    #Sessions
    def project_sessions(self, project_id: str, sbsId:str) -> dict:
        """ Get Project Sessions """
        path = 'project/{}/sessions'.format(project_id)
        return self._make_api_request(path, 'GET', {})
    
    def workflow_sessions(self, project_id: str, session_id:str) -> dict:
        """ Workflow sessions """
        path = 'project/{}/sessions/{}'.format(project_id,session_id)
        return self._make_api_request(path, 'GET', {})

    def workflow_createSession(self, project_id: str, workflow_id:str, name:str , sbs_code:str = "") -> dict:
        """ Workflow sessions """
        path = 'project/{}/session'.format(project_id)
        return self._make_api_request(path, 'POST', {"name": name, "workflow": workflow_id, "sbs_code": sbs_code})

    def workflow_sessionUpdateName(self, project_id: str, session_id:str, name:str) -> dict:
        """ Workflow sessions """
        path = 'project/{}/session/{}'.format(project_id,session_id)
        return self._make_api_request(path, 'PUT', {"name": name})

    def workflow_sessionUpdateSBS(self, project_id: str, session_id:str, sbs_code:str) -> dict:
        """ Workflow sessions """
        path = 'project/{}/session/{}'.format(project_id,session_id)
        return self._make_api_request(path, 'PUT', {"sbs_code": sbs_code})
 
    def workflow_sessionDelete(self, project_id: str, session_id:str) -> dict:
        """ Workflow sessions """
        path = 'project/{}/session/{}'.format(project_id,session_id)
        return self._make_api_request(path, 'DELETE', {})

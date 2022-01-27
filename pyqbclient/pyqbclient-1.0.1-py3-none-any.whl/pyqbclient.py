import json
import numpy as np
import requests
import pandas as pd
from io import StringIO
import requests
import re
from lxml import etree
import logging


logger = logging.getLogger("pyqbclient")


    
class Error(Exception):
    """Base Error
    """
    def __init__(self, code, msg, response=None):
        self.args = (code, msg)
        self.msg = (code, msg)
        self.desc = code
        self.response = response

    def __str__(self):
        return f'{self.msg}: {self.desc}'



class ResponseError(Error):
    pass


class QuickBaseError(Error):
    pass


default_realm_hostname = None
default_user_token = None

def set_default(realm_hostname=None,user_token=None):
    global default_realm_hostname
    global default_user_token

    default_realm_hostname = realm_hostname
    default_user_token = user_token

def _slice_list(start_line,filter_list):
    end_line = start_line + 100
    slice = filter_list[start_line:end_line:]
    return slice  


class Client(object):

    def check_defaults(self,realm_hostname,user_token):
        if default_realm_hostname == None:
            if realm_hostname == None:
                raise ValueError('Must provide a realm hostname')
            self.realm_hostname = realm_hostname
        else:
            if realm_hostname != None:
                self.realm_hostname = realm_hostname
            else:
                self.realm_hostname = default_realm_hostname
        
        if default_user_token == None:
            if user_token == None:
                raise ValueError('Must provide a user token')
            self.user_token = f'QB-USER-TOKEN {user_token}'
        else:
            if user_token != None:
                self.user_token = f'QB-USER-TOKEN {user_token}'
            else:
                self.user_token = f'QB-USER-TOKEN {default_user_token}'

    def set_retries(self,retries):
        if retries < 0:
            raise ValueError('Retries must be 0 or greater')
        self.retries = retries
    
    def json_request(self,body,request_type,
    api_type,return_type,sub_url=None):

        url =f'https://api.quickbase.com/v1/{api_type}'
        if  not isinstance(sub_url,type(None)):
            url += f'/{sub_url}'


        for attempt in range(self.retries + 1):
            try:
                if request_type == 'post':
                    with requests.Session() as s:
                        r = s.post(
                        url, 
                        params = self.base_params, 
                        headers = self.headers, 
                        json = body
                        )


                elif request_type == 'delete':
                    with requests.Session() as s:
                        r = s.delete(
                        url, 
                        params = self.base_params, 
                        headers = self.headers, 
                        json = body
                        )

                
                elif request_type == 'get':
                    with requests.Session() as s:
                        r = s.get(
                        url, 
                        params = self.base_params, 
                        headers = self.headers
                        )
                    
                
                response = json.loads(r.text)
                
          


                if request_type != 'get': 
                    if "message" in response.keys():
                        raise QuickBaseError(
                         response['message'],
                         response['description']
                       ,
                        response=response
                        )
                    if "errors" in response.keys():
                        raise QuickBaseError(
                        'Request returned error(s):',
                        f'{", ".join(response["errors"])}',response=response
                        )
                if r.status_code not in [200,207]:
                        r.raise_for_status()
             

            except QuickBaseError:
                logger.critical('Quickbase Error')
                raise
            except Exception as e:    
                if attempt < self.retries:
                    logger.error(e)
                    logger.info(f'Retrying  - Attempt {attempt +1}')

                    continue
                else:
                    logger.critical(e)
                    raise
            break

        if return_type == 'response':
            return response
        elif return_type == 'dataframe':
            df = pd.json_normalize(response['data'])
            metadata = response['metadata']
            return df, metadata
        elif return_type == 'properties':

            json_data = pd.read_json(StringIO(r.text))
            properties = json_data.join(
            pd.json_normalize(
            json_data.pop('properties')
            ))
            return properties
        
        elif return_type == 'unparsed':
            return r
        

    
    def get_fields(self):

        params = self.base_params
        params['includeFieldPerms'] = 'false'
        return self.json_request(None,'get','fields','properties') 

    def get_reports(self):
        
        return self.json_request(
        None,
        'get',
        'reports',
        'properties'
        )  
    def get_valid_reports(self):
        return     self.reports.loc[
        self.reports['type'].eq('table'),'name'].to_list()

    def get_column_dict(self):
        pared_fields = self.field_data.loc[:,['id','label',]].copy()
        pared_fields.loc[:,'id'] = pared_fields.loc[:,'id']
        column_dict  = pared_fields.set_index('label').to_dict()['id']
        
        return column_dict 

    def get_label_dict(self):
        pared_fields = self.field_data.loc[:,['id','label',]].copy()
        pared_fields.loc[:,'id'] = pared_fields.loc[:,'id'].astype(str) + '.value'
        label_dict = pared_fields.set_index('id').to_dict()['label']
        
        return label_dict 

    def get_rename_dict(self):
        labels =list(self.label_dict.keys())
        values = list(self.label_dict.values())
        rename_dict = self.label_dict.copy()
        sub_values = [
            'name', 'id', 'email', 'userName', 'url','versions'
        ]
 
        for i  in range(0,len(labels)):
            rename_dict[
            int(f"{labels[i].replace('.value','')}")
            ] = values[i]
            rename_dict[
            f"'{labels[i].replace('.value','')}'"
            ] = int(f"{labels[i].replace('.value','')}")
            for j in range(0,len(sub_values)):
                rename_dict[
                f'{labels[i]}.{sub_values[j]}'
                ] = f'{values[i]} - {sub_values[j]}'
          
        return rename_dict
    def get_inv_label_dict(self):

        inv_label_dict = {
        v: str(k).replace('.value','') for k, v in self.label_dict.items()
        }
        return inv_label_dict
    
        


    def get_base_xml_request(self):
        request = {}
        request['encoding'] = 'UTF-8'
        request['msInUTC'] = 1
        request['realmhost'] = self.realm_hostname
        request['apptoken'] = self.user_token
        self.base_xml_request = request

    def get_base_xml_headers(self):
        self.base_xml_headers = {
        'User-Agent': '{User-Agent}',
        'Authorization': self.user_token,
        'Content-Type': 'application/xml'
        }
    
    def get_xml_url(self):
        self.xml_url = f'https://{self.realm_hostname}/db/{self.table_id}'

    def build_request(self,**request_fields):
        r"""Build QuickBase request XML with given fields. Fields can be straight
        key=value, or if value is a 2-tuple it represents (attr_dict, value), or if
        value is a list of values or 2-tuples the output will contain multiple entries.
        >>> Client._build_request(a=1, b=({}, 'c'), d=({'f': 1}, 'e'))
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<qdbapi><a>1</a><b>c</b><d f="1">e</d></qdbapi>'
        >>> Client._build_request(f=['a', 'b'])
        "<?xml version='1.0' encoding='UTF-8'?>\n<qdbapi><f>a</f><f>b</f></qdbapi>"
        >>> Client._build_request(f=[({'n': 1}, 't1'), ({'n': 2}, 't2')])
        '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<qdbapi><f n="1">t1</f><f n="2">t2</f></qdbapi>'
        """
        request = etree.Element('qdbapi')
        doc = etree.ElementTree(request)

        def add_sub_element(field, value):
            if isinstance(value, tuple):
                attrib, value = value
                attrib = dict((k, str(v)) for k, v in attrib.items())
            else:
                attrib = {}
            sub_element = etree.SubElement(request, field, **attrib)
            if not isinstance(value, str):
                value = str(value)
            sub_element.text = value

        for field, values in request_fields.items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                add_sub_element(field, value)

        return etree.tostring(doc, xml_declaration=True, encoding="utf-8")






    def xml_request(self,action,data,stream=True):
                # Do the POST request with additional QuickBase headers

        headers = self.base_xml_headers
        headers['QUICKBASE-ACTION'] = action

        response = ""
        for attempt in range(self.retries + 1):
            try:

                response = requests.post(
                self.xml_url, data, headers=headers, stream=stream
                )
                if response.status_code != 200:
                        response.raise_for_status()
            except Exception as e:

                if attempt < self.retries:
                    logger.error(e)
                    logger.info(f'Retrying  - Attempt {attempt +1}')
                    continue
                else:
                    raise
            break

        parsed = etree.fromstring(
        response.text.encode('ascii',errors='replace')
        ) 
        error_code = parsed.findtext('errcode')
        if error_code is None:
            raise ResponseError(
            -4, '"errcode" not in response', response=response
            )
        if error_code != '0':
            error_text = parsed.find('errtext')
            error_text = error_text.text if error_text is not\
            None else '[no error text]'
            raise ResponseError(error_code, error_text, response=response)


        return parsed



    def get_table_name(self):
        """Performs get schema on XML API to extract table name"""
        request = self.base_xml_request
        data = self.build_request(**request)
        response = self.xml_request('API_GetSchema', data)
        return response.xpath('//table/name')[0].text
    
    def fetch_field_info(self):
        """ Updates field information and dictionaries for translation"""
        self.field_data = self.get_fields()
        self.column_dict = self.get_column_dict()
        self.label_dict = self.get_label_dict()
        self.rename_dict = self.get_rename_dict()
        self.inv_label_dict = self.get_inv_label_dict()

    def __init__(
        self,
        table_id,
        realm_hostname=None,
        user_token=None,
        retries=3,
        dataframe=pd.DataFrame()
    ):
        self.table_id = table_id
        self.base_params = {
            'tableId': self.table_id
        }
        self.base_json_url = 'https://api.quickbase.com/v1/'

        self.check_defaults(realm_hostname,user_token)
        self.set_retries(retries)
        self.dataframe = dataframe
        self.headers = {
            'QB-Realm-Hostname': self.realm_hostname,

            'User-Agent': '{User-Agent}',
            'Authorization': self.user_token
        }
        self.get_base_xml_request()
        self.get_base_xml_headers()
        self.get_xml_url()
        self.table_name = self.get_table_name()
        self.fetch_field_info()
        self.reports = self.get_reports()
        self.valid_reports = self.get_valid_reports()
        self.merge_dicts = {}
        logger.info(f'Created Client for table "{self.table_name}"')
        
    

    

    def get_filter(self,filter_criteria,record=False):
        """Substitutes ids for labels using the quickbase query language.
        I found using field ids to be cumbersome, this translates labels
        in to field ids.

        Example: {My_Field_Label.EX.'My Value'} might become {6.EX.'My Value'}
        
        """

        pattern = re.compile(r'{(.*?)[.]')
        filter_list = []
        for m in re.finditer(pattern, filter_criteria):
            if str(m.group()).replace(
                '{',''
                ).replace('.','') not in filter_list:
                filter_list.append(str(m.group()).replace(
                '{','').replace('.','')
                )
        if record ==False:
            for k in filter_list:
                if k in filter_criteria:
                    filter_criteria = filter_criteria.replace(
                    k,str(self.inv_label_dict[k])
                    )
        else:
            for k in filter_list:
                if k in filter_criteria:
                    filter_criteria = filter_criteria.replace(
                    k,str(self.rename_dict[k])
                    )
        return filter_criteria


    def gen_filter_from_list(self,filter_list,filter_list_label):
        where_str = f'{{{filter_list_label}.EX."' 
        join_str = f'"}}OR{{{filter_list_label}.EX."'
        return f'{where_str}{join_str.join(filter_list)}"}}'
         



    

    


    def get_data(self,report=None,columns=None,all_columns=False,
    overwrite_df=True,return_copy=True,filter_list_dict=None,where=None,
    **kwargs):
        """Queries data from a quickbase table"""

        valid_kwargs = [
        'sortBy',
        'groupBy'
        ]
        body = {"from":self.table_id}
        # Without a default sort order does not behave as expected
        body['sortBy'] = [{'fieldId': 2, 'order': 'DESC'}]
        if report:
            if any([filter_list_dict,columns,all_columns,where,kwargs]):
                raise ValueError(
                'Columns,filters and kwargs can not be specified with a report'
                )
            if report not in self.valid_reports:
                raise ValueError(
                f'"{report}" is not a valid table type report for'
                f' {self.table_name}'
                )

            for k, v in self.reports.loc[
            self.reports['name'].eq(report),'query'
            ].to_dict().items():
                
                body['select'] = v['fields']
                body['where'] = self.get_filter(v['filter'],record=True)
                if len(v['sortBy']) > 0:
                    body['sortBy'] = v['sortBy']
                if len(v['groupBy']) > 0:
                    body['groupBy'] = v['groupBy']



        if columns:
            try:
                body['select'] = [self.column_dict[c] for c in columns]
            except KeyError as e:
                raise ValueError(
                f'Invalid Column {e} provided.'
                )
        if all_columns:
            body['select'] = list(self.label_dict.keys())
        if where:
            if not isinstance(filter_list_dict, type(None)):
                raise ValueError('Can not specify where with a filter list')
            if not isinstance(report, type(None)):
                raise ValueError('Can not specify where with a report')
            body['where']  = self.get_filter(where)

        

  
        invalid_kwargs = []
        for kw in kwargs:
            if kw  in valid_kwargs:
                body[kw] = kwargs[kw]
            else:
                invalid_kwargs.append(kw)

        if len(invalid_kwargs)>0:
            raise ValueError(f'Invalid Kwargs {", ".join(invalid_kwargs)}')

        if isinstance(filter_list_dict, dict):
            df_list = []
            retrieved = 0 

            for k,v in filter_list_dict.items():

                list_length = len(v)
                iter_np = np.arange(0, list_length, 100)
                iter = list(iter_np)
                for i in iter:
                    slice = _slice_list(i,v)
                    body['where'] = self.get_filter(self.gen_filter_from_list(
                    slice,
                    k)
                    )
                    df, metadata = self.json_request(
                    body,
                    'post',
                    'records',
                    'dataframe',
                    'query'
                    )
                    df_list.append(df)
                    retrieved += metadata['numRecords']

            
        else:
            df_list = []
            retrieved = 0 
            df, metadata = self.json_request(
            body,
            'post',
            'records',
            'dataframe',
            'query'
            )
            df_list.append(df)
            retrieved = metadata['numRecords']
            if metadata['totalRecords'] > metadata['numRecords']:
                body['options'] = {"skip": retrieved}
                remaining = metadata['totalRecords'] -  metadata['numRecords']
                while remaining > 0:
                    df, metadata = self.json_request(
                    body,
                    'post',
                    'records',
                    'dataframe',
                    'query'
                    )
                    retrieved += metadata['numRecords']
                    remaining = metadata['totalRecords'] - retrieved
                    body['options'] = {"skip": retrieved}
                    df_list.append(df)
                   



        result = pd.concat(df_list)
        logger.info(f'Retrieved {retrieved} records from {self.table_name}')
        result.columns = result.columns.to_series().map(self.rename_dict)
        if retrieved > 0:
            if columns:
                result = result[columns]
        if overwrite_df  == True:
            self.dataframe = result
        if return_copy == True:
            return result.copy()
        else:
            return result



    def create_fields(self,field_dict=None,external_df=None,
    ignore_errors=False, appearsByDefault=True
    ):
        """
        Creates a field. Can create based on columns in a dataframe or based on
        a field_dict of desired attributes.
        """
        type_dict = {
        'float64': 'numeric',
        'int64': 'numeric',
        'datetime64[ns]': 'datetime',
        'object': 'text',
        'bool': 'checkbox',
        'int32': 'numeric',
        'UInt32': 'numeric'
        }

        logger.info('Preparing to create fields')


        
        if field_dict:
            body = field_dict
            if appearsByDefault == False:
                body['appearsByDefault'] = False
            response = self.json_request(
            body,'post','fields','response'
            )
            logger.info(f'''Added field "{response['label']}"'''
            f' to {self.table_name}'
            )
            self.fetch_field_info()    
            return
             
        if external_df is not None:
            self.dataframe = external_df.copy()
       
        body = {}

        unknown_columns = [
            col for col in self.dataframe.columns \
            if col not in self.rename_dict.values()
        ]

        if len(unknown_columns) > 0:
            dtypes_dict = self.dataframe.dtypes.to_dict()
            unknown_dict = {
            str(k): str(v) for k, v in dtypes_dict.items(
            ) if k in unknown_columns
            }

            counter = 0
            counter_dict = {}
            for k,v in unknown_dict.items():
                counter += 1
                if v not in type_dict.keys():
                    
                    counter_dict[k] =v

            if len(counter_dict) > 0 and len(counter_dict) < len(unknown_dict):
                if ignore_errors==False and len(counter_dict) > 0:
                    error_string = ''
                    for k,v in counter_dict.items():
                        error_string += f'Column: {k} datatype: {v}\n'
                    logger.error(
                    f'Unknown Pandas datatypes:\n'
                    f'{error_string}'   
                    )
                    raise ValueError(f'Unknown Pandas datatypes:\n'
                    f'{error_string}'
                    )
                else:
                    for k,v in counter_dict.items():
                        logger.warn(
                            f'Unknown Pandas datatype {v} for column {k},'
                            f' field not created'
                        )
                        unknown_dict.pop(k)
                    for k,v in unknown_dict.items():
  
                        if appearsByDefault == False:
                            body['appearsByDefault'] = False

                        body['label'] = k
                        body['fieldType']=type_dict[v]
                        response = self.json_request(
                        body,'post','fields','response'
                        )
                        logger.info(
                        f'''Added field "{response['label']}"'''
                        f' to {self.table_name}'
                        )
                        
                    self.fetch_field_info()    
                    return
             


            elif len(counter_dict) == len(unknown_dict):
                for k,v in counter_dict.items():
                    logger.warn(
                    f'Unknown Pandas datatype {v} for column {k},'
                    f' field not created'
                    )
            else:
                for k,v in unknown_dict.items():

                    if appearsByDefault == False:
                        body['appearsByDefault'] = False

                    body['label'] = k
                    body['fieldType']=type_dict[v]
                    response = self.json_request(
                    body,'post','fields','response'
                    )
                    logger.info(
                    f'''Added field "{response['label']}"'''
                    f' to {self.table_name}'
                    )
                self.fetch_field_info()
                return         
        else:
            
            logger.info('No unknown fields found')

    def update_field(self,field_label,field_dict = None,**kwargs):
        """
        Update field attributes using field_dict or using key word arguments
        """
        valid_args = [
        "label", "noWrap", "bold", "required", "appearsByDefault",
        "findEnabled", "unique", "fieldHelp", "addToForms", "properties"
        ]
        if  not any([kwargs,field_dict]):
            raise ValueError(
            'Must provide a field dict or a key word argument'
            )
        if kwargs:
            if not all([i in valid_args  for i in kwargs]):
                inv_args = [
                '"' + str(i) + '"' for i in kwargs if i not in valid_args
                ]
                raise ValueError(
                f'Invalid argument(s) {", ".join(inv_args)}.'
                )
        if field_dict:
            if type(field_dict) != dict:
                raise TypeError("'field_dict' must be a dictionary.")
            if not all([i in valid_args  for i in field_dict]):
                inv_args = [
                '"' + i + '"' for i in field_dict if i not in valid_args
                ]
                raise ValueError(f'Invalid argument(s) {", ".join(inv_args)}.')
        
        
        if type(field_label) != str:
            raise TypeError("'label' must be a string")
        if field_label not in self.inv_label_dict.keys():
            raise ValueError(
            f'{field_label} is not a valid label for table {self.table_id}'
            )
        body = {}
        if field_dict:
            body.update(field_dict)
        body.update(kwargs)
        

        response = self.json_request(
        body,
        'post',
        'fields',
        'response',
        sub_url=f'{self.inv_label_dict[field_label]}'
        )
        
        
        logger.info(
            f'Updated field {self.inv_label_dict[field_label]} with'
            f' { {k: v for k, v in response.items() if k in body.keys()} }'
        )
        self.fetch_field_info()

    def delete_fields(self,field_labels):
        """
        Delete a list of fields. Takes in field labels.
        """

        if not isinstance(field_labels,list):
            raise ValueError('Must supply a list of field labels to delete')

        invalid_labels = [
        l for l in field_labels if l not in list(self.inv_label_dict.keys())
        ]
        if len(invalid_labels)>0:
            raise ValueError(
            f'''Invalid fieldlabel(s) "{'", "'.join(invalid_labels)}".'''
            )
        
        

        body = {}
        body['fieldIds'] = [int(self.inv_label_dict[f]) for f in field_labels]
        built_ins = [_ for _ in range(1,6)]

        entered_built_ins = [
            self.rename_dict[i] for i in body['fieldIds'] if i in built_ins
        ]
        if len(entered_built_ins) > 0:
            err_str = ", ".join([f'"{b}"' for b in entered_built_ins])
            raise ValueError(f'Built in field(s) {err_str} can not be deleted')

        response = self.json_request(body,'delete','fields','response')
        for k, v in response.items():
            if k == 'deletedFieldIds':
                t_list = [
                self.rename_dict[d] for d in v
                ]
                logger.info(f'''Deleted field(s) "{'", "'.join(t_list)}"'''
                f' from {self.table_name}')

        self.fetch_field_info() 
        

    def slice_df(self, start_line,step=5000):
        end_line = start_line + step
        slice = self.dataframe.iloc[start_line:end_line,:]
        return slice

    def post_data(self,external_df=None,step=5000, merge=None,
        create_if_missing=False, exclude_columns=None, subset=None):
        """
        Upload data to quickbase
        """

        if  isinstance(external_df, pd.DataFrame):
            self.dataframe = external_df.copy()
        if exclude_columns:
            self.dataframe.drop(labels=exclude_columns, axis=1, inplace=True)
        if subset:
            self.dataframe.drop(
            labels=[
            col for col in self.dataframe.columns
            if col not in subset and not merge],
            axis=1, inplace=True
            )

        if create_if_missing ==True:
            self.create_fields(ignore_errors=True)

        self.dataframe = self.dataframe.rename(
        columns=self.inv_label_dict
        )
        if merge:
            if merge not in self.field_data.loc[
            self.field_data['unique']==True,'label'
            ].to_list():
                raise ValueError(
                'Merge columns must be unique, check Quickbase field settings'
                )

        unknown_columns = [
        col for col in self.dataframe.columns if col
        not in self.inv_label_dict.values()
        ]

        if len(unknown_columns) >= 1:
            logger.warn(f'Discovered unknown column(s) '
            f'''"{'", "'.join(unknown_columns)}".'''
            ' Unknown columns were dropped'
            )
            self.dataframe.drop(labels=unknown_columns, axis=1, inplace=True)
        
        

        dflength = len(self.dataframe.index)
        iter_np = np.arange(0, dflength, step)
        iter = list(iter_np)
        
        
        req_total = int(np.ceil(dflength / step))
        req_nr = 1
        processed=0
        created = 0
        unchanged = 0
        updated = 0
        failed = 0
        for i in iter :
            slice = self.slice_df(i,step=step)
            logger.info(
            f'Sending Insert/ Update Records API request {req_nr} '
            f'out of {req_total}')
            df_json = slice.to_json(orient='records')
            df_json = json.loads(df_json)
            for l in df_json:
                for k,v in l.items():
                    v = str(v).replace('None','Null')
            df_json = [{key: {"value": value} for key, value in item.items(
            ) if value is not None} for item in df_json]
            data = {"to": self.table_id, "data": df_json}
            if merge:
                data["mergeFieldId"] = int(self.inv_label_dict[merge])
            
            
            response = self.json_request(
            data,
            'post',
            'records',
            'unparsed'
            )
            metadata = json.loads(response.text)['metadata']
            processed  += metadata['totalNumberOfRecordsProcessed']
            created += len(metadata['createdRecordIds'])
            unchanged += len(metadata['unchangedRecordIds'])
            updated += len(metadata['updatedRecordIds'])
      
            if response.status_code == 200:
                logger.debug(f'Request {req_nr}: 0 no error')
            elif response.status_code == 207:
                count_dict={}
                for k,v in metadata["lineErrors"].items():
                    for item in v:
                        if item not in count_dict.keys():
                            count_dict[item] = 0;
                        count_dict[item] +=1
                for k,v in count_dict.items():
                    logger.error(f'Failed to insert {v} record(s) due to {k}')
                    failed +=v

                logger.debug(
                f'Request {req_nr}: {response}'
                f' {json.dumps(response.json())} \n'
                )
            else:
                logger.error(f'Failed to insert request {req_nr}. '
                 'Check debug logs for reason if enabled')

                logger.debug(f'Request {req_nr}: {response}' 
                f'{json.dumps(response.json())["description"]} \n')
            req_nr += 1
        

        logger.info(f'Uploaded {processed} records to {self.table_name}, '
        f'created: {created}, unchanged: {unchanged}, updated: {updated}, '
        f'failed: {failed}'
        )

    def delete_records(self,where=None,all_records=False):
        if where == None:
            if all_records == False:
                raise ValueError(
                'Must specify records to delete'
                )
        if all_records == True:
             body = {
            "from": self.table_id,
            "where": '{3.GT.0}'
            }
        elif where:
            body ={
            "from": self.table_id,
            "where":  f"{self.get_filter(where)}"
            }
                
            

        response = self.json_request(
        body,
        'delete',
        'records',
        'response'
        )

        logger.info(
        f'Deleted {response["numberDeleted"]} records from {self.table_name}'
        )





    def get_merge_dict(self,merge_field,try_internal):
        """
        Translation function for uploading files
        """


        record_label = self.field_data.loc[
        self.field_data['id']==3,
        'label'
        ].to_string(index=False)
        if merge_field == record_label:
            if record_label in self.dataframe.columns:
                self.merge_dicts[merge_field]  = dict(zip(
                self.dataframe[record_label].to_list(),
                self.dataframe[record_label].to_list()
                ))
                logger.debug(
                f'Created merge dict for {merge_field}'
                )
                return
            else:
                logger.info(
                'Downloading required fields to upload files'
                )
                merge_df = self.get_data(
                columns=[record_label],
                overwrite_df=False,
                return_copy=True
                )
                self.merge_dicts[merge_field]  = dict(zip(
                merge_df[record_label].to_list(),merge_df[record_label].to_list()
                ))
                logger.debug(
                f'Created merge dict for {merge_field}'
                )
                return
        


        if try_internal:
            if merge_field and record_label in self.dataframe.columns:
                self.merge_dicts[merge_field]  = dict(zip(
                self.dataframe[merge_field].to_list(),
                self.dataframe[record_label].to_list()
                ))
                logger.debug(
                f'Created merge dict for {merge_field}'
                )
                return
        logger.info(
        'Downloading required fields to upload files'
        )
        merge_df = self.get_data(
        columns=[merge_field,record_label],
        overwrite_df=False,
        return_copy=True
        )
        self.merge_dicts[merge_field]  = dict(zip(
        merge_df[merge_field].to_list(),merge_df[record_label].to_list()
        ))
        logger.debug(
        f'Created merge dict for {merge_field}'
        )
        
 


            
    def upload_files(self,field_label, file_dict,
    merge_field,try_internal=True):
        """
        Upload files to existing records, merging on a value in a unique field.
        file_dict is a dictionary  setup like so :
        {'*Filename with extension*':
         {
            'merge_value': '*The value you are merging on*',
            'file_str': '*Base64 encoded string of your file*'
         }
        }
        The merge field is provided separately as the label of the field.
        """
    
        request = self.base_xml_request
        if merge_field not in self.field_data.loc[
        self.field_data['unique']==True,'label'
        ].to_list():
                raise ValueError(
                'Invalid merge field. Merge field must exist in the table'
                ' and be unique, check Quickbase field settings'
                )
       
        if merge_field not in self.merge_dicts.keys():
            self.get_merge_dict(merge_field,try_internal)
        
        uploaded_files = 0
        for k, v in file_dict.items():
            try:
                request['rid'] = self.merge_dicts[merge_field][v['merge_value']]
            except KeyError:
                raise ValueError(
                f'"{v["merge_value"]}" not a valid value in {merge_field}'
                )
            request_field = (
            {'fid': self.inv_label_dict[field_label],
                'filename': k}, v['file_str'])
            request['field'] = [request_field]

            data = self.build_request(**request)
            response = self.xml_request('API_EditRecord',data)
            uploaded_files +=1
        
        logger.info(f'Uploaded {uploaded_files} files to {self.table_name}')
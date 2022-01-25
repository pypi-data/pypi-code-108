from abc import ABC, abstractmethod
from ecmind_blue_client.options import Options
from .query_condition_group import QueryConditionGroup
from .query_condition_field import QueryConditionField
from .query_result_field import QueryResultField
from typing import Iterator, Optional, Any, List, Dict, Union
from XmlElement import XmlElement
from .job import Job
from .result import Result
from .result_file import ResultFile
from .const import *
from .param import Param, ParamTypes
from datetime import datetime
import logging

log = logging.getLogger(__name__)
class Client(ABC):

    @abstractmethod
    def execute(self, job:Job) -> Result:
        """Send a job to the blue server, execute it and return the response.

        Keyword arguments:
        job -- A previously created Job() object.
        """
        raise NotImplemented
    
    def get_object_type_by_id(self, object_id:int) -> int:
        """Helper function: Execute the dms.GetObjectTypeByID job for a given object id and return the objects type id.

        Keyword arguments:
        object_id -- A folder, register or document id.
        """
        job = Job('dms.GetObjectTypeByID', Flags=0, ObjectID=object_id)
        return self.execute(job).values['ObjectType']


    def store_in_cache(self, object_id:int, object_type_id:int=None, checkout:bool=False) -> List[ResultFile]:
        """Helper function: Execute the std.StoreInCache job for a given object to retrieve its files.

        ### Keyword arguments:

        - object_id -- A document id.
        - object_type_id -- (Optional) The documents type id. When not provided, it is retrieve via get_object_type_by_id() first.
        - checkout -- (Optional) When True, change the documents state to checked out on the server.

        ### Warning

        Known bug: Throws an enaio error on archived documents. 
        """
        if object_type_id == None:
            object_type_id = self.get_object_type_by_id(object_id)

        job = Job('std.StoreInCache',
            Flags=1,
            dwObjectID=object_id,
            dwObjectType=object_type_id,
            DocState=(0 if checkout else 1),
            FileCount=0
        )
        result = self.execute(job)
        if result.return_code != 0:
            raise(RuntimeError(f'Received return code {result.return_code}: {result.error_message}'))

        return result.files


    def store_in_cache_by_id(
        self, object_id:int, convert:StoreInCacheByIdConversion=StoreInCacheByIdConversion.NONE) -> List[ResultFile]:
        """Helper function: Execute the std.StoreInCacheById job for a given object to retrieve/convert its files.

        ### Keyword arguments:

        - object_id -- A document id.
        - convert -- (Optional) Convert 
           - main type 1, 2, 3 or 4 to PDF with StoreInCacheByIdConversion.PDF 
           - main type 2 or 3 with StoreInCacheByIdConversion.MULTIPAGE_TIFF
        """

        job = Job('std.StoreInCacheById',
            Flags=1,
            dwObjectID=object_id,
            Convert=convert.value
        )

        result = self.execute(job)
        if result.return_code != 0:
            raise(RuntimeError(f'Received return code {result.return_code}: {result.error_message}'))

        return result.files


    def xml_import(self,
                  object_name:str,
                  search_fields:Dict[str, str],
                  import_fields:Dict[str, str],
                  table_fields:Dict[str, List[Dict[str, Any]]]=None,
                  folder_id:int=None,
                  register_id:int=None,
                  object_id:int=None,
                  options:Union[Options, str]='',
                  action0:ImportActions=ImportActions.INSERT,
                  action1:ImportActions=ImportActions.UPDATE,
                  actionM:ImportActions=ImportActions.ERROR,
                  files:List[str]=[],
                  main_type:Union[MainTypeId, int, None]=None,
                  variant_parent_id:int=None
        ):
        """Helper function: Execute the dms.XMLImport job.

        ### Keyword arguments
        
        - `object_name` -- The internal name of the object type to import.
        - `search_fields` -- Dict of internal field names and values. If one or more objects match all `search_fields`, the `action1` or `actionM` will be used, `action0` otherwise. 
        - `import_fields` -- Dict of internal field names and (new) values.
        - `table_fields` -- Dict of internal table field names and list of new rows as dicts of internal column name and values.
        - `folder_id` -- (Optional) Folder id to import registers or documents into.
        - `register_id` -- (Optional) Register id to import sub-registers or documents into.
        - `object_id` -- (Optional) Objekt id to force an update of this element. 
        - `options` -- (Optional) Semicolon separated string of import options.
        - `action0` -- (Optional) `ImportActions` Enum element defining how to handle imports when the search_fields do not match any pre-existing objects.
        - `action1` -- (Optional) `ImportActions` Enum element defining how to handle imports when the search_fields do match exactly one pre-existing object.
        - `actionM` -- (Optional) `ImportActions` Enum element defining how to handle imports when the search_fields do match more then one pre-existing object.
        - `files` -- (Optional) List of strings containing file path to import into a document object.
        - `main_type` -- (Optional) Set the main type id for document imports or leave empty for default value. Valid ids are `DOC_GRAYSCALE`/`1`, `DOC_BW`/`2`, DOC_COLOR`3`, `DOC_WINDOWS`/`4`, `DOC_MULTIMEDIA`/`5`, `DOC_MAIL`/`6`, `DOC_XML`/`7`, `DOC_CONTAINER`/`8`.
        - `variant_parent_id` -- (Optional) Set the parent id for document variant imports. `search_fields` must be empty when `variant_parent_id` is set.
        """

        object_element = XmlElement('Object', 
            s=[ XmlElement(
            'Search', s=[ search_fields_element := XmlElement('Fields') ]), 
            import_fields_element := XmlElement('Fields') 
        ])

        if main_type and isinstance(main_type, MainTypeId):
            object_element.set('maintype', str(main_type.value))
        elif main_type:
            object_element.set('maintype', str(main_type))

        if variant_parent_id:
            if len(search_fields) > 0:
                raise ValueError('search_fields must be empty when variant_parent_id is set.')
            search_fields = { SystemFields.OBJECT_ID.name: '-1' }
            object_element.set('variantparent_id', str(variant_parent_id))
        
        xml = XmlElement('DMSData', s=[
                XmlElement('Archive', s=[
                    XmlElement('ObjectType', {'internal_name': object_name}, [object_element])
                ])
        ])
        
        folder_id and object_element.set('folder_id', str(folder_id))
        register_id and object_element.set('register_id', str(register_id))
        object_id and object_element.set('object_id', str(object_id))

        for field_internal_name, field_value in search_fields.items():
            field = XmlElement('Field', a={'internal_name': field_internal_name}, t=field_value)
            if field_internal_name in SystemFields._member_names_:
                field.set('system', '1')
            search_fields_element.append(field)

        for field_internal_name, field_value in import_fields.items():
            field = XmlElement('Field', a={'internal_name': field_internal_name}, t=field_value)
            if field_internal_name in SystemFields._member_names_:
                field.set('system', '1')
            import_fields_element.append(field)

        if table_fields != None and len(table_fields):
            object_element.append(table_fields_element := XmlElement('TableFields'))
            for table_field_internal_name, table_field_rows in table_fields.items():
                table_field = XmlElement('TableField', {'internal_name': table_field_internal_name})
                table_fields_element.append(table_field)
                for table_field_row in table_field_rows:
                    table_field.append(XmlElement('Row', s=[ XmlElement(
                        'Field', {'internal_name': table_row_field_internal_name}, t=table_row_field_value) \
                            for table_row_field_internal_name, table_row_field_value in table_field_row.items()
                    ]))

        job = Job('dms.XMLImport', Flags=0, Options=str(options), 
            Action0=action0.value, Action1=action1.value, ActionM=actionM.value, 
            files=files, Encoding='UTF-8', XML=xml
        )

        return self.execute(job)

    def get_object_details(self, object_name:str, object_id:int, system_fields:Optional[List[SystemFields]]=[]) -> dict:
            query_fields = []
            for system_field in system_fields:
                query_field = XmlElement('Field', {'internal_name': system_field.name, 'system': '1'})
                query_fields.append(query_field)

            query_xml = XmlElement('DMSQuery', {}, [
                XmlElement('Archive', {} , [
                    XmlElement('ObjectType', {'internal_name': object_name}, [
                        XmlElement('Fields', {'field_schema': 'ALL'}, query_fields),
                        XmlElement('Conditions', {}, [
                            XmlElement('ConditionObject', {'internal_name': object_name}, [
                                XmlElement('FieldCondition', {'internal_name': SystemFields.OBJECT_ID.name, 'operator': '=', 'system': '1'}, [
                                    XmlElement('Value', t=str(object_id))
                                ])
                            ])
                        ])
                    ])
                ])
            ])

            job = Job('dms.GetResultList', Flags=0, Encoding='UTF-8', RequestType='HOL', XML=query_xml)
            result = self.execute(job)
            if result.return_code != 0:
                raise(Exception(f'Failed with error code: {result.return_code}'))

            if result.values['Count'] == 0:
                return {}

            result_xml = XmlElement.from_string(result.values['XML'])
            obj_xml = result_xml['Archive'][0]['ObjectType'][0]['ObjectList'][0]['Object'][0]

            result = {}
            for field in obj_xml['Fields'][0]['Field']:
                result[field.attributes['internal_name']] = field.text

            table_fields = obj_xml.find('TableFields')
            if table_fields:
                for table_field in table_fields['TableField']:
                    table_field_result = []
                    cols = [ col.attributes['internal_name'] for col in table_field['Columns'][0]['Column'] ]
                    for row in table_field.findall('Row'):
                        row_result = {}
                        for i, col in enumerate(cols):
                            row_result[col] = row.subelements[i].text
                        table_field_result.append(row_result)

                    result[table_field.attributes['internal_name']] = table_field_result

            return result

    def execute_sql(self, sql_command:str) -> Union[List[Dict[str, str]], None]:
        """Helper function: Execute a sql command via ADO.

        Keyword arguments:
        
        - sql_command -- The sql command.

        Returns:
        
        - For SELECT statements: `List[Dict]` -- The list of records with each row as dictionary of column name and string-value
        - For other statements: `None`
        """
        
        job = Job('ado.ExecuteSQL', Flags=0, Command=sql_command.strip())
        result = self.execute(job)
        if result.return_code != 0:
            raise Exception(f'Failed with error code: {result.return_code}')

        if result.files:
            xml_result = XmlElement.from_string(result.files[0].bytes().decode('UTF-8'))
            data = [ row.attributes for row in xml_result['{urn:schemas-microsoft-com:rowset}data'][0]['{#RowsetSchema}row'] ]
            return data
        else:
            return None

    def lol_query(self,
                        object_name:str, 
                        conditions:Union[QueryConditionGroup, List[QueryConditionGroup]]=None,
                        result_fields:Union[str, SystemFields, QueryResultField, List[Union[str, SystemFields, QueryResultField]]]=None,
                        offset:int=0,
                        page_size:int=1000,
                        max_hits:Union[int, None]=None,
                        include_file_info:bool=False,
                        follow_doc_links:bool=False,
                        include_status:bool=False,
                        garbage_mode:bool=False,
                        context_user:str=None
        ) -> Iterator[Dict[str, Any]]:
        """Helper function: Page through dms.GetResultList in LOL format, yielding dicts of result fields for each hit.

        Keyword arguments:
        object_name -- The internal name of the object type to import.
        result_fields -- List of internal field names, SystemField instances or QueryField instances (for sorting). 
        offset -- (Optional) int defining the query offset, default = 0.
        page_size -- (Optional) int defining the query page size, default = 1000.
        max_hits -- (Optional) int|None limiting the querys maximum yield, default = None.
        include_file_info -- (Optional) bool indicating, if file size, file extension and mime type should be added to document results, default = False.
        follow_doc_links -- (Optional) bool indicating, the include_file_info returns the data of referenced files ("green arrows"), default = False.
        include_status -- (Optional) bool indicating, if status field should be added to the result, default = False.
        garbage_mode -- (Optional) bool indicating, if the query searches the recycle bin instead of non-deleted objects, default = False.
        context_user -- (Optional) string to change the job context to another user name.
        """        

        if conditions and isinstance(conditions, list):
            conditions_element = XmlElement('Conditions', {}, [ x.to_xml_element() for x in conditions ])
        elif conditions:
            conditions_element = XmlElement('Conditions', {}, [ conditions.to_xml_element() ])
        else:
            conditions_element = XmlElement('Conditions')

        if result_fields and len(result_fields) > 0:
            fields_element = XmlElement('Fields', {'field_schema': 'DEF'})
            for result_field in result_fields if isinstance(result_fields, list) else [ result_fields ]:
                if isinstance(result_field, QueryResultField):
                    fields_element.append(result_field.to_xml_element())
                else:
                    fields_element.append(QueryResultField(result_field).to_xml_element())

        else:
            fields_element = XmlElement('Fields', {'field_schema': 'ALL'})

        query_xml = XmlElement('DMSQuery', {}, [
            XmlElement('Archive', {} , [
                XmlElement('ObjectType', {'internal_name': object_name}, [
                    fields_element, conditions_element
                ])
            ])
        ])

        job = Job('dms.GetResultList', 
                    Flags=0, 
                    Encoding='UTF-8', 
                    RequestType='LOL',
                    XML=query_xml,
                    MaxHits=max_hits,
                    PageSize=page_size,
                    Offset=offset,
                    DateFormat='%Y-%m-%d', # %z,
                    FileInfo=1 if include_file_info else 0,
                    FollowDocLink=1 if follow_doc_links else 0,
                    Status=1 if include_status else 0,
                    GarbageMode=1 if garbage_mode else 0,
                )
        if context_user:
            job.append(Param('$$$SwitchContextUserName$$$', ParamTypes.STRING, context_user))

        current_offset = offset
        combined_count = 0
        columns = None
        while (not max_hits) or (combined_count <= max_hits):
            result = self.execute(job)
            if result.return_code != 0:
                raise RuntimeError(f'enaio error {result.return_code}: {result.error_message}')
            combined_count += result.values['Count']
            if result.values['TotalHits'] == 0:
                logging.debug(f'Query returned no result objects. Finished.')
                return

            archive = XmlElement.from_string(result.values['XML'])['Archive'][0]
            objecttype = archive['ObjectType'][0]
            rowset = objecttype['Rowset'][0]

            if not columns:
                columns = { column.attributes['internal_name']: column.attributes['datatype'] for column in rowset['Columns'][0]['Column'] }

            for row in rowset['Rows'][0]['Row']:
                yield_result = {}

                #Add common fields form Archive and ObjectType tag
                yield_result['OBJECT_FOLDER_TYPE_ID'] = archive.attributes['id']
                yield_result['OBJECT_TYPE_ID'] = objecttype.attributes['id']
                yield_result['OBJECT_MAINTYPE'] = objecttype.attributes['maintype']
                yield_result['OBJECT_COTYPE'] = objecttype.attributes['cotype']
                yield_result['OBJECT_INTERNAL_NAME'] = objecttype.attributes['internal_name']
                yield_result['OBJECT_TYPE'] = objecttype.attributes['type']
                yield_result['OBJECT_TABLE'] = objecttype.attributes['table']

                for name, value in zip(columns, row['Value']):
                    datatype = columns[name]
                    if datatype == 'TEXT':
                        # Value attribute of system fields or text value
                        yield_result[name] = value.attributes['value'] if 'value' in value.attributes else value.text
                    elif datatype == 'INTEGER':
                        # Text value of status fields or integer value of text value or None
                        yield_result[name] = value.text if 'value' in value.attributes else int(value.text) if value.text else None
                    elif datatype == 'DECIMAL': 
                        yield_result[name] = float(value.text) if value.text else None
                    elif datatype == 'DATE': 
                        yield_result[name] = datetime.strptime(value.text, '%Y-%m-%d').date() if value.text else None
                    elif datatype == 'DATETIME': 
                        yield_result[name] = datetime.strptime(value.text, '%Y-%m-%d %H:%M:%S') if value.text else None
                    else:
                        yield_result[name] = value.text
                    
                yield yield_result

            if page_size > result.values['Count']:
                logging.debug(f'Last query reached end of result rows. Finished')
                return

            if max_hits and (max_hits - combined_count == 0):
                logging.debug(f'Max hits reached. Finished')
                return 
            elif max_hits and (max_hits - combined_count < page_size):
                job.update(Param('PageSize', ParamTypes.INTEGER, max_hits - combined_count))

            current_offset += page_size
            job.update(Param('Offset', ParamTypes.INTEGER, current_offset))
            logging.debug(f'Paging to next result frame with offset {current_offset} after {combined_count} combined hits.')

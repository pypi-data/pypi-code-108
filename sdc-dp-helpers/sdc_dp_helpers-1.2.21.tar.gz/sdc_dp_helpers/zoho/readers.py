import os
import time

from zcrmsdk import ZCRMRestClient, ZCRMException
from zcrmsdk.OAuthClient import ZohoOAuth
from zcrmsdk.Operations import ZCRMModule

from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.api_utilities.retry_managers import request_handler
from sdc_dp_helpers.zoho.writers import CustomS3JsonWriter


class CustomZohoReader:
    """
        Custom Zoho Reader
    """

    def __init__(self, **kwargs):
        self.config = load_file(kwargs.get('config_path', None), 'yaml')
        self.creds = load_file(kwargs.get('creds_path', None), 'yaml')

        self.zoho_token = self.initialize_zoho_client()
        self.partial_pull = self.config.get('partial_pull', True)
        self.partial_pull_size = self.config.get('partial_pull_size', 5)

        self.module = self.config.get('module')

        self.writer = CustomS3JsonWriter(
            bucket=kwargs.get('bucket')
        )

    def initialize_zoho_client(self):
        """
        Zoho Client will be creating local auth and log files every time it is run.
        This method handles the directories and environments as well as the OAth Client.
        """
        # create file for app log without needing root and OS dependency
        try:
            os.mkdir(f"{os.getcwd()}/{self.creds.get('application_log_file_path').replace('./', '')}")
            log_file_path = f"{os.getcwd()}/{self.creds.get('application_log_file_path').replace('./', '')}/{'client_library.log'}"
            if not os.path.exists(log_file_path):
                with open(log_file_path, 'a') as _file:
                    _file.write('')
        except FileExistsError:
            pass

        config = {
            'sandbox': self.creds.get('sandbox'),
            'applicationLogFilePath': self.creds.get('application_log_file_path'),  # a local log file is needed
            'client_id': self.creds.get('client_id'),
            'client_secret': self.creds.get('client_secret'),
            'redirect_uri': self.creds.get('redirect_uri'),  # this can be totally random
            'accounts_url': self.creds.get('accounts_url'),
            'token_persistence_path': self.creds.get('token_persistence_path'),
            'currentUserEmail': self.creds.get('current_user_email')
        }

        ZCRMRestClient.initialize(config)
        return ZohoOAuth.get_client_instance()

    @staticmethod
    def match_keys(field_name, record):
        """
        Find keys in record and map them.
        """
        for key in record.keys():
            if field_name.lower() == key.lower():
                return key
        return False

    @staticmethod
    @request_handler(wait=0.2, backoff_factor=0.5, backoff_method='random')
    def record_response_handler(row, record):
        """
        Handle response data and add missing data to suit
        business requirements.
        """
        record['entity_id'] = row.entity_id

        if row.created_by is not None:
            record['created_by_id'] = row.created_by.id
        else:
            record['created_by_id'] = 'null'

        if row.modified_by is not None:
            record['modified_by_id'] = row.modified_by.id
        else:
            record['modified_by_id'] = 'null'

        if row.modified_by is not None:
            record['modified_by'] = row.modified_by.name
        else:
            record['modified_by'] = 'null'

        if row.modified_time is not None:
            record['modified_time'] = row.modified_time
        else:
            record['modified_time'] = 'null'

        if row.created_by is not None:
            record['created_by'] = row.created_by.name
        else:
            record['created_by'] = 'null'

        if row.layout is not None:
            record['layout'] = row.layout.name
        else:
            record['layout'] = 'null'

        if row.layout is not None:
            record['layout_id'] = row.layout.id
        else:
            record['layout_id'] = 'null'

        record['owner_id'] = row.owner.id
        record['owner'] = row.owner.name
        record['created_time'] = row.created_time

        return record

    def record_run_query(self):
        """
        Run Zoho Client Query for Records based on module.
        """
        oauth_client = self.initialize_zoho_client()
        oauth_client \
            .generate_access_token_from_refresh_token(
            self.creds.get('refresh_token'),
            self.creds.get('current_user_email')
        )

        module_instance = ZCRMModule.get_instance(self.module)
        all_fields = module_instance.get_all_fields().data

        page, per_page = 1, 200
        module_response = module_instance.get_records(None, 'Modified_Time', 'desc', page, per_page)
        try:
            if self.partial_pull:
                while page <= self.partial_pull_size:  # this is a partial pull
                    loop_count = 1
                    data_set = []
                    for row in module_response.data:
                        print(f'At loop: {loop_count}, and page: {page}.')
                        record = {}
                        for field in all_fields:
                            name = field.api_name
                            value = row.get_field_value(field.api_name)
                            record[name.lower()] = value
                        data_set.append(
                            self.record_response_handler(row, record)
                        )
                        loop_count += 1

                    # write each page as a partition and clean data_set
                    print('Writing to S3.')
                    self.writer.write_to_s3(
                        json_data=data_set, config=self.config, partition=page, layout='records'
                    )
                    page += 1

                print("No more data to import.")

            else:
                loop_count = 1
                data_set = []
                for row in module_response.data:
                    print(f'At loop: {loop_count}, and page: {page}.')
                    record = {}
                    for field in all_fields:
                        name = field.api_name
                        value = row.get_field_value(field.api_name)
                        record[name.lower()] = value
                    data_set.append(
                        self.record_response_handler(row, record)
                    )
                    loop_count += 1

                # write entire set as single partition
                print('Writing to S3.')
                self.writer.write_to_s3(
                    json_data=data_set, config=self.config, partition=0, layout='records'
                )
                page += 1

        except ZCRMException as ex:
            if ex.status_code == 204:
                print("No more data to import.")

        finally:
            return None

    def layouts_response_handler(self, module_object, layout, record):
        if self.module == "Products":
            record['layout_id'] = layout.id
            record[self.module + '_id'] = module_object.entity_id
            record['owner_id'] = module_object.owner.id
            record['owner_name'] = module_object.owner.name
            record['created_time'] = module_object.created_time
            record['created_by'] = module_object.created_by.name
            record['created_by_id'] = module_object.created_by.id
        elif self.module != "Products":
            record['layout_id'] = layout.id
            record[self.module + '_id'] = module_object.entity_id
            record['owner_id'] = module_object.owner.id
            record['owner_name'] = module_object.owner.name
            record['created_time'] = module_object.created_time
            record['created_by'] = module_object.created_by.name
            record['created_by_id'] = module_object.created_by.id
            record['modified_time'] = module_object.modified_time
            record['modified_by'] = module_object.modified_by.name
            record['modified_by_id'] = module_object.modified_by.id

            try:
                record['last_activity_time'] = module_object.last_activity_time
            except:
                print("The last_activity_time is not available.")

            if self.module == "Deals":
                res = []
                for stage_record in module_object.get_relatedlist_records('Stage_History').data:
                    res.append(stage_record.field_data)
                record['Stage_History'] = res

        return record

    def layouts_run_query(self):
        oauth_client = self.initialize_zoho_client()
        oauth_client \
            .generate_access_token_from_refresh_token(
            self.creds.get('refresh_token'),
            self.creds.get('current_user_email')
        )

        module_instance = ZCRMModule.get_instance(self.module)
        all_layouts = module_instance.get_all_layouts()

        for layout in all_layouts.data:
            if layout.id:
                # re-declare field_list for use in insert statement
                field_list = ['layout_id', self.module + '_ID', 'Owner_ID', 'Owner_Name']
                problem_fields = ['Tag', 'Description']
                if self.module == 'Deals':
                    field_list.append('Stage_History')
                elif self.module == 'Activities':
                    problem_fields = ['Tags']

                # fetch fields by section inside the current layout
                for section in layout.sections:
                    if section is not None:
                        for field in (section.fields if section.fields is not None else []):
                            if field.api_name not in problem_fields:
                                field_list.append(field.api_name)

                page, per_page = 1, 200
                module_response = module_instance.get_records(None, 'Modified_Time', 'desc', page, per_page)
                try:
                    if self.partial_pull:
                        data_set = []
                        while page <= self.partial_pull_size:  # this is a partial pull
                            loop_count = 1
                            print(f'At loop: {loop_count}, and page: {page}.')
                            for module_object in module_response.data:
                                record = module_object.field_data

                                record = self.layouts_response_handler(
                                    module_object, layout, record
                                )

                                for field_name in field_list:
                                    if field_name not in record.keys():
                                        try:
                                            field_value = module_object.field_name
                                        except:
                                            field_value = module_object.get_field_value(field_name)
                                        key_found = self.match_keys(field_name.lower(), record)
                                        if not key_found:
                                            record[field_name] = field_value

                                data_set.append(record)
                                loop_count += 1

                            # write each page as a partition and clean data_set
                            print("Writing to s3.")
                            self.writer.write_to_s3(
                                json_data=data_set, config=self.config, partition=page, layout='layouts'
                            )
                            data_set = []

                            page += 1
                            # get_records dies very easily if overused, so permanent sleep method is recommended
                            time.sleep(1)
                            print('Waiting for 1 second.')

                        print("No more data to import.")

                    else:
                        # we can only run while no errors occur, else the API shuts down.
                        data_set = []
                        while 200 <= module_response.status_code < 300:
                            loop_count = 1
                            print(f'At loop: {loop_count}, and page: {page}.')
                            for module_object in module_response.data:
                                record = module_object.field_data

                                record = self.layouts_response_handler(
                                    module_object, layout, record
                                )

                                for field_name in field_list:
                                    if field_name not in record.keys():
                                        try:
                                            field_value = module_object.field_name
                                        except:
                                            field_value = module_object.get_field_value(field_name)
                                        key_found = self.match_keys(field_name.lower(), record)
                                        if not key_found:
                                            record[field_name] = field_value

                                data_set.append(record)
                                loop_count += 1
                            page += 1

                            # get_records dies very easily if overused, so permanent sleep method is recommended
                            time.sleep(20)
                            print('Waiting for 20 seconds.')

                        print("Writing to s3.")
                        self.writer.write_to_s3(
                            json_data=data_set, config=self.config, partition=0, layout='layouts'
                        )

                        print("No more data to import.")

                except ZCRMException as ex:
                    if ex.status_code == 204:
                        print("No more data to import.")

                finally:
                    return None

            else:
                print('No list id, skipping.')

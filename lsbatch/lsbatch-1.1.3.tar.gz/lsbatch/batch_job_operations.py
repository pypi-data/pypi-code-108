import configparser
import json
import os
import pathlib
import re

from lsbatch.log import Log
from lsbatch.requests_handler import RequestHandler
from lsbatch.constants import Messages, ValidationMessages, Constants
from lsbatch.helper import Helper


class BatchJobOperations:
    def __init__(self):
        pass

    __file_path = pathlib.Path(__file__).resolve()

    @classmethod
    def lsbatch_save(cls, script_path, save_setting=False):
        if Helper.validate_lsbatch_pack(script_path):
            batch_details = Helper.retrieve_batch_details(script_path)
            if batch_details is None:
                return
            is_code_uploaded = False
            if not (batch_details.get("Id", "").strip() == ""):
                is_code_uploaded = cls.__upload_code(script_path, batch_details["Id"])
            else:
                if cls.__create_batch(script_path, batch_details):
                    is_code_uploaded = cls.__upload_code(script_path, batch_details["Id"])
            if is_code_uploaded and save_setting:
                cls.__save_settings(script_path, batch_details["Id"])
        else:
            return

    @classmethod
    def lsbatch_publish(cls, script_path):
        Log.started(Messages.PublishingBatchJob)
        batch_details = Helper.retrieve_batch_details(script_path)
        if batch_details is None:
            return
        batch_id = batch_details.get("Id", "").strip()
        if batch_id == "":
            Log.error(ValidationMessages.IdNotFoundWhilePublishing)
            return
        response = RequestHandler.publish_batch(batch_id)
        return cls.__handle_response(response, Messages.BatchJobPublished)

    @classmethod
    def lsbatch_configure(cls):
        credentials_list = [Constants.OrgCode, Constants.Token, Constants.Region]
        credentials = {}
        for cred in credentials_list:
            Log.question(f"{cred} (mandatory) : ")
            credentials[cred] = input().strip()
        Log.question(f"profile-name (default: {{{Constants.OrgCode}}}): ")
        profile_name = input().strip()
        message = Helper.validate_credentials(credentials)
        if message is not None:
            Log.error(message)
            return
        if profile_name == "":
            profile_name = credentials[Constants.OrgCode]
        existing_configuration = cls.retrieve_configuration()
        update_profile = None
        if profile_name in existing_configuration:
            Log.question(Messages.ProfileAlreadyExists)
            update_profile = input().strip().lower()
        if update_profile is None or update_profile == 'y':
            existing_configuration[profile_name] = credentials
            cls.update_configuration(existing_configuration)
            Log.info(Messages.ProfileAddedSuccessfully)

    @classmethod
    def update_configuration(cls, configuration):
        if configuration is not None:
            config_file_path = os.path.join(cls.__file_path.parent, 'config.cfg')
            with open(config_file_path, 'w') as config_file:
                configuration.write(config_file)

    @classmethod
    def retrieve_configuration(cls, profile_name=None):
        config = configparser.ConfigParser()
        config.read(os.path.join(cls.__file_path.parent, 'config.cfg'))
        if profile_name is not None:
            if profile_name in config:
                return dict(config[profile_name])
        else:
            return config

    @classmethod
    def __create_batch(cls, script_path, batch_detail):
        Log.started(Messages.CreatingNewBatchJob)
        name = batch_detail.get("Name", "").strip()
        validation_message = None
        if not name == "":
            validation_message = cls.__validate_batch_job_name(name)
            if validation_message:
                Log.error(validation_message, 'batch_details.json')
        if name == "" or validation_message is not None:
            name = cls.__get_batch_job_name()
            batch_detail["Name"] = name
        description = batch_detail.get("Description", "").strip()
        if len(description) > 1000:
            Log.error(ValidationMessages.LengthOfDescription, 'batch_details.json')
        if description == "" or len(description) > 1000:
            description = cls.__get_batch_description()
            if not description == "":
                batch_detail["Description"] = description
        response = RequestHandler.create_batch(name, description)
        result = cls.__handle_response(response, Messages.BatchJobCreated)
        if result:
            batch_detail["Id"] = response["Data"]["BatchJobName"]
            Helper.update_batch_details(script_path, batch_detail)
        return result

    @classmethod
    def __get_batch_job_name(cls):
        while True:
            Log.question(Messages.YourBatchName)
            batch_job_name = input()
            validation_message = cls.__validate_batch_job_name(batch_job_name)
            if validation_message is None:
                return batch_job_name
            Log.error(validation_message)

    @classmethod
    def __get_batch_description(cls):
        Log.question(Messages.WantToProvideDescription)
        provide_description = input()
        if provide_description.lower() == 'y':
            while True:
                Log.info(Messages.ProvideDescription)
                description = input()
                if len(description) <= 1000:
                    return description
                Log.error(ValidationMessages.LengthOfDescription)
        return ""

    @classmethod
    def __validate_batch_job_name(cls, name):
        message = None
        if name is None or len(name) < 3 or len(name) > 100:
            message = ValidationMessages.LengthOfJobName
        elif not re.match("(^([a-zA-Z0-9]+)([a-zA-Z0-9 _-]*))$", name):
            message = ValidationMessages.NameShouldNotHaveSpecialCharacters
        return message

    @classmethod
    def __upload_code(cls, script_path, batch_id):
        Log.started(Messages.UploadingBatchFile.format(batch_id))
        Helper.zip_source_code(script_path)
        file_name = f"code.zip"
        batch_job_zip = os.path.join(script_path, 'deliverables', file_name)
        bytes_buffer = Helper.convert_file_to_bytes(batch_job_zip)
        response = RequestHandler.upload_zip(batch_id, bytes_buffer, file_name)
        return cls.__handle_response(response, Messages.BatchFileUploaded)

    @classmethod
    def __save_settings(cls, script_path, batch_id):
        Log.started(Messages.UpdatingSettings)
        settings = {}
        settings_file_path = os.path.join(script_path, 'settings.json')
        if os.path.exists(settings_file_path):
            with open(settings_file_path, 'r') as file:
                try:
                    settings = json.loads(file.read())
                except Exception:
                    print(f"ERROR : {ValidationMessages.SettingsFileNotInFormat}")
        if len(settings) > 0:
            settings_list = [{"Key": key, "Value": settings.get(key)} for key in settings]
            response = RequestHandler.save_settings(batch_id, settings_list)
            return cls.__handle_response(response, Messages.SettingsUpdated)
        else:
            Log.completed(Messages.NoSettingsFound)
            return True

    @classmethod
    def __handle_response(cls, response, success_msg):
        if response.get("Status") == "Failed":
            Log.error(f'ExceptionType: {response.get("ExceptionType")}, Message: {response.get("Message")}')
            return False
        Log.completed(success_msg)
        return True

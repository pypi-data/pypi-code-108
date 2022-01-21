import io
import json
import os
import shutil
import sys
import time
import threading

from lsbatch.constants import ValidationMessages, ALLOWED_REGIONS, Constants
from lsbatch.log import Log


class Helper:
    def __init__(self):
        pass

    @classmethod
    def validate_lsbatch_pack(cls, script_path):
        if not os.path.exists(os.path.join(script_path, 'src')):
            Log.error(os.path.join(script_path, 'src') + ' is not a directory')
            return False
        if not os.path.exists(os.path.join(script_path, 'src', 'main.py')):
            Log.error(ValidationMessages.MainFileNotPresent.format(os.path.join(script_path, 'src')))
            return False
        with open(os.path.join(script_path, 'src', 'main.py')) as py_file:
            if not ('def main(' in py_file.read()):
                Log.error(ValidationMessages.MainFunctionNotPresent.format(os.path.join(script_path, 'src', 'main.py')))
                return False
        return True

    @classmethod
    def zip_source_code(cls, script_path):
        shutil.make_archive(os.path.join(script_path, 'deliverables', 'code'), 'zip',
                            os.path.join(script_path, 'src'))

    @classmethod
    def validate_credentials(cls, credentials, update_region_details=False):
        credentials_to_validate = [Constants.OrgCode, Constants.Token, Constants.Region]
        for credential in credentials_to_validate:
            if credentials.get(credential) is None or not type(credentials[credential]) == str or credentials[
                credential] == '':
                return ValidationMessages.InvalidCredentials.format(credential)

        region_detail = cls.get_region_detail(credentials.get(Constants.Region))
        if region_detail is None:
            return ValidationMessages.InvalidValueOfRegion
        if update_region_details:
            credentials[Constants.Region] = region_detail

    @classmethod
    def convert_file_to_bytes(cls, file_name):
        with open(file_name, "rb") as f:
            bytes_buffer = io.BytesIO(f.read())
        return bytes_buffer

    @classmethod
    def retrieve_batch_details(cls, path):
        batch_details = {}
        batch_details_file_path = os.path.join(path, 'batch_details.json')
        if os.path.exists(batch_details_file_path):
            with open(batch_details_file_path, 'r') as json_file:
                try:
                    batch_details = json.loads(json_file.read())
                except Exception:
                    Log.error(ValidationMessages.BatchDetailsNotInFormat)
                    return None
        return batch_details

    @classmethod
    def update_batch_details(cls, script_path, batch_details):
        with open(os.path.join(script_path, 'batch_details.json'), 'w') as f:
            json.dump(batch_details, f, indent=4)

    @classmethod
    def get_region_detail(cls, region):
        region = region.strip()
        for region_detail in ALLOWED_REGIONS:
            if region == region_detail.get("name") or region == region_detail.get("id"):
                return region_detail
        return None


class ProgressBar(threading.Thread):
    def __init__(self, message, stop=False, kill=False):
        super().__init__()
        self.stop = stop
        self.kill = kill
        self.message = message

    def run(self):
        print(self.message)
        sys.stdout.flush()
        i = 0
        while not (self.stop or self.kill):
            if (i % 4) == 0:
                sys.stdout.write('\b/')
            elif (i % 4) == 1:
                sys.stdout.write('\b-')
            elif (i % 4) == 2:
                sys.stdout.write('\b\\')
            elif (i % 4) == 3:
                sys.stdout.write('\b|')

            sys.stdout.flush()
            time.sleep(0.2)
            i += 1
        if self.kill:
            print('\b\b\b\b ABORT!')
        else:
            print('\b\b\b done!')

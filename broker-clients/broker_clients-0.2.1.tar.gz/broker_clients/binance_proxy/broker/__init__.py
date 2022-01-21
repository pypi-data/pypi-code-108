import re
from datetime import datetime

class UtilsAPI:
    @classmethod
    def to_snake_case(cls, phrase):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', phrase).lower()

    @classmethod
    def convert_keys_to_snake_case(cls, json_response):
        json_response = cls.change_keys(json_response, cls.to_snake_case)
        return json_response

    @classmethod
    def rename_keys_with_prefix(cls, json_response, prefix):
        json_response = cls.change_keys(json_response, lambda s: prefix+s)
        return json_response

    @classmethod
    def change_keys(cls, obj, convert):
        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                new[convert(k)] = cls.change_keys(v, convert)
        elif isinstance(obj, (list, set, tuple)):
            new = [cls.change_keys(v, convert) for v in obj]
        else:
            return obj
        return new

    @classmethod
    def replace_abbreviations(cls, phrase):
        return phrase.replace('qty', 'quantity').replace('orig', 'original').replace('cummulative', 'cumulative')

    @classmethod
    def clean_response_field_names(cls, field_name):
        return cls.replace_abbreviations(cls.to_snake_case(field_name))

    @classmethod
    def clean_response(cls, response):
        if type(response) is dict:
            cleaned_response = {
                cls.clean_response_field_names(k): v if type(v) != list else [
                    cls.clean_response(i) for i in v] for k, v in response.items()}
            if 'transact_time' in cleaned_response:
                cleaned_response['transact_time'] = datetime.utcfromtimestamp(
                    cleaned_response['transact_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')

            if 'update_time' in cleaned_response:
                cleaned_response['update_time'] = datetime.utcfromtimestamp(
                    cleaned_response['update_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')

            if 'time' in cleaned_response:
                cleaned_response['time'] = datetime.utcfromtimestamp(
                    cleaned_response['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')

            return cleaned_response
        return response

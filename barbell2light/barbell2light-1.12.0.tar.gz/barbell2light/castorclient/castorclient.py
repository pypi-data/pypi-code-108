import os
import json

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from barbell2light.utils import Logger


class CastorClient:

    def __init__(self, client_id=None, client_secret=None, log_dir='.', cache_dir='castor_cache'):
        client_id, client_secret = self.get_credentials(client_id, client_secret)
        self.base_url = 'https://data.castoredc.com'
        self.token_url = self.base_url + '/oauth/token'
        self.api_url = self.base_url + '/api'
        self.session = self.create_session(client_id, client_secret, self.token_url)
        self.logger = Logger(prefix='log_castorclient', to_dir=log_dir)
        self.cache_dir = cache_dir

    @staticmethod
    def get_credentials(client_id=None, client_secret=None):
        cid = client_id
        cse = client_secret
        if cid is None:
            cid_file = '{}/castorclientid.txt'.format(os.environ['HOME'])
            if os.path.isfile(cid_file):
                with open(cid_file, 'r') as f:
                    cid = f.readline().strip()
            else:
                cid = os.environ.get('CASTOR_CLIENT_ID', None)
                if cid is None:
                    raise RuntimeError('Castor client ID not found in: \n'
                                       '(1) arguments\n'
                                       '(2) $HOME/castorclientid.txt\n'
                                       '(3) CASTOR_CLIENT_ID environment variable')
        if cse is None:
            cse_file = '{}/castorclientsecret.txt'.format(os.environ['HOME'])
            if os.path.isfile(cse_file):
                with open(cse_file, 'r') as f:
                    cse = f.readline().strip()
            else:
                cse = os.environ.get('CASTOR_CLIENT_SECRET', None)
                if cse is None:
                    raise RuntimeError('Castor client secret not found in: \n'
                                       '(1) arguments\n'
                                       '(2) $HOME/castorclientsecret.txt\n'
                                       '(3) CASTOR_CLIENT_SECRET environment variable')
        return cid, cse


    @staticmethod
    def create_session(client_id, client_secret, token_url):
        client = BackendApplicationClient(client_id=client_id)
        client_session = OAuth2Session(client=client)
        client_session.fetch_token(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
        )
        return client_session

    def get_studies(self):
        response = self.session.get(self.api_url + '/study').json()
        studies = []
        for study in response['_embedded']['study']:
            studies.append(study)
        return studies

    def get_study_id(self, name):
        studies = self.get_studies()
        for study in studies:
            if study['name'] == name:
                return study['study_id']
        return None

    def get_fields(self, study_id, use_cache=True, verbose=False):
        if use_cache and os.path.isfile('{}/fields_{}.json'.format(self.cache_dir, study_id)):
            self.logger.print('Loading fields from {}/fields_{}'.format(self.cache_dir, study_id))
            fields = json.load(open('{}/fields_{}.json'.format(self.cache_dir, study_id), 'r'))
            return fields
        self.logger.print('Loading fields for study {} from Castor'.format(study_id))
        url = self.api_url + '/study/{}/field'.format(study_id)
        response = self.session.get(url).json()
        page_count = response['page_count']
        fields = []
        for i in range(1, page_count + 1):
            url = self.api_url + '/study/{}/field?page={}'.format(study_id, i)
            response = self.session.get(url).json()
            for field in response['_embedded']['fields']:
                fields.append(field)
                if verbose:
                    self.logger.print(field['id'])
        if use_cache:
            os.makedirs('{}'.format(self.cache_dir), exist_ok=True)
            json.dump(fields, open('{}/fields_{}.json'.format(self.cache_dir, study_id), 'w'))
        return fields

    @staticmethod
    def get_field(name, fields):
        for f in fields:
            if f['field_variable_name'] == name:
                return f
        return None

    def get_field_id(self, name, fields):
        f = self.get_field(name, fields)
        return f['id']

    @staticmethod
    def get_option_name(value, option_group_name, option_groups):
        for option_group in option_groups:
            if option_group['name'] == option_group_name:
                for option in option_group['options']:
                    if option['value'] == value:
                        return option['name']
        return None

    def get_records(self, study_id, use_cache=True, verbose=False):
        if use_cache and os.path.isfile('{}/records_{}.json'.format(self.cache_dir, study_id)):
            self.logger.print('Loading records from {}/records_{}.json'.format(self.cache_dir, study_id))
            records = json.load(open('{}/records_{}.json'.format(self.cache_dir, study_id), 'r'))
            return records
        self.logger.print('Loading records for study {} from Castor'.format(study_id))
        url = self.api_url + '/study/{}/record'.format(study_id)
        response = self.session.get(url).json()
        page_count = response['page_count']
        records = []
        for i in range(1, page_count + 1):
            url = self.api_url + '/study/{}/record?page={}'.format(study_id, i)
            response = self.session.get(url).json()
            for record in response['_embedded']['records']:
                if not record['id'].startswith('ARCHIVED'):
                    records.append(record)
                    if verbose:
                        self.logger.print(record['id'])
        if use_cache:
            os.makedirs('{}'.format(self.cache_dir), exist_ok=True)
            json.dump(records, open('{}/records_{}.json'.format(self.cache_dir, study_id), 'w'))
        return records

    def get_option_groups(self, study_id, verbose=False):
        url = self.api_url + '/study/{}/field-optiongroup'.format(study_id)
        response = self.session.get(url).json()
        page_count = response['page_count']
        option_groups = []
        for i in range(1, page_count + 1):
            url = self.api_url + '/study/{}/field-optiongroup?page={}'.format(study_id, i)
            response = self.session.get(url).json()
            for option_group in response['_embedded']['fieldOptionGroups']:
                option_groups.append(option_group)
                if verbose:
                    self.logger.print(option_group['id'])
        return option_groups

    def get_field_data(self, study_id, record_id, field_id):
        url = self.api_url + '/study/{}/record/{}/study-data-point/{}'.format(study_id, record_id, field_id)
        field_data = self.session.get(url).json()
        return field_data


if __name__ == '__main__':
    client = CastorClient()
    print(client.get_studies())

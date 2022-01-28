import os
import pickle
import time

import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import OAuth2WebServerFlow

from sdc_dp_helpers.api_utilities.retry_managers import request_handler
from sdc_dp_helpers.google_search_console.config_managers import get_config
from sdc_dp_helpers.google_search_console.utils import date_range, un_nest_keys
from sdc_helpers.slack_helper import SlackHelper


class CustomGSCReader:
    """
        Custom Google Search Console Reader
    """

    def __init__(self, config_path=None, **kwargs):
        if config_path is not None:
            self.config = get_config(config_path, fmt='yml')
            self.credentials = kwargs['credentials']

        if config_path is None:
            self.credentials = get_config(kwargs['credentials'], fmt='json')

        self.scopes = (
            'https://www.googleapis.com/auth/webmasters.readonly',
            'https://www.googleapis.com/auth/webmasters'
        )
        self.discovery_uri = (
            'https://www.googleapis.com/discovery/v1/apis/customsearch/v1/rest'
        )

        self.slack_webhook = kwargs.get('slack_webhook', None)

    def generate_authentication(self, auth_file_location='gsc_credentials.pickle'):
        """
        A user friendly method to generate a .pickle file for future authentication.
        For the first time, you would need to log in with your web browser based on
        this web authentication flow. After that, it will save your credentials in
        a pickle file. Every subsequent time you run the script, it will use the
        “pickled” credentials stored in credentials.pickle to build the
        connection to Search Console.
        """
        client_id = self.credentials['installed'].get('client_id')
        client_secret = self.credentials['installed'].get('client_secret')
        oauth_scope = 'https://www.googleapis.com/auth/webmasters.readonly'
        redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

        flow = OAuth2WebServerFlow(client_id, client_secret, oauth_scope, redirect_uri)
        authorize_url = flow.step1_get_authorize_url()
        print(f'Go to the following link in your browser: {authorize_url}')
        code = input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        pickle.dump(credentials, open(auth_file_location, 'wb'))

    def webmasters_service(self):
        """
        Makes use of the .pickle cred file to establish a webmaster connection.
        """
        credentials = pickle.load(open(self.credentials, 'rb'))
        return build('webmasters', 'v3', credentials=credentials)

    @request_handler(
        wait=1, backoff_factor=5.0, backoff_method='random'
    )
    def run_request(self, service, request, site_url):
        """
        Run the API request that consumes a request payload and site url.
        This separates the request with the request handler from the rest of the logic.
        """
        print(f'Request: {request}')
        return service.searchanalytics().query(
            siteUrl=site_url,
            body=request
        ).execute()

    def query(self):
        """
        Consumes a .yaml config file and loops through the date and url
        to return relevant data from GSC API.
        """
        service = self.webmasters_service()
        start_date = self.config.get('startDate')
        end_date = self.config.get('endDate')

        data_set = []

        # split request by date to reduce 504 errors
        for date in date_range(start_date=start_date, end_date=end_date):

            # run until none is returned or there is no more data in rows
            row_index = 0
            while True:
                request = {
                    'startDate': date,
                    'endDate': date,
                    'dimensions': self.config.get('dimensions'),
                    'metrics': self.config.get('metrics'),
                    'searchType': self.config.get('searchType'),
                    'rowLimit': self.config.get('maxRows', 25000),
                    'startRow': row_index * self.config.get('maxRows', 25000),
                    'aggregationType': self.config.get('aggregationType', 'byPage')
                }

                try:
                    response = self.run_request(
                        service=service,
                        request=request,
                        site_url=self.config.get('siteUrl')
                    )

                    if response is None:
                        print('Response is None, stopping.')
                        break
                    if 'rows' not in response:
                        print('No more data in Response.')
                        break

                    # added additional data that the api does not provide
                    # un un_nest keys
                    for row in response['rows']:
                        row['site_url'] = self.config.get('siteUrl')
                        row['search_type'] = self.config.get('searchType')
                        row = un_nest_keys(
                            data=row,
                            col='keys',
                            key_list=self.config.get('dimensions'),
                            value_list=row.get('keys')
                        )
                        data_set.append(row)
                    row_index += 1

                except googleapiclient.errors.HttpError as error:
                    if error.resp.status == 403:
                        message = f"GSC quotaExceeded on: {self.config.get('siteUrl')} " \
                                  f"for {self.config.get('searchType')}, " \
                                  f"waiting for 15 minutes."
                        print(message)
                        if self.slack_webhook:
                            SlackHelper.send_message(
                                hook=self.slack_webhook,
                                color='#ffa500',
                                message=message
                            )
                        time.sleep(900)
                    else:
                        raise error

        return data_set

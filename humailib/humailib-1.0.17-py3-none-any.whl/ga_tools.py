"""A simple example of how to access the Google Analytics API."""

import argparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

class HumaiGAWrapper:

    # Define the auth scopes to request.
    scope = ['https://www.googleapis.com/auth/analytics.readonly']

    def __init__(self):
        self.service = None
        self.profile = None
        self.credentials = None

    def authenticate(self, service_account_email, key_file_location):

        # TODO: Make robust to failure.

        # Authenticate and construct service.
        self.service, self.credentials = self._get_service('analytics', 'v3', self.scope, key_file_location, service_account_email)
        self.profile = self._get_first_profile_id(self.service)
        
        #results = get_results(service, profile)
        accounts = self.service.management().accounts().list().execute()
        print("Username: {0}, Kind: {1}".format(accounts['username'], accounts['kind']));

    def get(self, start_date, end_date, metrics, dimensions, start_index=0, max_rows=1000):
        
        if self.service is None or self.profile is None or self.credentials is None:
            return None

        ids = "ga:" + self.profile
        data = self.service.data().ga().get(
            ids=ids, start_date=start_date, end_date=end_date, metrics=metrics,
            dimensions=dimensions, start_index=start_index, max_results=max_rows).execute()
 
        return data["rows"], data["totalResults"]

    def get_source_sessions(self, start_date, end_date, source_filters):

        if self.service is None or self.profile is None or self.credentials is None:
            return None

        ids = "ga:" + self.profile
        metrics = "ga:sessions"
        data = self.service.data().ga().get(
            ids=ids, start_date=start_date, end_date=end_date, metrics=metrics,
            filters=source_filters).execute()
        #printDictionary(data)
        return data["totalsForAllResults"][metrics]


    def _get_service(self, api_name, api_version, scope, key_file_location,
                    service_account_email):
        """Get a service that communicates to a Google API.

        Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scope: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account p12 key file.
        service_account_email: The service account email address.

        Returns:
        A service that is connected to the specified API.
        """

        credentials = ServiceAccountCredentials.from_p12_keyfile(
        service_account_email, key_file_location, scopes=scope)

        http = credentials.authorize(httplib2.Http())
        print(http)

        # Build the service object.
        service = build(api_name, api_version, http=http)

        return service, credentials

    def _get_first_profile_id(self, service):
        # Use the Analytics service object to get the first profile id.

        # Get a list of all Google Analytics accounts for this user
        accounts = service.management().accounts().list().execute()

        if accounts.get('items'):
            # Get the first Google Analytics account.
            account = accounts.get('items')[0].get('id')

            # Get a list of all the properties for the first account.
            properties = service.management().webproperties().list(
                accountId=account).execute()

            if properties.get('items'):
                # Get the first property id.
                property = properties.get('items')[0].get('id')

                # Get a list of all views (profiles) for the first property.
                profiles = service.management().profiles().list(
                accountId=account,
                webPropertyId=property).execute()

                if profiles.get('items'):
                    # return the first view (profile) id.
                    return profiles.get('items')[0].get('id')

        return None

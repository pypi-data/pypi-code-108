from __future__ import print_function
# built-in
import pickle
from pathlib import Path
from os.path import expanduser

# third library
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account


class GoogleAPI:
    def __init__(self, credentials=None):
        self.CREDENTIALS_PATH = credentials or Path(
            f'{expanduser("~")}/.credentials')

    def connect_lia(self):
        CREDENTIALS = 'credentials.json'
        SCOPES = ['https://www.googleapis.com/auth/content']

        try:
            credentials_path = self.CREDENTIALS_PATH / CREDENTIALS
        except:
            credentials_path = f"{self.CREDENTIALS_PATH}/{CREDENTIALS}"

        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(credentials_path.absolute()),
                scopes=SCOPES
            )
        except:
            credentials = service_account.Credentials.from_service_account_file(
                str(credentials_path),
                scopes=SCOPES
            )

        service = build('content', 'v2.1',
                        credentials=credentials, cache_discovery=False)
        return service

    def connect_gmail(self):
        CREDENTIALS = 'credentials.json'
        SCOPES = [
            'https://mail.google.com/', 'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.settings.basic'
        ]
        TOKEN = 'token.pickle'

        creds = None
        token_path = Path(self.CREDENTIALS_PATH) / TOKEN
        credentials_path = Path(self.CREDENTIALS_PATH) / CREDENTIALS

        if token_path.exists():
            with open(str(token_path.absolute()), 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path.absolute()), SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(str(token_path.absolute()), 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds,
                        cache_discovery=False)
        return service

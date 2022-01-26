import base64
import fnmatch
import logging
import uuid

from pathlib import Path
from .google_api import GoogleAPI
from napplib.hub.utils import Utils
from .errors import HttpError
from os.path import expanduser

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, download_folder=None, extension=None, credentials=None, limit=None):
        self.download_folder = download_folder
        self.limit = limit
        self.extension = extension
        self.credentials = Path(credentials) or Path(f'{expanduser("~")}/.credentials')

    def download_files(self):
        """Subclasses tem que implementar este método"""
        raise NotImplementedError()

    def __call__(self):
        self.download_files()


class WebDownloader(Downloader):
    download_folder = None
    start_date = None
    end_date = None
    credentials = None


class GetAttachments(WebDownloader):
    def __init__(self, query, amount=None, pattern=None, **kwargs):
        self.query = query
        self.amount = amount
        self.pattern = pattern
        super().__init__(**kwargs)

    def download_files(self):
        # user
        user = 'me'

        # path to store files
        store_dir = Path(self.download_folder).absolute()

        # get service connection gmail
        gmail = GoogleAPI(credentials=self.credentials)
        service = gmail.connect_gmail()

        params = {}

        if self.amount:
            params.update({'maxResults': self.amount})

        # search messages wich query
        results = service.users().messages().list(
            userId=user,
            q=self.query,
            **params,
        ).execute()

        # get messages
        messages = results.get('messages', [])
        # downloader file by file
        for message in messages: 
            try:
                self._GET(service, user, message['id'], store_dir)
            except Exception as e:
                print('erro:')
                print(e)
                print(f'{message} have problems. Please check!')

    def _GET(self, service, user_id, msg_id, store_dir):
        try:
            # get message
            message = service.users().messages().get(userId=user_id, id=msg_id).execute()

            for part in message['payload']['parts']:
                if part['filename']:
                    if self.pattern:
                        if not fnmatch.filter([part['filename']], self.pattern):
                            continue

                    # get attachment
                    attachment = service.users().messages().attachments().get(
                        userId=user_id,
                        messageId=message['id'],
                        id=part['body']['attachmentId']
                    ).execute()

                    if '/' in part['filename']:
                        part['filename'] = str(part['filename']).replace('/','_')

                    # write file
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    name = store_dir / part['filename']
                    new_name = Path(f'{name.stem}_{str(uuid.uuid4())[:8]}{name.suffix}')
                    path = f'{name.parents[0]}/{new_name}'

                    print(f'file: {part["filename"]}')
                    f = open(path, 'wb')
                    f.write(file_data)
                    f.close()

                    compacts_extension = ['.tar', '.tar.gz', '.rar', '.zip']
                    if str(new_name.suffix).lower() in compacts_extension:
                        Utils.extract_file(path)

        except HttpError as error:
            logger.errro(f'An error occurred: {error}')

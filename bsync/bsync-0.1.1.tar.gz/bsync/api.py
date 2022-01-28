import json
import os
import hashlib

from boxsdk import Client, JWTAuth
from progress.bar import Bar


def send_chunked(path, session_func):
    """
    Uses the chunked upload API from Box to upload sequential segments of a file
    """
    total_size = os.stat(path).st_size
    sha1 = hashlib.sha1()
    upload_session = session_func(total_size, path.name)
    part_array = []
    bar = Bar(path.name, max=upload_session.total_parts)
    content_stream = open(path, 'rb')

    for part_num in range(upload_session.total_parts):
        copied_length = 0
        chunk = b''
        while copied_length < upload_session.part_size:
            bytes_read = content_stream.read(upload_session.part_size - copied_length)
            if bytes_read is None:
                continue
            if len(bytes_read) == 0:
                break
            chunk += bytes_read
            copied_length += len(bytes_read)

        uploaded_part = upload_session.upload_part_bytes(chunk, part_num * upload_session.part_size, total_size)
        bar.next()
        part_array.append(uploaded_part)
        sha1.update(chunk)
    content_sha1 = sha1.digest()
    uploaded_file = upload_session.commit(content_sha1=content_sha1, parts=part_array)
    bar.finish()
    return uploaded_file


class BoxAPI:
    """
    Wraps boxsdk to create a client and perform actions, logging results
    """

    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self._client = None

    @property
    def client(self):
        """
        Gets a boxsdk.Client instance from the JSON settings file using JWT
        """
        if self._client:
            return self._client
        user = self.options['box_user']
        config = json.load(open(self.options['settings']))
        CLIENT_ID = config['boxAppSettings']['clientID']
        CLIENT_SECRET = config['boxAppSettings']['clientSecret']
        PUBLIC_KEY_ID = config['boxAppSettings']['appAuth']['publicKeyID']
        PRIVATE_KEY = config['boxAppSettings']['appAuth']['privateKey']
        PASSPHRASE = config['boxAppSettings']['appAuth']['passphrase']
        ENTERPRISE_ID = config['enterpriseID']
        auth = JWTAuth(CLIENT_ID, CLIENT_SECRET, ENTERPRISE_ID, PUBLIC_KEY_ID,
                       rsa_private_key_data=PRIVATE_KEY, rsa_private_key_passphrase=PASSPHRASE)
        auth.authenticate_instance()
        client = Client(auth)
        me = list(client.users(filter_term=user))[0]
        client = client.as_user(me)
        self.logger.info(f'Created Box client for user {user}')
        self._client = client
        return client

    def upload(self, parent_id, fname):
        """
        Uploads a file to the parent folder_id
        Handles large files by chunking
        """
        total_size = os.stat(fname).st_size
        folder = self.client.folder(parent_id)
        if total_size < 20000000:
            uploaded_file = folder.upload(fname, upload_using_accelerator=True)
        else:
            uploaded_file = send_chunked(fname, folder.create_upload_session)
        self.logger.info(f'Uploaded File ID: {uploaded_file.id} and File Name: {uploaded_file.name}')
        return uploaded_file

    def update(self, file_id, fname):
        """
        Updates the contents of a file and uploads it to an existing file on Box
        """
        total_size = os.stat(fname).st_size
        boxfile = self.client.file(file_id)
        if total_size < 20000000:
            updated_file = boxfile.update_contents(fname, upload_using_accelerator=True)
        else:
            updated_file = send_chunked(fname, boxfile.create_upload_session)
        self.logger.info(f'Updated File ID: {updated_file.id} and File Name: {updated_file.name}')
        return updated_file

    def create_folder(self, parent_id, name):
        """
        Creates a subfolder in an existing Box folder
        """
        subfolder = self.client.folder(parent_id).create_subfolder(name)
        self.logger.info(f'Created subfolder {subfolder.id}({name}) in {parent_id}')
        return subfolder

from googleapiclient.discovery import build 
from googleapiclient.http import MediaFileUpload 
from oauth2client.service_account import ServiceAccountCredentials 
import os

class GoogleDrive():
    """[summary]
    """
    def __init__(self, key_file_path: str, base_folder_id: str):
        self.service = self.get_google_service(key_file_path=key_file_path)
        self.base_folder_id = base_folder_id

    def get_google_service(self, key_file_path: str):
        scope = ['https://www.googleapis.com/auth/drive.file'] 
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_path, scopes=scope)
        return build("drive", "v3", credentials=credentials, cache_discovery=False) 

    def upload_file(self, filename:str, local_path:str, parents:str=None):
        ext = os.path.splitext(local_path.lower())[1][1:]
        if ext == "jpg":
            ext = "jpeg"
        mimeType = "image/" + ext
        if not parents:
            parents = self.base_folder_id
        print(parents)
        file_metadata = {"name": filename, "mimeType": mimeType, "parents": [parents] } 
        media = MediaFileUpload(local_path, mimetype=mimeType, resumable=True) 
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def create_folder(self, folder_name: str, parents: str=None):
        if not parents:
            parents = self.base_folder_id
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            "parents": [parents]
        }
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

    def delete(self, id):
        self.service.files().delete(fileId=id).execute()

    def list_key_id(self, base_key: str = None):
        page_token = None
        fl = []
        while True:
            response = self.service.files().list(
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)',
                                                pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print(file.get('name') + "," + file.get('id'))
                fl.append({'name': file.get('name'), 'id': file.get('id')})
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return fl
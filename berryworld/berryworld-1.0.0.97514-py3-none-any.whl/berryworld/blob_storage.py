from azure.storage.blob import BlobServiceClient, BlobClient, generate_account_sas,\
    ResourceTypes, AccountSasPermissions
from datetime import datetime, timedelta


class BlobStorage:
    """Class to connect to Azure Blob Storage easily
    """

    def __init__(self, blob_creds):
        """ Initialize the class
        -----------------------------
        blob_creds = {
            'account_name': '', 'account_key': '', 'container': ''
            }

        blob_ = Blob(blob_creds)
        -----------------------------
        """
        self.account_name = blob_creds['account_name']
        self.account_key = blob_creds['account_key']
        self.def_container = blob_creds['container']
        self.conn_str = 'DefaultEndpointsProtocol=https;AccountName=' + self.account_name + ';AccountKey=' +\
                        self.account_key + ';EndpointSuffix=core.windows.net'
        self.service_client = BlobServiceClient.from_connection_string(self.conn_str)
        try:
            list(self.service_client.get_container_client(self.def_container).list_blobs())
        except Exception:
            raise Exception

    def list_blobs(self, container_name=''):
        """
        List all the blobs in a container
        """
        if container_name == '':
            container_name = self.def_container
        container_client = self.service_client.get_container_client(container_name)
        return list(container_client.list_blobs())

    def list_blob_names(self, container_name=''):
        """
        List all the blob names in a container
        """
        if container_name == '':
            container_name = self.def_container
        container_client = self.service_client.get_container_client(container_name)
        blobs = list(container_client.list_blobs())
        return [blob['name'] for blob in blobs]

    def upload_blob(self, source, dest, container_name=''):
        """
        Upload local file to Blob Storage
        """
        if container_name == '':
            container_name = self.def_container
        # Create a blob client using the local file name as the name for the blob
        blob_client = self.service_client.get_blob_client(container=container_name, blob=dest)
        # Upload the created file
        with open(source, "rb") as data:
            blob_client.upload_blob(data)

    def download_blob(self, source, dest, container_name=''):
        """
        Download blob file to path
        """
        if container_name == '':
            container_name = self.def_container
        blob_client = self.service_client.get_blob_client(container=container_name, blob=source)
        with open(dest, 'wb') as file:
            data = blob_client.download_blob()
            file.write(data.readall())

    def delete_blob(self, blob_name, container_name=''):
        """
        Delete blob file from container
        """
        if container_name == '':
            container_name = self.def_container
        if isinstance(blob_name, list) is False:
            blob_name = [blob_name]
        # Check if the specified files exist in the container
        blob_names = self.list_blob_names(container_name=container_name)
        files_in_blob_list = [item for item in blob_names if item in blob_name]
        # Delete blobs
        blob_client = self.service_client.get_container_client(container=container_name)
        blob_client.delete_blobs(*files_in_blob_list)

    def move_blob(self, source, dest, container_name=''):
        """
        Move blob from one path to another
        """
        if container_name == '':
            container_name = self.def_container

        # Create sas token to access blob from URL
        sas_token = generate_account_sas(account_name=self.account_name, account_key=self.account_key,
                                         resource_types=ResourceTypes(object=True, container=True),
                                         permission=AccountSasPermissions(read=True, list=True),
                                         start=datetime.now(), expiry=datetime.utcnow() + timedelta(hours=1)
                                         )

        # Create blob client for source blob
        source_blob = BlobClient(self.service_client.url, container_name=container_name,
                                 blob_name=source, credential=sas_token)

        # Create new blob and copy using the URL
        new_blob = self.service_client.get_blob_client(container=container_name, blob=dest)
        new_blob.start_copy_from_url(source_blob.url)

import datetime
from pathlib import Path
from napplib.azure.blob_storage import BlobStorage

class FacebookController:
    @classmethod
    def send_to_storage(self, products, account_name, account_key, project, path, store_name = '', file_name = None, root_folder = False):
        try:
            # write local xml
            dt = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            xml_path = Path(f'{dt}_products.xml').absolute()
            if file_name:
                if '.' not in file_name and '.xml' not in file_name:
                    file_name += '.xml'
                xml_path = Path(file_name).absolute()

            with xml_path.open('w', encoding='utf-8') as output:
                output.write(products)

            # Send orders to storage
            BlobStorage.upload_blob(
                account_name    = account_name,
                account_key     = account_key,
                path            = path,
                project         = project,
                store_name      = store_name,
                output_file     = str(xml_path),
                root_folder     = root_folder
            )
        except Exception as e:
            print(f'Failed to save payload as blob storage file. {e}')

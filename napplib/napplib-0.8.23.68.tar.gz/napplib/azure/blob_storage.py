# azure-storage-blob==2.1.0
from typing import List
from azure.storage.blob import BlockBlobService
import logging, datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

class BlobStorage:
    
    
    @staticmethod
    def list_all_blobs(account_name='', account_key='', path='', project='', store_name=''):
        # Azure configs
        block_blob_service = BlockBlobService(
            account_name=account_name, 
            account_key=account_key
        )

        # create blob base object
        generator = block_blob_service.list_blobs(path, prefix=f'{project}/{store_name}')
        blobs = []

        for blob in generator:
            blobs.append({'name': blob.name, 'raw_object': blob})
        
        # return list of all blobs
        return blobs

    
    @staticmethod
    def get_blob(account_name='', account_key='', path='', blob_path='', custom_encoding='utf8'):
        # Azure configs
        block_blob_service = BlockBlobService(
            account_name=account_name, 
            account_key=account_key
        )

        blob_content = block_blob_service.get_blob_to_bytes(path, blob_path).content.decode(custom_encoding)

        # return content
        return blob_content


    @staticmethod
    def get_latest_blob(account_name='', account_key='', path='', project='', store_name='', custom_encoding='utf8', get_filename=None):
        # Azure configs
        block_blob_service = BlockBlobService(
            account_name=account_name, 
            account_key=account_key
        )

        # create blob base object
        generator = block_blob_service.list_blobs(path)
        
        # date objects
        selected_last_modified = None
        selected_file_name = None
        selected_file_content = None
        
        # loop in all blob from generator
        for blob in generator:
            # get file name and last modified date
            file_name = blob.name

            # create a match name based on blob path ex: project/store
            split_path = file_name.split('/')
            match_name = f'{split_path[0]}/{split_path[1]}'
            
            # concat project and store name
            project_store = f'{project}/{store_name}'
            
            if project_store != match_name:
                continue
                
            file_last_modified = blob.properties.last_modified

            # if selected last modified date is not None
            if selected_last_modified:
                # check if selected file  date is greater than current loop file
                if selected_last_modified > file_last_modified:
                    # log
                    logging.info(f'This file {selected_file_name} is newest... Skip: {file_name}')
                else:
                    # set dates with this loop file
                    selected_last_modified = file_last_modified
                    selected_file_name = file_name
            else:
                # set dates with this loop file
                selected_last_modified = file_last_modified
                selected_file_name = file_name
        
        # get blob content
        if selected_file_name:
            # get file content using custom encoding, default: uf-8
            selected_file_content = block_blob_service.get_blob_to_bytes(path, selected_file_name).content.decode(custom_encoding)
            
            # print
            logging.info(f'Selected file: {selected_file_name}, File date: {selected_last_modified}')
        
            # return blob content
            if get_filename:
                return selected_file_content, selected_file_name
            else:
                return selected_file_content
        
        # log with no match files
        logging.info(f'No files detected for this store {store_name}...')
        return None


    @staticmethod
    def get_latest_folder_blobs(account_name='', account_key='', path='', project='', store_name='', custom_encoding='utf-8') -> List[dict]:
        # Azure configs
        block_blob_service = BlockBlobService(
            account_name=account_name, 
            account_key=account_key
        )

        # create blob base object
        generator = list(block_blob_service.list_blobs(path))

        generator.reverse()
        
        blob_list = list()
        last_folder = None

        # loop in all blob from generator
        for blob in generator:
            # get file name and last modified date
            file_name = blob.name

            # create a match name based on blob path ex: project/store
            split_path = file_name.split('/')
            match_name = f'{split_path[0]}/{split_path[1]}'
            
            # concat project and store name
            project_store = f'{project}/{store_name}'
            
            if project_store != match_name:
                continue

            split_path.pop(-1)

            folder = '/'.join(split_path)

            if not last_folder:
                last_folder = folder

            if folder == last_folder:
                _file = block_blob_service.get_blob_to_bytes(path, file_name).content.decode(custom_encoding)
                blob_list.append({'name': file_name, 'content': _file})
                
                
        return blob_list

    
    @staticmethod
    def get_latest_blob_by_name(account_name='', account_key='', path='', project='', blob_name='', store_name='', custom_encoding='utf8'):
        # Azure configs
        block_blob_service = BlockBlobService(
            account_name=account_name, 
            account_key=account_key
        )

        # create blob base object
        generator = block_blob_service.list_blobs(path)
        
        # date objects
        selected_last_modified = None
        selected_file_name = None
        selected_file_content = None
        
        # loop in all blob from generator
        for blob in generator:
            # get file name and last modified date
            file_name = blob.name

            # create a match name based on blob path ex: project/store
            split_path = file_name.split('/')
            match_name = f'{split_path[0]}/{split_path[1]}'
            
            # concat project and store name
            project_store = f'{project}/{store_name}'
            
            if project_store != match_name:
                continue
            if blob_name not in file_name:
                continue

            file_last_modified = blob.properties.last_modified

            # if selected last modified date is not None
            if selected_last_modified:
                # check if selected file  date is greater than current loop file
                if selected_last_modified > file_last_modified:
                    # log
                    logging.info(f'This file {selected_file_name} is newest... Skip: {file_name}')
                else:
                    # set dates with this loop file
                    selected_last_modified = file_last_modified
                    selected_file_name = file_name
            else:
                # set dates with this loop file
                selected_last_modified = file_last_modified
                selected_file_name = file_name
        
        # get blob content
        if selected_file_name:
            # get file content using custom encoding, default: uf-8
            selected_file_content = block_blob_service.get_blob_to_bytes(path, selected_file_name).content.decode(custom_encoding)
            # print
            logging.info(f'Selected file: {selected_file_name}, File date: {selected_last_modified}')
            return selected_file_content
        
        # log with no match files
        logging.info(f'No files detected for this store {store_name}...')
        return None


    @staticmethod
    def upload_blob(account_name='', account_key='', path='', project='', store_name='', output_file='', prefix=None, first_charge=False, is_sale=False, is_stock=False, root_folder=False):
        # Azure config
        block_blob_service = BlockBlobService(
            account_name=account_name, 
            account_key=account_key
        )
        
        # create date pattern based on Year/Month/Day
        dt_str = datetime.datetime.now().strftime('%Y/%m/%d')
        year = dt_str.split('/')[0]
        month = dt_str.split('/')[1]
        day = dt_str.split('/')[2]

        # extract filename from full output file path
        filename = output_file.split('/')[-1]
        
        # parse args
        if first_charge and not is_sale and not is_stock:
            filename = f'fullcharge_{filename}'
        elif first_charge and is_sale and not is_stock:
            filename = f'sales_fullcharge_{filename}'
        elif first_charge and not is_sale and is_stock:
            filename = f'stock_fullcharge_{filename}'
        elif is_sale and not is_stock and not first_charge:
            filename = f'sales_{filename}'
        elif is_stock and not is_sale and not first_charge:
            filename = f'stock_{filename}'
        
        # psrse prefix
        if prefix and prefix != '':
            if '-' in prefix or '_' in prefix:
                filename = f'{prefix}{filename}'
            else:
                filename = f'{prefix}_{filename}'
        
        # create target folder to upload on azure blob storage. Ex: project/store/2020/01/01/sample.csv
        if store_name:
            project = f"{project}/{store_name}"

        if not root_folder:
            target = f'{project}/{year}/{month}/{day}/{filename}'
        else:
            target = f'{project}/{filename}'

        # use azure blob service to upload
        try:
            block_blob_service.create_blob_from_path(path, target, output_file)
            logging.info(f'Upload file {target} finished!')
        except Exception as e:
            logging.info(f'Failed to upload file {target} on azure blob storage: {e}')

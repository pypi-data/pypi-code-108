import datetime
import logging

class Utils:
    @classmethod
    def normalize_datetime(self, date):
        new_dt = date
        if new_dt and new_dt != '':
            if len(new_dt) > 25:
                # Eg: 2020-10-14T14:24:57.789000
                new_dt = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
                new_dt = new_dt.strftime('%d/%m/%Y %H:%M:%S')
            elif len(new_dt) == 25:
                # 2015-01-09T22:00:00-02:00
                new_dt = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
                new_dt = new_dt.strftime('%d/%m/%Y %H:%M:%S')
            elif len(new_dt) == 10:
                # 1995-01-01
                try:
                    new_dt = datetime.datetime.strptime(date, '%Y-%m-%d')
                    new_dt = new_dt.strftime('%d/%m/%Y')
                except:
                    new_dt = datetime.datetime.strptime(date, '%d-%m-%Y')
                    new_dt = new_dt.strftime('%d/%m/%Y')
        return new_dt

    @classmethod
    def download_azure_storage(self, block_blob_service='', server='', store=''):
        """
        Foi criada essa funcao para coletar o ultimo arquivo da loja e armazenar o conteudo para se integrar
        com o Napp HUB.
        """
        # create blob base object
        generator = block_blob_service.list_blobs(server)

        # date objects
        selected_last_modified = None
        selected_file_name = None
        selected_file_content = None

        # loop in all blob from generator
        for blob in generator:
            # get file name and last modified date
            file_name = blob.name
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
        selected_file_content = block_blob_service.get_blob_to_bytes(server, selected_file_name).content.decode('utf8')

        # print
        logging.info(f'Selected file: {selected_file_name}, File date: {selected_last_modified}')

        # return blob content
        return selected_file_content
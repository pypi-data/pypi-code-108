import logging, ftplib, datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

class FTPController:
    
    @classmethod
    def download_ftp(self, download_path, host="", login="", password="", 
                port=None, url="", extension="",
                move_downloaded_files=False):

        if download_path=='':
            logging.info(f"Please, insert download_path.")
        
        connection = ftplib.FTP(host, login, password)
        logging.info(f"Logged into {host} with user {login}")

        list_files = connection.nlst()
        files = list_files.copy()

        for file in files:
            if str(file.split('.')[-1]).lower() in extension:
                logging.info(f'Downloading {file}')
                with open(f'{download_path}/files/{file}', 'wb') as f:
                    connection.retrbinary(f'RETR {file}', f.write)
                    
        if move_downloaded_files:
            if "processados" not in list_files:
                connection.mkdir("processados")
                
            for file in files:
                if 'processados' not in str(file):
                    logging.info(f'Moving file  {file} to folder processados')    
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
                    file_part = file.split('.')
                    new_name = f"{file_part[0]}-{timestamp}.{file_part[1]}"
                    connection.rename(file, f"processados/{new_name}")

        connection.close()
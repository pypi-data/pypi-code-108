from  ftplib import FTP
import os

class FTPService():

    server = None
    login = None
    password = None
    ftp = None
    
    def __init__(self, server, login, password):
        
        self.server = server
        self.login = login
        self.password = password
        self.ftp = FTP(self.server,self.login, self.password)
        
        
    def send_file(self, local_filename, remote_filename ):
        with open(local_filename, "rb") as file:
            try:
                self.ftp.storbinary('STOR %s' % os.path.basename(remote_filename), file)
            except Exception as e:
                print (e)
            
    def create_directory(self, directory_name):
        try:
            ftpResponse = self.ftp.mkd(directory_name)
        except Exception as e:
                print (e)
            
    def create_directory_tree(self, directory_path):
        if directory_path != "":
            try:
                self.ftp.cwd(directory_path)
            except Exception as e:
                self.create_directory_tree("/".join(directory_path.split("/")[:-1]))
                self.ftp.mkd(directory_path)
                self.ftp.cwd(directory_path)
        
    def list_files(self):
        try:
            ftpResponse = self.ftp.dir()
        except Exception as e:
            print (e)

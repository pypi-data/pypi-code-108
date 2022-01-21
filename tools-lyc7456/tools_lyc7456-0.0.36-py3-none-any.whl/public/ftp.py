from ftplib import FTP


class FTP_Tools():
    """[ftp简单方法封装]
    """
    def __init__(self, host, username, password, port=21):
        self.host = host
        self.port = port
        self.username = username
        self.password = password


    def connect(self):
        """[建立ftp连接]

        Returns:
            [type]: [description]

        Return:
            [obj]: ftp_conn 连接对象, False-连接异常
        """
        try:
            ftp_conn = FTP()
            # ftp.set_debuglevel(2)
            ftp_conn.connect(self.host, int(self.port))
            ftp_conn.login(self.username, self.password)
            self.conn = ftp_conn
            return ftp_conn
        
        except Exception as err:
            print(err) 
            return False


    def upload_file(self, localfile, remotefile, bufsize=1024):
        """[上传文件]

        Args:
            localfile ([str]): [本地文件绝对路径]
            remotefile ([str]): [目标文件绝对路径]
            bufsize (int, optional): [读取文件buff缓存大小]. Defaults to 1024.
        
        Return:
            [bool]: False-异常|True-正常
        """

        try:
            ftp_conn=self.connect()
            fp = open(localfile, 'rb')
            ftp_conn.storbinary('STOR ' + remotefile, fp, bufsize)
            ftp_conn.set_debuglevel(0)
            fp.close()
            return True

        except Exception as err:
            print(err)
            return False


    def download_file(self, remotefile, localfile, bufsize=4096):
        """[下载文件]

        Args:
            remotefile ([str]): [目标文件绝对路径]
            localfile ([str]): [本地文件绝对路径]
            bufsize (int, optional): [读取文件buff缓存大小]. Defaults to 4096.

        Return:
            [bool]: False-异常|True-正常
        """
        try:
            ftp_conn=self.connect()
            fp = open(localfile, 'wb')
            ftp_conn.retrbinary('RETR ' + remotefile, fp.write, bufsize)
            ftp_conn.set_debuglevel(0)
            fp.close()
            return True

        except Exception as err:
            print(err)
            return False


    def check_remote_dir(self, remotedir):
        """[检查远端ftp目录，不存在则创建]

        Args:
            remotedir ([str]): [远端ftp根目录下的目录]

        Return:
            [bool]: False-异常|True-正常
        """
        
        try:
            ftp_conn=self.connect()
            remotepath_list = remotedir.split('/')
            dir = ''
            index = 1
            for i in remotepath_list:
                if index < len(remotepath_list):
                    dir += i+ '/'
                    if remotepath_list[index] not in ftp_conn.nlst(dir):
                        ftp_conn.mkd(dir + remotepath_list[index])
                    index += 1
            return True

        except Exception as err:
            print(err)
            return False


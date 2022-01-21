import os
import paramiko

# Write by lyc at 2021-10-14
# 参考文档《Python paramiko 模块详解与SSH主要功能模拟》https://blog.csdn.net/u014028063/article/details/81197431

class SSH_Tools():
    """[ssh简单方法封装]
    """
    def __init__(self, host, username='root', port=22, password='', key='') -> None:
        """[初始化对象]

        Args:
            host ([str]): [主机ip]
            port (int, optional): [端口号].默认值 '22'
            username (str, optional): [用户名]. 默认root用户
            password ([str, optional]): [密码].
            ssh_key ([str, optional]): [ssh-key 私钥文件，绝对路径]
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key = key
    

    def connect(self, auth_type='sshclient'):
        """[sshclient 方式登录]

        Args:
            auth_type ([str, optional]): 'sshclient' 或 'transport'

        Returns:
            [obj]: [SSHClient的对象]
        """
        try:
            ssh = paramiko.SSHClient()      # 创建ssh对象
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())       # 允许连接不在know_hosts文件中的主机

            # sshclient 方式
            if auth_type == 'sshclient':
                # 基于用户名和密码
                if len(self.password) > 0:
                    ssh.connect(hostname=self.host, port=self.port, username=self.username, password=self.password, timeout=5)
                
                # ssh-key 秘钥方式
                elif len(self.key) > 0 and os.path.exists(self.key):
                    key = paramiko.RSAKey.from_private_key(self.key)
                    ssh.connect(hostname=self.host, port=self.port, username=self.username, pkey=key, timeout=5)

                else:
                    # 密码或密钥有误，主动抛出异常
                    raise Exception("Please check password or key.")
            
            # transport 方式
            # elif auth_type == 'transport':
            #     transport = paramiko.Transport((self.host, self.port))      # 实例化一个transport对象
               
            #     # 基于用户名和密码
            #     if len(self.password) > 0:
            #         transport.connect(username=self.username, password=self.password)       # 建立连接

            #         # 将sshclient的对象的transport指定为以上的transport
            #         ssh._transport = transport
            #         # 关闭连接
            #         # transport.close()
            
 
            return ssh      # 返回已经连接成功的ssh对象

        except Exception as err:
            print(err)



    def ssh_exec_command(self, command, open_log=True):
        """[ssh远程linux主机执行命令]

        Args:
            command ([str]): [Linux shell命令，多条命令使用 ';' 分隔符分割。]
            open_log (bool, optional): ['True'开启采集命令 stdout和stderr；'False' 关闭采集。]. Defaults to True.

        Returns:
            [dict]: [返回字典：'stdout'命令正确结果，'stderr'命令失败报错]
        """
        ssh = self.connect()    # ss连接目标主机
        try:
            result = {'stdout': '', 'stderr': '', 'open_log': open_log}
            stdin, stdout, stderr = ssh.exec_command(command)
            if open_log:
                result['stdout'] = (stdout.read()).decode('utf-8')
                result['stderr'] = (stderr.read()).decode('utf-8')
            ssh.close()
            return result        # 返回命令结果

        except Exception as err:
            print(err)



    def push_file(self, local_file, remote_file):
        """[sftp上传文件到目标主机]

        Args:
            local_file ([str]): [本地文件绝对路径]
            remote_file ([str]): [目标主机文件绝对路径]

        Returns:
            [str]: ['0'上传成功]
        """
        ssh = self.connect()
        try:
            sftp = ssh.open_sftp()      # 创建sftp对象
            sftp.put(local_file, remote_file)
            sftp.close()
            ssh.close()
            return '0'

        except Exception as err:
            print(err)
            return err



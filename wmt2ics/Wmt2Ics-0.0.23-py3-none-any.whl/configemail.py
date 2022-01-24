import os
import json
from sys import platform


class ConfigEmail:
    '''Used to configure settings for sending email'''

    def __init__(self):
        self.basepath = os.path.dirname(__file__)
        self.config_file = os.path.abspath(os.path.join(self.basepath,
                                           "wmtconfig.json"))

    def get_config(self):
        if platform == 'linux':
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.loads(f.read())
                    if self.config["APP_PWD"] == "":
                        self.config["APP_PWD"] = os.environ.get('GMAIL_APP_PWD')
                        return self.config
            except ValueError:
                print('No configuration found\n')
                self.ask_config()
        elif platform == 'win32':
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.loads(f.read())
                    return self.config
            except ValueError:
                print('No Configuration Found\n')
                self.ask_config()

    def ask_config(self):
        self.smtp = input("Enter smtp server -> ")
        self.port = input("Enter smtp port -> ")
        self.send = input("Enter sender's email -> ")
        self.send_pwd = input("Enter sender's app password -> ")
        self.dest = input("Enter destination email -> ")
        self.write_config()

    def setup_config(self, smtp='smtp.gmail.com', port='587',
                     send='', send_pwd='', dest=''):
        self.smtp = smtp
        self.port = port
        self.send = send
        self.send_pwd = send_pwd
        self.dest = dest
        self.write_config()

    def write_config(self):
        '''writes the wmtconfig.json file'''
        self.raw_config = {"SMTPSERVER": self.smtp,
                           "SMTPPORT": self.port,
                           "SENDER": self.send,
                           "APP_PWD": self.send_pwd,
                           "RECEIVER": self.dest
                           }
        with open(self.config_file, 'w+') as f:
            f.write(json.dumps(self.raw_config, indent=3))


if __name__ == '__main__':
    ConfigEmail()

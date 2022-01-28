from easy_patents.get_apitoken import get_token, get_token_by
import configparser
from datetime import datetime, timedelta
import os

DIR_NAME = os.path.dirname(__file__)
CONF_FILE = os.path.join(DIR_NAME, 'config/config.ini')
USER_FILE = os.path.join(DIR_NAME, 'config/user.ini')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class AuthInfo:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(CONF_FILE)
        self.user_conf = configparser.ConfigParser()
        self.user_conf.read(USER_FILE)
        self.token_path = self.user_conf['AuthInfo']['token_path']
        self.username = self.user_conf['AuthInfo']['username']
        self.password = self.user_conf['AuthInfo']['password']
        self.read_accesstokens()

    def get_accesstoken(self):
        self.refresh()
        return self.access_token

    def read_accesstokens(self):
        self.access_token = self.config['AuthInfo']['access_token']
        expire_in = self.config['AuthInfo']['expires_in']
        self.expires_in = datetime.strptime(expire_in, DATETIME_FORMAT)
        self.refresh_token = self.config['AuthInfo']['refresh_token']
        refresh_expires_in = self.config['AuthInfo']['refresh_expires_in']
        self.refresh_expires_in = datetime.strptime(refresh_expires_in, DATETIME_FORMAT)

    def refresh(self):
        now = datetime.now()
        if now > self.refresh_expires_in:
            self.get_token_by_username()
        elif now > self.expires_in:
            self.get_token_by_refresh_token()

    def update_tokens(self, now, response):
        response = response.json()
        # Configファイルのアップデート
        self.config['AuthInfo']['access_token'] = response['access_token']
        self.config['AuthInfo']['refresh_token'] = response['refresh_token']
        expire_td = timedelta(seconds=(response['expires_in']))
        expires_in = now + expire_td
        self.config['AuthInfo']['expires_in'] = expires_in.strftime(DATETIME_FORMAT)
        refresh_expire_td = timedelta(seconds=(response['refresh_expires_in']))
        refresh_expires_in = now + refresh_expire_td
        self.config['AuthInfo']['refresh_expires_in'] = refresh_expires_in.strftime(DATETIME_FORMAT)
        with open(CONF_FILE, "w") as f:
            self.config.write(f)
        self.read_accesstokens()


    def get_token_by_username(self):
        now = datetime.now()
        response = get_token(self.username, self.password, self.token_path)
        self.update_tokens(now, response)

    def get_token_by_refresh_token(self):
        now = datetime.now()
        response = get_token_by(self.refresh_token, self.token_path)
        self.update_tokens(now, response)


if __name__ == "__main__":
    authinfo = AuthInfo()
    print(authinfo.get_accesstoken())


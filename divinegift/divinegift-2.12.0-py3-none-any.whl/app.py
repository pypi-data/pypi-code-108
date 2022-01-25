import os
from copy import deepcopy
from datetime import datetime
from time import sleep
from traceback import format_exc
from typing import List, Dict

from divinegift.config import Settings
from divinegift.logger import Logger
from divinegift.main import get_args, get_log_param, get_list_files
from divinegift.sender import Sender


class Application:
    def __init__(self):
        self.st = datetime.now()
        self.sp = datetime.now()
        self.args = get_args()
        self.lp = get_log_param(self.args)
        self.logger = Logger()
        self.logger.set_log_level(**self.lp)

        self.settings = Settings(logger_=self.logger)
        self.settings_edited_at = None
        self.conf_file_path = self.args.get('c', 'settings.yml')
        self.cipher_key_path = self.args.get('ck', 'key.ck')

        self.print_intro()

        self.logger.log_info(f'{"=" * 20} START {"=" * 20}')

    def __repr__(self):
        return f'Application()'

    def update_settings(self, encrypt_config=True, log_changes=False, use_yaml=True, encoding='utf-8'):
        settings_edited_at = os.path.getmtime(self.conf_file_path)
        if settings_edited_at != self.settings_edited_at:
            self.set_settings(encrypt_config, log_changes, use_yaml, encoding)

    def run(self):
        pass

    def run_service(self):
        while True:
            self.run()
            sleep(self.get_settings('service_wait', 5))

    def set_settings(self, encrypt_config=True, log_changes=False, use_yaml=True, encoding='utf-8'):
        self.settings.parse_settings(self.conf_file_path, self.cipher_key_path,
                                     encoding=encoding, log_changes=log_changes, use_yaml=use_yaml)
        self.settings_edited_at = os.path.getmtime(self.conf_file_path)

        if encrypt_config:
            self.init_config()

    def init_config(self):
        if not os.path.exists('key.ck'):
            self.settings.initialize_cipher()
            self.encrypt_password('email_conf', 'pwd')
            self.settings.save_settings(self.conf_file_path)

    def encrypt_password(self, connection_name: str, pass_field: str = 'db_pass'):
        try:
            self.settings.encrypt_password(connection_name, pass_field)  # Change it for your config
        except Exception as ex:
            self.logger.log_err(f'Could not encrypt password: {ex}')

    def get_settings(self, param=None, default=None):
        return self.settings.get_settings(param, default)

    def print_intro(self):
        print(f'Process {self.args.get("name")} started!')
        log_place = os.path.join(self.lp.get("log_dir"), self.lp.get("log_name")) if self.lp.get(
            "log_name") else "ON SCREEN"
        print(f'Log will be here: {log_place}')

    def log_debug(self, *args, separator: str = ' '):
        self.logger.log_debug(*args, separator)

    def log_info(self, *args, separator: str = ' '):
        self.logger.log_info(*args, separator)

    def log_warning(self, *args, separator: str = ' '):
        self.logger.log_warn(*args, separator)

    def log_warn(self, *args, separator: str = ' '):
        self.logger.log_warn(*args, separator)

    def log_err(self, *args, separator: str = ' ', src: str = None, mode: List = None, channel: Dict = None):
        self.logger.log_err(*args, separator, src, mode, channel)

    def log_crit(self, *args, separator: str = ' '):
        self.logger.log_crit(*args, separator)

    def log_err_notif(self, *args, separator: str = ' '):
        mode = self.get_settings('monitoring')
        channel = deepcopy(self.get_settings('monitoring_channel'))
        if 'email' in mode or 'email_attach' in mode:
            channel['email'] = deepcopy(self.get_settings('email_conf'))
            channel['email']['TO'] = channel.pop('email_to')
        self.log_err(*args, separator=separator)
        src = self.get_settings('service_name', self.args.get('name'))
        self.notify(*args, separator=separator, src=src, mode=mode, channel=channel)

    def notify(self, *args, separator: str = ' ', src: str = None, mode: List = None, channel: Dict = None):
        """
        :param args:
        :param separator:
        :param msg: Error message which will logged
        :param src: Source which raised error
        :type src: string
        :param mode: List of monitoring's mode (telegram, email, email_attach, slack)
        :type mode: list
        :param channel: Dict with parameters of monitoring (e.g. {'telegram': -1001343660695}
        :type channel: dict
        :return:
        """
        error_txt = f'''An error has occurred in {src}
        Error text: {separator.join([str(x) for x in args])}\n{format_exc()}'''

        sender = Sender()

        if mode:
            if 'telegram' in mode:
                sender.send_telegram(error_txt, chat_id=channel.get('telegram', -1001343660695))
            if 'slack' in mode:
                sender.send_slack(error_txt)
            if 'email' in mode:
                sender.send_mail(error_txt, f'{src} ERROR', **channel.get('email'))
            if 'email_attach' in mode:
                if self.lp.get('log_dir', '.') and self.lp.get('log_name'):
                    log = get_list_files(self.lp.get('log_dir'), self.lp.get('log_name'), add_path=True)
                else:
                    log = []
                sender.send_mail(error_txt, f'{src} ERROR', attachments=log, **channel.get('email_attach'))

import smtplib
import socket
from typing import Union, Optional

from divinegift import logger, version
from divinegift.mailer import Mailer, Message
import requests
from deprecation import deprecated
from email.header import Header


class MailerContinius(Mailer):
    def __init__(self, host="localhost", port=0, use_tls=False, usr=None, pwd=None, use_ssl=False, use_plain_auth=False,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        super().__init__(host, port, use_tls, usr, pwd, use_ssl, use_plain_auth, timeout)
        self.server = None

    def send(self, msg, debug=False):
        """
        Send one message or a sequence of messages.
        """
        if not self.server:
            if self.use_ssl:
                self.server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                self.server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)

            if debug:
                self.server.set_debuglevel(1)

            if self._usr and self._pwd:
                if self.use_tls is True:
                    self.server.ehlo()
                    self.server.starttls()
                    self.server.ehlo()

                if self.use_plain_auth is True:
                    self.server.esmtp_features["auth"] = "LOGIN PLAIN"

                self.server.login(self._usr, self._pwd)

        if isinstance(msg, Message):
            msg = [msg]

        for m in msg:
            self._send(self.server, m)

    def quit(self):
        self.server.quit()
        self.server = None


class Sender:
    def __init__(self, reopen_mail_session=True):
        self.email_connector = None
        self.zabbix_agent = None
        self.reopen_mail_session = reopen_mail_session

    def send_mail(self, msg: str, subject: str, TO: list, CC: list = None, BCC: list = None,
                  FROM: str = '', HOST: str = '', PORT=0, USE_TLS=False,
                  usr='', pwd='', charset: str = 'utf-8', IS_HTML: bool = True,
                  attachments: Union[list, str] = None, mimetype: str = None):
        """
        Sending email
        :param msg: Message body
        :param subject: Message subject
        :param TO: List of recipients
        :param CC: List of copy recipients
        :param BCC: List of shadow copy recipients
        :param FROM: Sender email
        :param HOST: smtp server
        :param usr: user
        :param pwd: password
        :param charset: Encoding charset
        :param IS_HTML: Will it be HTML or plain text
        :param attachments: Attachments
        :param mimetype: Mimetipe of attachments
        :return:
        """
        message = Message(From=FROM,
                          To=TO,
                          Cc=CC,
                          Bcc=BCC,
                          charset=charset)
        message.Subject = Header(subject.encode('utf-8'), 'UTF-8').encode()
        if IS_HTML:
            message.Html = msg
        else:
            message.Body = msg
        if attachments:
            if type(attachments) == list:
                for file in attachments:
                    try:
                        message.attach(file, mimetype=mimetype, charset=charset)
                    except Exception as ex:
                        logger.get_logger().log_err(f'Could not attach file: {file}')
            elif type(attachments) == str:
                try:
                    message.attach(attachments)
                except Exception as ex:
                    logger.get_logger().log_err(f'Could not attach file: {attachments}')
            else:
                logger.get_logger().log_warn('There is incorrect type of variable attachments')

        if self.email_connector is None:
            if self.reopen_mail_session:
                self.email_connector = Mailer(HOST, PORT, USE_TLS, usr=usr, pwd=pwd)
            else:
                self.email_connector = MailerContinius(HOST, PORT, USE_TLS, usr=usr, pwd=pwd)
        try:
            self.email_connector.send(message)
        except Exception as ex:
            logger.get_logger().log_err('Error while sending email')
            self.email_connector = None
            raise ex

    @staticmethod
    def send_telegram(message: str, chat_id: int = 161680036):
        """
            Send a telegram message
            :param message: Message
            :param chat_id: Id of chat where msg will be sent
            :param subject: Subject of message
            :return: None
            """
        URL = 'https://api.telegram.org/bot'  # URL на который отправляется запрос
        TOKEN = '456941934:AAGZMmXJE4VyLagIkVY7qMG0doASxU7f8ac'  # токен вашего бота, полученный от @BotFather
        data = {'chat_id': chat_id, 'text': message}

        try:
            requests.post(URL + TOKEN + '/sendMessage', data=data)  # запрос на отправку сообщения
        except:
            logger.get_logger().log_err('Send message error')

    @staticmethod
    def send_slack(message: str, webhook: str = None, channel: str = 'aims_integrations',
                   username: str = 'aims_notifier', icon_url: str = None):
        """
        Send message to slack
        :param message: Message
        :param webhook: WebHook URL to sending
        :return: None
        """
        if not webhook:
            webhook = 'https://mattermost.s7.aero/hooks/71ra7afrgjytfq4j5wm4o6x6jo'
        data = {
            'text': message,
            'username': username,
            'channel': channel,
        }
        if icon_url:
            data.update({'icon_url': icon_url})
        try:
            requests.post(webhook, json=data, headers={'content-type': 'application/json'})
        except:
            logger.get_logger().log_err('Send message error')

    def send_zabbix(self, host, key, value, **server_conf):
        from divinegift import zabbix_agent
        if self.zabbix_agent is None:
            self.zabbix_agent = zabbix_agent.ZabbixAgent(**server_conf)
        try:
            self.zabbix_agent.send(host, key, value)
        except:
            logger.get_logger().log_err('Error was occured while sending status to zabbix')


@deprecated(deprecated_in='1.3.16', current_version=version, details='Use class Sender instead')
def send_email(msg: str, subject: str, TO: list, CC: list = None, BCC: list = None, 
               FROM: str = '', HOST: str = '', PORT=0, USE_TLS=False, usr='', pwd='',
               charset: str = 'utf-8', IS_HTML: bool = True, attachments: object = None, mimetype: str = None):
    sender = Sender()
    sender.send_mail(msg, subject, TO, CC, BCC, FROM, HOST, PORT, USE_TLS, usr, pwd, charset, IS_HTML, attachments, mimetype)


@deprecated(deprecated_in='1.3.16', current_version=version, details='Use class Sender instead')
def send_telegram(message: str, chat_id: int = 161680036, subject: str = None):
    sender = Sender()
    sender.send_telegram(message, chat_id)


@deprecated(deprecated_in='1.3.16', current_version=version, details='Use class Sender instead')
def send_slack(message: str, webhook: str = None, channel: str = 'aims_integrations', username: str = 'aims_notifier',
               icon_url: str = None):
    sender = Sender()
    sender.send_slack(message, webhook, channel, username, icon_url)


if __name__ == '__main__':
    pass

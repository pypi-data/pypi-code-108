#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.import logging

import logging
from logging.handlers import SMTPHandler, TimedRotatingFileHandler

log_format_default = '[%(asctime)s] %(levelname)s %(module)s: %(funcName)s(%(lineno)d): %(message)s'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')


def get_app_mail_logger(app_name):
    # TODO find SMTP configuration
    mail_handler = SMTPHandler(
        mailhost='127.0.0.1',
        fromaddr='server-error@example.com',
        toaddrs=['admin@example.com'],
        subject='Application Error'
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))


def file_handler(app_name):
    rotating_file_handler = TimedRotatingFileHandler(
        filename='logs/%s.log' % app_name,
        when='midnight',
        backupCount=5
    )
    rotating_file_handler.setLevel(logging.WARNING)
    rotating_file_handler.setFormatter(
        logging.Formatter(log_format_default))
    return rotating_file_handler


def default_handler():
    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    return stream

import re
from email import policy
from email.message import EmailMessage, Message
from email.parser import BytesParser
from typing import Union

from nehushtan.mail.rfc822.NehushtanMessagePart import NehushtanMessagePart


class NehushtanEmailMessage:
    """
    Since 0.4.8
    """

    def __init__(self, msg: Union[EmailMessage, Message]):
        self.__email_message = msg
        self.__part = NehushtanMessagePart(self.__email_message, None)

    def get_email_message(self):
        return self.__email_message

    def get_part(self):
        return self.__part

    def read_field_from(self):
        return self.__email_message.get('From', '')

    def read_field_to(self):
        return self.__email_message.get('To', '')
        # x=self.__email_message.get('To','')
        # return NehushtanEmailMessage.parse_mail_address_line(x)

    def read_field_cc(self):
        return self.__email_message.get('cc', '')

    def read_field_bcc(self):
        return self.__email_message.get('bcc', '')

    def read_field_subject(self):
        return self.__email_message.get('Subject', '')

    def read_field_date(self):
        return self.__email_message.get('Date', '')

    @staticmethod
    def parse_bytes(text: bytes):
        # <class 'email.message.EmailMessage'>
        msg = BytesParser(policy=policy.default).parsebytes(text)
        return NehushtanEmailMessage(msg)

    @staticmethod
    def parse_mail_address_line(x: str):
        # print('parse_mail_address_line <-', x)

        # a1@b.c, a2@b.c
        # A1 <a1@b.c>, a2@b.c
        # A1 <a1@b.c>, A2 <a2@b.c>

        email_rule_express = r'([A-Za-z0-9.-]+@[A-Za-z0-9.-]+)|((\S*)\s*<([A-Za-z0-9.-]+@[A-Za-z0-9.-]+)>)'
        address_pieces = re.findall(email_rule_express, x)

        list_of_mail_address_tuple = []
        for address_piece in address_pieces:
            address = None
            name = None
            if address_piece[0]:
                address = address_piece[0]
                name = None
            elif address_piece[2] and address_piece[3]:
                address = address_piece[3]
                name = address_piece[2]
                # EncodedWordsKit.decode_string_following_rfc2047(name)

            list_of_mail_address_tuple.append((address, name))
        return list_of_mail_address_tuple

    @staticmethod
    def extract_email_address(x: str):
        """
        Since 0.4.9
        """
        email_rule_express = r'[A-Za-z0-9.-]+@[A-Za-z0-9.-]+'
        return re.findall(email_rule_express, x)

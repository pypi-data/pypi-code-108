from email.message import EmailMessage, Message
from typing import Union, Optional, List


class NehushtanMessagePart:
    """
    Since 0.4.8
    """

    def __init__(self, msg: Union[EmailMessage, Message], parent: Optional['NehushtanMessagePart']):
        self.__parent = parent
        self.__message = msg
        self.__sub_message_list: List['NehushtanMessagePart'] = []

        self.__organize_parts()

    def get_parent(self):
        return self.__parent

    def get_message(self):
        return self.__message

    def get_sub_message_list(self):
        return self.__sub_message_list

    def is_leaf(self):
        return len(self.__sub_message_list) == 0

    # def append_sub_message(self, sub_message):
    #     self.__sub_message_list.append(sub_message)
    #     return self

    def __organize_parts(self):
        if self.__message.is_multipart():
            for part in self.__message.iter_parts():
                self.__sub_message_list.append(NehushtanMessagePart(part, self))

    def get_content_charset(self):
        return self.__message.get_content_charset()

    def get_content_type(self):
        return self.__message.get_content_type()

    def get_content_disposition(self):
        return self.__message.get_content_disposition()

    def get_body_content(self, i=None):
        x: bytes = self.__message.get_payload(i=i, decode=True)
        return x.decode(encoding=self.__message.get_content_charset('ascii'))

    def get_attachement_filename_of_this_part(self) -> Optional[str]:
        if self.__message.is_attachment():
            return self.__message.get_filename()

    def get_attachement_content_of_this_part(self, i=None):
        if self.__message.is_attachment():
            attachment_content = self.__message.get_payload(i=i, decode=True)
            return attachment_content

    def save_attachement_of_this_part(self, target_file_path: str, i=None):
        with open(target_file_path, 'wb') as fp:
            fp.write(self.get_attachement_content_of_this_part(i=i))

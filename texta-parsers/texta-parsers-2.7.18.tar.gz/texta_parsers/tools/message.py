import email
import logging
import os
import sys
from random import getrandbits

from bs4 import BeautifulSoup

from texta_parsers.settings import META_FIELD


class HeaderParser:
    def __init__(self, msg):
        self.msg = msg
        self.fails = []


    def parse(self):
        header_data = {}
        from_name, from_addr = self._get_from()
        header_data["from_name"] = from_name
        header_data["from"] = " ".join([from_name, from_addr])
        header_data["to"] = self._get_addr("to")
        header_data["subject"] = self._get_subject()
        header_data["date"] = self._get_date()

        cc = self._get_addr("cc")
        bcc = self._get_addr("bcc")

        if (cc):
            header_data["cc"] = cc
        if (bcc):
            header_data["bcc"] = bcc

        return header_data


    def _get_from(self):
        try:
            addr_list = email.utils.getaddresses(self.msg.get_all("from", []))
            assert len(addr_list) <= 1

            if (addr_list):
                name, address = addr_list[0]
                name_dec, charset = email.header.decode_header(name)[0]
                name_str = self._decode(name_dec, charset, "from")

                address_dec, charset = email.header.decode_header(address)[0]
                address_str = self._decode(address_dec, charset, "from")

                return name_str, address_str
            return "", ""
        except:
            exc_type, value, _ = sys.exc_info()
            error_message = "EmailParser - From - {}: {}".format(exc_type.__name__, value)
            self.fails.append(error_message)
            return "", ""


    def _get_addr(self, field):
        try:
            addr_list = email.utils.getaddresses(self.msg.get_all(field, []))

            all_addresses = []
            for addr_tuple in addr_list:
                addr_items = []
                for item in addr_tuple:
                    item_dec, charset = email.header.decode_header(item)[0]
                    item_str = self._decode(item_dec, charset, "subject")

                    if (item_str):
                        addr_items.append(item_str)
                all_addresses.append(" ".join(addr_items))

            return "\n".join(all_addresses)

        except:
            exc_type, value, _ = sys.exc_info()
            error_message = "EmailParser - Address - {}: {}".format(exc_type.__name__, value)
            self.fails.append(error_message)
            return ""


    def _get_subject(self):
        if "subject" in self.msg:
            try:
                subject_parts = email.header.decode_header(self.msg["subject"])

                subject_items = []
                for item_dec, charset in subject_parts:
                    item_str = self._decode(item_dec, charset, "subject")

                    subject_items.append(item_str.strip())

                return " ".join(subject_items)

            except:
                exc_type, value, _ = sys.exc_info()
                error_message = "EmailParser - Subject - {}: {}".format(exc_type.__name__, value)
                self.fails.append(error_message)
                return ""
        else:
            return ""


    def _get_date(self):
        if "date" in self.msg:
            date = self.msg["date"]
            if (type(date) == str):
                return email.utils.parsedate_to_datetime(self.msg["date"])
            elif (type(date) == email.header.Header):
                encoded_date, charset = email.header.decode_header(self.msg["date"])[0]
                decoded_date = None
                try:
                    decoded_date = encoded_date.decode(charset)
                except:
                    decoded_date = encoded_date.decode("Windows-1251")

                if (decoded_date):
                    return email.utils.parsedate_to_datetime(decoded_date)


    def _decode(self, item, charset, field):
        try:
            item_str = ""
            if charset:
                item_str = item.decode(charset)
                # charset is None for non-encoded header parts and the part itself a bytestring
            elif type(item) == bytes:
                item_str = item.decode()
            else:
                # if whole header is non-encoded, result is a string
                assert type(item) == str
                item_str = item

            return item_str
        except:
            exc_type, value, _ = sys.exc_info()
            error_message = "EmailParser - Decode - {}: {}".format(exc_type.__name__, value)
            self.fails.append(error_message)
            return ""


class BodyParser:
    def __init__(self, msg):
        self.msg = msg
        self.fails = []


    def _parse_body_rec(self, msg):
        if msg.get_content_disposition() == "attachment":  # therefore attachment not body part
            return ""

        body = []
        message_content_type = msg.get_content_type()
        message_main_type = msg.get_content_maintype()

        if message_content_type == "multipart/mixed":
            for payload in msg.get_payload():
                body.append(self._parse_body_rec(payload))
        elif message_main_type == "text":
            body.append(self._parse_text_content(msg))
        elif message_content_type == "multipart/alternative":
            for payload in msg.get_payload():
                body.append(self._parse_body_rec(payload))
                break
        return "\n".join(body).strip()


    def parse_body(self):
        try:
            return self._parse_body_rec(self.msg)
        except:
            exc_type, value, _ = sys.exc_info()
            error_message = "EmailParser - Body - {}: {}".format(exc_type.__name__, value)
            self.fails.append(error_message)
            return ""


    def _parse_text_content(self, msg):
        body = ""
        subtype = msg.get_content_subtype()
        charset = msg.get_content_charset(failobj="us-ascii")

        if subtype == "html":
            cleaned_body = self._clean_html(msg.get_payload(decode=True).decode(charset))
            body = cleaned_body
        elif subtype == "plain":
            if (msg["Content-Transfer-Encoding"] == "8bit"):
                try:
                    body = msg.get_payload(decode=True).decode(charset)
                except UnicodeDecodeError:
                    body = msg.get_payload(decode=True).decode("latin1")
            else:
                body = msg.get_payload(decode=True).decode(charset)

        else:
            logging.warning("Content of this type not modified: {}".format(subtype))
            body = msg.get_payload(decode=True).decode(charset)

        return body


    def _parse_attachments_rec(self, msg, msg_id: str):
        attachments_jsons = []
        for payload in msg.get_payload():
            if type(payload) != str:
                if (payload.get_content_disposition() == "attachment" and payload.get_content_type() != "message/rfc822"):
                    a_parser = AttachmentParser(payload, msg_id)
                    attachment_data = a_parser.parse()

                    if a_parser.fails:
                        attachment_data.setdefault(META_FIELD, {})
                        attachment_data[META_FIELD].setdefault("errors", [])
                        attachment_data[META_FIELD]["errors"].extend(a_parser.fails)

                    attachments_jsons.append(attachment_data)
                elif payload.is_multipart() and payload.get_content_type() != "message/rfc822":
                    attachments_jsons += self._parse_attachments_rec(payload, msg_id)

        return attachments_jsons


    def parse_attachments(self, msg_id):
        return self._parse_attachments_rec(self.msg, msg_id)


    def _clean_html(self, payload):
        soup = BeautifulSoup(payload, features="lxml")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        text = "\n".join(line for line in lines if line)
        return text


class AttachmentParser(BodyParser):
    def __init__(self, msg, msg_id):
        BodyParser.__init__(self, msg)
        self.msg_id = msg_id


    def parse(self):
        attachment_id = str(getrandbits(64))
        attachment_json = {"parent_id": self.msg_id, "id": attachment_id}

        filename = self._get_filename()
        attachment_json["filename"] = filename

        attachment_json["content"] = self._get_payload()

        return attachment_json


    def _get_filename(self):
        try:
            encoded_filename = self.msg.get_filename()
            return AttachmentParser.parse_filename(encoded_filename)
        except:
            exc_type, value, _ = sys.exc_info()
            error_message = "EmailParser - Filename - {}: {}".format(exc_type.__name__, value)
            self.fails.append(error_message)
            return ""


    @staticmethod
    def parse_filename(encoded_filename):
        filename_parts = email.header.decode_header(encoded_filename)

        filename_items = []
        for item_dec, charset in filename_parts:
            if charset:
                item_str = item_dec.decode(charset)
            elif type(item_dec) == bytes:
                item_str = item_dec.decode()
            else:
                assert type(item_dec) == str
                item_str = item_dec

            filename_items.append(item_str.strip())

        return "".join(filename_items)


    def _get_payload(self) -> bytes:
        """
        Simply returns decoded payload (binary).
        """
        attachment_payload = self.msg.get_payload(decode=True)
        return attachment_payload


    def _make_dir(self, f_dir):
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)

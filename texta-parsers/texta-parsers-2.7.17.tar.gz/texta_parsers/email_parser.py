import logging
import mailbox
import os
import shutil
from random import getrandbits

from texta_parsers.settings import META_FIELD
from texta_parsers.tools.message import AttachmentParser, BodyParser, HeaderParser
from texta_parsers.tools.pst_extractor import check_readpst_exists, extract_pst_file
from texta_parsers.tools.extension import Extension


logging.basicConfig(
    format='%(levelname)s %(asctime)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.INFO
)


class EmailParser():
    """ 
    # Parameters 
    tmp_folder (string): folder for temporal files, (optional, default: "tmp")
    save_path (string): folder for non-temporal files, (optional, default: "parsed_files")
    supported_attachment_extensions (set): only parse known extensions, (optional)
    """

    def __init__(self, tmp_folder="tmp", save_path="parsed_files", supported_attachment_extensions=Extension.KNOWN_EXTENSIONS):
        self.tmp_folder = tmp_folder
        self.save_path = save_path
        self.save_mails = None
        self.supported_attachment_extensions = supported_attachment_extensions
        if not check_readpst_exists():
            raise FileNotFoundError("Readpst not found. Can not initialize parser.")


    def parse(self, input_path: str, save_mails: bool = False):
        """Parses emails from given folder or file.

        # Parameters
        input_path (str): Path to folder or file that contains emails
        save_mails (bool): whether to save emails to files (optional, default: False)

        # Returns
        Generator which yields emails in format (msg_json, [attachment_json])
        """
        email_files = self._get_files(input_path)
        self.save_mails = save_mails
        self._make_dirs()

        for email_file, ext in email_files:
            logging.info("Parsing {}".format(email_file))

            if ext == ".mbox":
                folder_name = email_file.split("/")[-1].split(".")[0]

                for msg_json, attachment_jsons in map(self._parse_msg, mailbox.mbox(email_file)):
                    if (msg_json != {}):
                        msg_json["original_folder"] = folder_name
                    yield msg_json, attachment_jsons

            elif ext == ".pst":
                extracted_mboxes = extract_pst_file(email_file, self.tmp_folder)
                for mbox_file in extracted_mboxes:
                    logging.info("Parsing from .pst {}".format(mbox_file))
                    folder_name = mbox_file.split("/")[-1].split(".")[0]

                    for msg_json, attachment_jsons in map(self._parse_msg, mailbox.mbox(mbox_file)):
                        if (msg_json != {}):
                            msg_json["original_folder"] = folder_name
                        yield msg_json, attachment_jsons

                self._delete_extracted_pst(self.tmp_folder)

            elif ext == ".eml":
                raw_msg = self._load_raw_mail(email_file)
                msg = mailbox.Message(raw_msg)
                msg_json, attachment_jsons = self._parse_msg(msg)
                yield msg_json, attachment_jsons


    def _parse_msg_rec(self, msg, msg_id: str):
        """Parses given message recursively using parsers in message module for different parts
        """
        is_root_msg = msg_id == ""

        if is_root_msg:  # is main email, parse it accordingly
            msg_data, attachments = self._get_all_msg_data(msg)
            msg_id = msg_data["id"]

        else:  # is message/rfc822 attachment, parse it as an email with respective parsers
            try:
                filename = AttachmentParser.parse_filename(msg.get_filename())
            except:
                filename = ""

            msg = msg.get_payload()[0]
            msg_data, attachments = self._get_all_msg_data(msg)
            msg_data["parent_id"] = msg_id
            msg_data["filename"] = filename

            for attachment in attachments:
                # replace parent_id the id of correct parent
                attachment["parent_id"] = msg_data["id"]

            attachments.append(msg_data)

        # parse other message/rfc822 attachments if there is any
        if msg.is_multipart():
            for payload in msg.get_payload():
                if payload.get_content_type() == "message/rfc822":
                    _, nested_attachments = self._parse_msg_rec(payload, msg_id)

                    if (self.save_mails):
                        # save sub-mails if required as we won't see it's payload later
                        print("saving mail with id", nested_attachments[-1]["id"])
                        filepath = self._save_mail_as_eml(payload, msg_id + "/" + nested_attachments[-1]["id"])
                        if (filepath):
                            nested_attachments[-1]["location"] = filepath

                    attachments += nested_attachments

        return msg_data, attachments


    def _parse_msg(self, msg):
        try:
            msg_json, attachment_jsons = self._parse_msg_rec(msg, "")
            if (self.save_mails):
                filepath = self._save_mail_as_eml(msg, msg_json["id"])
                if (filepath):
                    msg_json["location"] = filepath
            return msg_json, attachment_jsons
        except Exception as e:
            # in case all other more specific exceptions handlers have failed
            logging.warning(e)
            return {}, []


    def _get_all_msg_data(self, msg):
        h_parser = HeaderParser(msg)
        b_parser = BodyParser(msg)

        msg_data = h_parser.parse()
        body = b_parser.parse_body()
        msg_data["body"] = body

        msg_id = str(getrandbits(64))
        msg_data["id"] = msg_id

        attachments = b_parser.parse_attachments(msg_id)

        failures = h_parser.fails + b_parser.fails
        if failures:
            msg_data.setdefault(META_FIELD, {})
            msg_data[META_FIELD].setdefault("errors", [])
            msg_data[META_FIELD]["errors"].extend(failures)

        return msg_data, attachments


    def _get_files(self, path):
        """Returns a list of email files from given folder (recursive) or a list with single file if input is file.
        """
        results = []
        if os.path.isfile(path):
            res = Extension.file_is_mail(path)
            if (res):
                results.append((path, res))
        else:
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    full_file = os.path.join(dirpath, filename)
                    res = Extension.file_is_mail(full_file)
                    if (res):
                        results.append((full_file, res))

        return results


    def _load_raw_mail(self, path):
        with open(path, "rb") as f:
            raw_mail = f.read()
        return raw_mail


    def _make_dirs(self):
        for path in [self.tmp_folder, self.save_path]:
            if (path != None):
                if not os.path.exists(path):
                    os.makedirs(path)


    def _save_mail_as_eml(self, message, msg_id):
        save_path = os.path.join(self.save_path, "mails")
        msg_path = os.path.join(save_path, msg_id + ".eml")

        if not os.path.exists(os.path.dirname(msg_path)):
            os.makedirs(os.path.dirname(msg_path))

        try:
            with open(msg_path, "wb") as f:
                f.write(bytes(message))
            return msg_path
        except KeyError:
            logging.error("Failed flattening file with id {}".format(msg_id))
            return None


    def _delete_extracted_pst(self, pst_dir):
        """Deletes the content of the tmp folder which is used for temporarily extracting pst files
        """
        for root, dirs, files in os.walk(pst_dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

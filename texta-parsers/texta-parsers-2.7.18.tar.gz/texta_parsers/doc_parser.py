import csv
import os
import shutil
import sys
import uuid
from subprocess import Popen
import logging
import pandas as pd
from tika import parser

from texta_parsers.email_parser import EmailParser
from texta_parsers.settings import META_FIELD
from texta_parsers.tools import utils
from texta_parsers.tools.extension import Extension
from texta_parsers.tools.scanner import DocScanner
from texta_parsers.tools.archive import ArchiveExtractor
from . import exceptions


logging.basicConfig(
    format='%(levelname)s %(asctime)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.INFO
)


class DocParser:

    def __init__(self,
                 save_attachments=False,
                 save_mails=False,
                 save_documents=False,
                 parse_attachments=True,
                 allowed_attachment_extensions=Extension.KNOWN_EXTENSIONS,
                 save_path="parsed_files",
                 temp_dir="",
                 languages=["est", "eng", "rus"],
                 max_file_size=100,
                 ignore_digidoc=False):

        """
        :param: bool save_attachments: Whether to save email attachments.
        :param: bool save_mails: Whether to save emails.
        :param: bool save_documents: Whether to save files (other than emails and attachments).
        :param: bool parse_attachments: Whether to parse the content of attached files in email.
        :param: set allowed_attachment_extensions: Limit the extensions used in attachment parsing to remove images etc. if required.
        :param: str save_path: Base directory for files to be saved permanently.
        :param: str temp_dir: Base directory for files to be saved temporary.
        :param: [str] languages: Tika OCR languages.
        :param: int max_file_size: Maximum file size in MBs that will be parsed. Does not apply to mailbox files.
        :param: [bool] ignore_digidoc: Whether digidoc containers should be ignored.
        """

        self.save_attachments = save_attachments
        self.allowed_attachment_extensions = allowed_attachment_extensions
        self.save_mails = save_mails
        self.save_documents = save_documents
        self.parse_attachments = parse_attachments
        self.save_path = save_path
        self.max_file_size = max_file_size
        self.temp_dir_path = temp_dir
        self.langs = languages
        self.ignore_digidoc = ignore_digidoc
        self.scanner = DocScanner()

        if (self.ignore_digidoc == False):
            if not utils.check_digidoc_exists():
                raise FileNotFoundError("Digidoc-tool not found. Either set ignore_digidoc=True or install the tool.")


    def create_temp_dir_for_parse(self):
        """
        Creates temp directory path.
        """
        temp_dir_for_parse = os.path.join(self.temp_dir_path, "temp_" + uuid.uuid4().hex)
        if not os.path.exists(temp_dir_for_parse):
            os.mkdir(temp_dir_for_parse)
        return temp_dir_for_parse


    def _write_uploaded_to_file(self, uploadedfile, file_name):
        if not file_name:
            raise exceptions.InvalidInputError("File name not supported.")
        # get extension from file name if any
        extension = Extension.predict(uploadedfile, file_name=file_name)
        # create new path with predicted extension
        new_name = uuid.uuid4().hex + extension
        # new_name = uploadedfile.name
        file_path = os.path.join(self.temp_dir, new_name)
        with open(file_path, "wb") as fh:
            fh.write(uploadedfile)
        return file_path


    def remove_temp_dir(self):
        """
        Removes temp directory path.
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


    def _parse_file(self, document):
        """
        Parses document using TIKA (for everything) and FaceAnalyzer (for images).
        """
        output_document = {}
        tika_options = {
            "headers": {
                "X-Tika-OCRLanguage": "+".join(self.langs),
                "X-Tika-PDFextractInlineImages": "true"
            }
        }

        # extract text using TIKA
        tika_output = parser.from_file(document["path"], requestOptions=tika_options)
        content = tika_output["content"]
        if content != None:  # remove leading and trailing spacing
            lines = (line.strip() for line in content.splitlines())
            content = "\n".join(line for line in lines if line)
        else:
            content = ""
        output_document["text"] = content
        # return as list
        return [output_document]


    @staticmethod
    def _file_size_ok(max_file_size, document):
        if (os.path.getsize(document["path"]) > max_file_size * 1024 ** 2):
            return False
        return True


    @staticmethod
    def _parse_collection(document):
        if (document["extension"] == ".csv"):
            # detect dialect and whether contains header
            with open(document["path"]) as f:
                lines = f.readline() + '\n' + f.readline()
                dialect = csv.Sniffer().sniff(lines)
                f.seek(0)

                has_header = csv.Sniffer().has_header(lines)
                f.seek(0)

            header = "infer" if has_header else None
            # read and yield actual data with pandas (more convenient)
            # skip rows that thrown an error and hide the warning message with 'warn_bad_lines'
            reader = pd.read_csv(document["path"], dialect=dialect, chunksize=1000, header=header, error_bad_lines=False, warn_bad_lines=False, dtype='string')

            for chunk in reader:
                for _, row in chunk.iterrows():
                    row.fillna("", inplace=True)
                    yield row.to_dict()

        # .xls or .xlsx
        else:
            # Enforce str type with 'dtype' to avoid schema conflicts in Elasticsearch.
            # TODO Find a better solution to handle types.
            reader = pd.read_excel(document["path"], header=0, sheet_name=None, dtype='string')  # dont know whether there is a header but assume that the first row is

            if isinstance(reader, dict):
                for _, df in reader.items():
                    df.fillna("", inplace=True)
                    for _, row in df.iterrows():
                        yield row.to_dict()
            else:
                reader.fillna("", inplace=True)
                for _, row in reader.iterrows():
                    yield row.to_dict()


    def save_attachment(self, attachment):
        if (self.save_attachments == True):
            save_path = os.path.join(self.save_path, "attachments", attachment["parent_id"])

            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            attachment_path = attachment[META_FIELD].get("path")
            
            if attachment_path:
                extension = attachment[META_FIELD].get("extension")
                if not extension:
                    extension = Extension.predict(attachment_path)
                    attachment[META_FIELD]["extension"] = extension

                filename = os.path.join(save_path, uuid.uuid4().hex + extension)

                shutil.copyfile(attachment[META_FIELD]["path"], filename)
                attachment[META_FIELD]["location"] = filename
        return True


    def save_document(self, meta):
        if (self.save_documents == True):
            extension = meta["extension"]
            save_path = os.path.join(self.save_path, "files", extension[1:])

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            filename = os.path.join(save_path, uuid.uuid4().hex + extension)
            path = meta.get("path")
            if path:
                shutil.copyfile(meta["path"], filename)
                meta["location"] = filename
        return True


    def _overwrite_bytes_content(self, content: dict):
        for key, value in content.items():
            if isinstance(value, bytes):
                content[key] = ""
        return content


    def _parse_attachment(self, attachment):
        parsed_attachment = list(self._parse(attachment["content"], attachment["filename"], save_to_file=False))  # this could be a list of multiple files

        extension = Extension.predict(attachment["content"], file_name=attachment["filename"])
        is_archive = extension in Extension.ARCHIVE_EXTENSIONS

        extracted_attachments = []
        for ix, sub_file in enumerate(parsed_attachment):
            # replicate the fields of original attachment to sub attachment
            sub_attachment = attachment.copy()
            sub_attachment["content"] = sub_file["text"]

            # infer filename from teporal path since the original was extension
            if (is_archive):
                sub_attachment["filename"] = os.path.split(sub_file["properties"]["path"])[1]

            # also add metadata of the file to the dictionary
            sub_attachment[META_FIELD] = sub_file[META_FIELD]

            # also add potential error messages
            sub_file.setdefault(META_FIELD, {})
            sub_file[META_FIELD].setdefault("errors", [])
            subfile_errors = sub_file[META_FIELD]["errors"]

            if subfile_errors:
                sub_attachment.setdefault(META_FIELD, {})
                sub_attachment[META_FIELD].setdefault("errors", [])
                sub_attachment[META_FIELD]["errors"].extend(subfile_errors)

            # in case the attachment was an archive and contained multiple files,
            # add index number to attachment id to show it 
            if (len(parsed_attachment) > 1):
                sub_attachment["id"] = sub_attachment["id"] + "_" + str(ix + 1)

            # remove files we should not parse
            if sub_attachment[META_FIELD].get("extension") in self.allowed_attachment_extensions:
                extracted_attachments.append(sub_attachment)
 
        return extracted_attachments


    def _parse(self, parser_input, file_name=None, save_to_file=True):
        """
        :param: str parser_input: Base64 string or file path.
        :param: bool save_to_file: As this function is recursive, specifies whether the file
            should be saved so it won't be saved multiple times when parsing complex structures.
        """
        if isinstance(parser_input, bytes):
            # input is in bytes
            file_paths = [self._write_uploaded_to_file(parser_input, file_name)]
        elif isinstance(parser_input, str):
            # input is path to file as string
            if not os.path.exists(parser_input):
                raise exceptions.InvalidInputError("File does not exist.")
            # input is a directory and we should scan it
            if os.path.isdir(parser_input):
                file_paths = self.scanner.scan(parser_input)
            else:
                file_paths = [parser_input]
        else:
            raise exceptions.InvalidInputError("Input should be path to file/directory or bytes.")

        # apply parsers for all paths in input
        for file_path in file_paths:
            docs_to_parse = []
            # guess extension (it also performs check if extension is known)
            extension = Extension.predict(file_path, file_name=file_name)

            if (self.ignore_digidoc == True and extension in Extension.DIGIDOC_EXTENSIONS):
                continue

            # in case of an arcive, extract all files from it
            if extension in Extension.ARCHIVE_EXTENSIONS:
                docs_to_parse = list(ArchiveExtractor().extract(file_path, self.temp_dir, extension))
            else:
                docs_to_parse.append({"path": file_path, "extension": extension})

            for doc in docs_to_parse:
                doc["origin"] = file_name if file_name != None else doc["path"]

            # parse all files
            for meta in docs_to_parse:
                # check size for anything but mailboxes, because they are huge
                if (not self._file_size_ok(self.max_file_size, meta)):
                    meta.setdefault("errors", [])
                    meta["errors"].append("File too large for parsing.")
                    yield {META_FIELD: meta}
                # deal with mailboxes etc
                # email parser handles all the errors and logs uncaught
                elif (meta["extension"] in Extension.EMAIL_EXTENSIONS):
                    parser = EmailParser(tmp_folder=self.temp_dir, save_path=self.save_path)
                    generator = parser.parse(meta["path"], save_mails=self.save_mails)

                    for msg_dict, attachment_dicts in generator:
                        msg_dict[META_FIELD] = meta.copy()  
                        # attachments in attachment_dicts are not parsed and the field content only contains raw payload in bytes.
                        # thus we need to call parse function on each content to get the text.
                        # moreover, each payload can potentially contain multiple files if it is an archive, for instance.
                        extracted_attachments = []
                        for attachment in attachment_dicts:
                            attachment.setdefault(META_FIELD, {})  # Ensure that the meta field exists.

                            if ("subject" in attachment):  # is actually mail, do not parse it (already parsed!)
                                attachment[META_FIELD] = meta.copy()
                                extracted_attachments.append(attachment)
                            else:
                                if (self.parse_attachments == True):
                                    try:
                                        extracted_attachments += self._parse_attachment(attachment)
                                    except:
                                        exc_type, value, _ = sys.exc_info()
                                        error_msg = "DocParser - Content - {}: {}".format(exc_type.__name__, value)

                                        attachment.setdefault(META_FIELD, {})
                                        attachment[META_FIELD].setdefault("errors", [])
                                        attachment[META_FIELD]["errors"].append(error_msg)

                                        extracted_attachments += [attachment]
                                        # Remove bytes that can be left in because of exceptions as they can
                                        # not be parsed by Elasticsearch.
                                        self._overwrite_bytes_content(attachment)

                                    # save attachments if specified
                                    for attachment in extracted_attachments:
                                        if ("subject" not in attachment):  # is actually mail, do not save it (already in email_parser if specified so!)
                                            self.save_attachment(attachment)

                                else:
                                    for attachment in attachment_dicts:
                                        attachment[META_FIELD] = meta.copy()
                                        if ("subject" not in attachment):
                                            if ("content" in attachment):
                                                attachment.pop("content", None)
                                            self.save_attachment(attachment)

                        yield msg_dict, extracted_attachments if self.parse_attachments else attachment_dicts

                # parse collections
                elif (meta["extension"] in Extension.COLLECTION_EXTENSIONS):
                    if (save_to_file):
                        self.save_document(meta)
                    generator = self._parse_collection(meta)
                    try:
                        for item in generator:
                            item[META_FIELD] = meta.copy()
                            yield item
                    except:
                        exc_type, value, _ = sys.exc_info()
                        error_msg = "DocParser - Content - {}: {}".format(exc_type.__name__, value)
                        meta.setdefault("errors", [])
                        meta["errors"].append(error_msg)
                        yield {META_FIELD: meta}

                # parse everything else
                else:
                    if (save_to_file):
                        self.save_document(meta)
                    try:
                        for parsed_document in self._parse_file(meta):
                            parsed_document[META_FIELD] = meta.copy()
                            yield parsed_document
                    except:
                        exc_type, value, _ = sys.exc_info()
                        error_msg = "DocParser - Content - {}: {}".format(exc_type.__name__, value)
                        meta.setdefault("errors", [])
                        meta["errors"].append(error_msg)
                        yield {META_FIELD: meta}


    def _remove_temp_path_ref(self, item):
        if (type(item) == tuple):
            item[0][META_FIELD].pop("path", None)
            for t in item[1]:
                t[META_FIELD].pop("path", None)
        else:
            item[META_FIELD].pop("path", None)


    def parse(self, parser_input, file_name=None):
        self.temp_dir = self.create_temp_dir_for_parse()
        generator = self._parse(parser_input, file_name)
        for item in generator:
            self._remove_temp_path_ref(item)
            yield item
        self.remove_temp_dir()

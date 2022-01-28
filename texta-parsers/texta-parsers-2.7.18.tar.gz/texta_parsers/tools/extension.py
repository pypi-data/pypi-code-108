import mimetypes
import os

import magic

from texta_parsers import exceptions


class Extension:
    AUDIO_EXTENSIONS = ()
    DIGIDOC_EXTENSIONS = (".ddoc", ".bdoc", ".asice", ".asics")
    DOC_EXTENSIONS = (".doc", ".docx", ".odt", ".pdf", ".rtf", ".htm", ".html", ".epub", ".txt")
    IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".gif", ".png", ".bmp", ".tiff")
    COLLECTION_EXTENSIONS = (".csv", ".xls", ".xlsx")
    EMAIL_EXTENSIONS = (".mbox", ".pst", ".eml")

    # ARCHIVE_EXTENSIONS = (".zip", ".tar", ".bz2", ".gz") + DIGIDOC_EXTENSIONS
    # requires patool to be installed
    # .rz - requires rzip
    # .lz - requires lzip
    # ".lrz", ".lha", ".lzh" - what to use?
    ARCHIVE_EXTENSIONS = (".7z", ".bz2", ".gz", ".rar", ".tar", ".xz", ".zip") + DIGIDOC_EXTENSIONS
    # union of all known extensions used in parsing
    KNOWN_EXTENSIONS = ARCHIVE_EXTENSIONS + DOC_EXTENSIONS + AUDIO_EXTENSIONS + COLLECTION_EXTENSIONS + IMAGE_EXTENSIONS + EMAIL_EXTENSIONS
    # these files are always identified by extension, because magic misidentifies them or because it is particularly important that these 
    # files are identified correctly and we trust extension more than magic for these file types
    EXTENSION_OVERWRITES = DIGIDOC_EXTENSIONS + AUDIO_EXTENSIONS + EMAIL_EXTENSIONS + COLLECTION_EXTENSIONS


    def __init__(self):
        pass


    @staticmethod
    def is_supported(file, file_name=None, allowed_extensions=None):
        """
        Tests if file is supported.
        :param file: either bytes or string to filepath.
        :param file_name: if file is bytes then file_name is always given.
        :param allowed_extensions: which extensions would be allowed.
        :return: bool.
        """
        if not allowed_extensions:
            allowed_extensions = Extension.KNOWN_EXTENSIONS
        try:
            prediction = Extension.predict(file, file_name=file_name)
            if prediction in allowed_extensions:
                return True
        except exceptions.UnsupportedFileError:
            return False
        return False

    @staticmethod
    def _has_msg_mimetype(input):
        mimetype = magic.from_buffer(input, mime=True)
        return mimetype == "message/rfc822"


    @staticmethod
    def _begins_like_mbox(input):
        try:
            return input.decode().startswith("From ")
        except:
            return False

    @staticmethod
    def _try_get_file_beginning(file):
        if isinstance(file, bytes):
            return file[:2048]
        else:
            try:
                return open(file, "rb").read(2048)
            except:
                return None

    @staticmethod
    def file_is_mail(filename):
        file_beginning = Extension._try_get_file_beginning(filename)

        ext = os.path.splitext(filename)[1]
        if ext in Extension.EMAIL_EXTENSIONS:
            return ext

        if (file_beginning == None):
            return None
        elif (Extension._has_msg_mimetype(file_beginning)):
            return ".eml"
        elif (Extension._begins_like_mbox(file_beginning)):
            return ".mbox"

    @staticmethod
    def predict(file, file_name=None):
        """
        Tries to validate magic output with some trivial hacks.
        Magic tends to mess up some files for some reason. Magic also fails on digidoc files.
        So let's do some double checks to be sure we parse it correctly.
        :param: file: either bytes or string to filepath.
        :param: file_name: if file is bytes then file_name is always given. 
        :return: File extension as string.
        """
        if isinstance(file, bytes):
            # input is file as bytes
            mime_type = magic.from_buffer(file, mime=True)
        else:
            # input is a path to file
            mime_type = magic.from_file(file, mime=True)
            file_name = file

        # let magic guess the extension based on mime
        guessed_extensions = mimetypes.guess_all_extensions(mime_type)
        # try extracting extenion from file name
        _, ext = os.path.splitext(file_name)
        parsed_ext = ext.lower()

        # extra check for mail or mailbox files
        mail_ext = Extension.file_is_mail(file_name)

        # final call
        if mail_ext:
            predicted_ext = mail_ext
        elif parsed_ext in Extension.EXTENSION_OVERWRITES or not guessed_extensions:
            predicted_ext = parsed_ext
        else:
            ### From the list of predicted possible extensions choose the one which is known, if possible
            guessed_known_exts = [ext for ext in guessed_extensions if ext in Extension.KNOWN_EXTENSIONS]
            predicted_ext = guessed_known_exts[0] if len(guessed_known_exts) > 0 else guessed_extensions[0]

        #if (predicted_ext not in Extension.KNOWN_EXTENSIONS):
        #    raise exceptions.UnsupportedFileError("File type not supported.")

        return predicted_ext

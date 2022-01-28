from subprocess import Popen
import bz2
import gzip
import lzma
import uuid
import os
import py7zr
from pyunpack import Archive
from texta_parsers.tools import rar_extractor, tar_extractor
from texta_parsers.tools.extension import Extension
from texta_parsers.exceptions import UnsupportedFileError


FNULL = open(os.devnull, "w")


class ArchiveExtractor:

    def _extract_digidoc(self, input_path, output_dir, extracted=[], processed={}):
        """
        Extracts contents from digidoc. Works recursively.
        """
        cmd = f'digidoc-tool open "{input_path}" --extractAll={output_dir}'
        p = Popen(cmd, shell=True, stdout=FNULL)
        p.wait()
        # generate full paths for the output
        extracted_docs = os.listdir(output_dir)
        extracted_docs = [os.path.join(output_dir, file_name) for file_name in extracted_docs]
        # extract further if digidocs in output
        for extracted_doc in extracted_docs:
            ext = Extension.predict(extracted_doc)
            if ext in Extension.KNOWN_EXTENSIONS and extracted_doc not in processed:
                if ext in Extension.DIGIDOC_EXTENSIONS:
                    processed[extracted_doc] = True
                    self._extract_digidoc(extracted_doc, output_dir, extracted=extracted)
                else:
                    extracted.append(extracted_doc)
        return extracted


    def _extract_rar(self, input_path, output_dir):
        rar_extractor.extract_rar_file(input_path, output_dir)


    def _extract_tar(self, input_path, output_dir):
        tar_extractor.extract_tar_file(input_path, output_dir)


    def _extract_7z(self, input_path, output_path):
        with py7zr.SevenZipFile(input_path, mode='r') as z:
            z.extractall(path=output_path)


    def _extract_bz2(self, input_path, output_path):
        output_loc = os.path.join(output_path, "out.decompressed")
        with open(output_loc, 'wb') as out_file, bz2.BZ2File(input_path, 'rb') as in_file:
            for data in iter(lambda: in_file.read(100 * 1024), b''):
                out_file.write(data)


    def _extract_gz(self, input_path, output_path):
        output_loc = os.path.join(output_path, "out.decompressed")
        with open(output_loc, 'wb') as out_file, gzip.GzipFile(input_path, 'rb') as in_file:
            for data in iter(lambda: in_file.read(100 * 1024), b''):
                out_file.write(data)


    def _extract_xz(self, input_path, output_path):
        output_loc = os.path.join(output_path, "out.decompressed")
        with open(output_loc, 'wb') as out_file, lzma.LZMAFile(input_path, 'rb') as in_file:
            for data in iter(lambda: in_file.read(100 * 1024), b''):
                out_file.write(data)


    def extract(self, input_path, output_dir, extension):
        """
        Extracts contents from archives. Works recursively.
        """
        # create temporary output directory
        # just to be safe, because file names may repeat
        output_dir = os.path.join(output_dir, uuid.uuid4().hex)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # extract with digidoc client
        if extension in Extension.DIGIDOC_EXTENSIONS:
            self._extract_digidoc(input_path, output_dir)
        elif extension == ".rar":
            self._extract_rar(input_path, output_dir)
        elif extension == ".tar":
            self._extract_tar(input_path, output_dir)
        elif extension == ".7z":
            self._extract_7z(input_path, output_dir)
        # Note: as the name of the file in the bz2 archive is unknow,
        # extension prediction relies entirely on magic, which tends to fail
        # in some cases (e.g digidoc)
        elif extension == ".bz2":
            self._extract_bz2(input_path, output_dir)
        elif extension == ".gz":
            self._extract_gz(input_path, output_dir)
        elif extension == ".xz":
            self._extract_xz(input_path, output_dir)
        else:
            archive = Archive(input_path)
            archive.extractall(output_dir)
        # generate full paths for the output
        extracted_paths = os.listdir(output_dir)
        extracted_paths = [os.path.join(output_dir, file_name) for file_name in extracted_paths]
        # extract further if archives in output
        for extracted_path in extracted_paths:
            if os.path.isdir(extracted_path):
                ### TODO: HOLY SHIT ITS A DIRECTORY INSIDE AN ARCHIVE!
                pass
            else:
                try:
                    extracted_extension = Extension.predict(extracted_path)
                    if extracted_extension in Extension.ARCHIVE_EXTENSIONS:
                        for doc in self.extract(extracted_path, output_dir, extracted_extension):
                            yield doc
                    else:
                        yield {"path": extracted_path, "extension": extracted_extension}
                except UnsupportedFileError as e:
                    yield {"path": extracted_path, "extension": None}

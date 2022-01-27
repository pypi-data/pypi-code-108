import hashlib
import io
import os
import shutil
import tempfile
from csv import DictWriter, DictReader
from typing import List, Optional


class ElasticDictWriter:
    """
    DictWriter, built on top of Python csv.DictWriter, that supports automatic extension of headers
    according to what data it receives.

    The result file always has a complete header (as defined by fieldnames) or it is extended if some new columns
     are introduced in the data. It always produces a valid CSV (missing columns are filled with blanks).

     It uses a series of cached writers / files that are merged into a single one with final set of columns on close()

     NOTE: If not using "with" statement, close() method must be called at the end of processing to get the result.

     NOTE: Does not keep the order of rows added - the rows containing additional headers always come first:

    Example:
        ```
        wr = ElasticDictWriter(file_path, ["a", "b" , "c"])
        wr.write({"a":1,"b":2"})
        wr.writer({"b":2", "d":4})
        wr.close()
        ```

        leads to CSV with following content:

        "a","b","c","d"
         ,2,,4
        1,2,,

    """

    def __init__(self, file_path: str, fieldnames: List[str], temp_directory: Optional[str] = None,
                 dialect: str = "excel", buffering=io.DEFAULT_BUFFER_SIZE,
                 *args, **kwargs):
        """

        Args:
            file_path: result file path
            fieldnames:  Minimal column list
            temp_directory:  Optional path to a temp directory for cached files. By default the same directory as the
        output file is used. Temporary files/directory are deleted on close.
            dialect:  As in Python csv package
            buffering:   As in Python csv package
            *args: Additional positional arguments to initialize underlying DictWriters, as in csv package
            **kwargs: Additional named arguments to initialize underlying DictWriters, as in csv package
        """

        self.result_path = file_path
        self.fieldnames = fieldnames
        # global writer properties
        self.dialect = dialect
        self._args = args
        self._kwds = kwargs

        self._buffering = buffering
        self.encoding = kwargs.get('encoding', 'utf-8')

        self._write_header = False

        if not temp_directory:
            temp_directory = tempfile.mkdtemp()

        os.makedirs(temp_directory, exist_ok=True)
        self.temp_directory = temp_directory
        # set initial key value of the complete writer
        self._complete_writer_key = None
        # hashing method
        self._hash_method = self._generate_hashed_header_key
        self._writer_cache = {}
        self._tmp_file_cache = {}
        self._get_or_add_cached_writer(fieldnames)

    def writeheader(self):
        """
        Call to write the columns header in the resulting CSV.

        Note: the header is actually written after the writer is closed (close() called)
        """
        self._write_header = True

    def writerow(self, row_dict: dict):
        cols = list(row_dict.keys())
        writer = self._get_or_add_cached_writer(cols)
        writer.writerow(row_dict)

    def writerows(self, row_dicts: List[dict]):
        for r in row_dicts:
            self.writerow(r)

    def _update_complete_header(self, columns):
        cols_to_add = set(columns).difference(set(self.fieldnames))
        self.fieldnames.extend(cols_to_add)
        return self.fieldnames

    def _get_or_add_cached_writer(self, columns):
        writer_key = self._build_writer_key(columns)
        wr = self._writer_cache.get(writer_key)
        if not wr:
            tmp_file = os.path.join(self.temp_directory, writer_key)
            t_file = open(tmp_file, 'wt+', newline='', buffering=self._buffering, encoding=self.encoding)
            self._tmp_file_cache[writer_key] = t_file
            wr = DictWriter(t_file, self.fieldnames.copy(), *self._args, **self._kwds)
            wr.writeheader()
            self._writer_cache[writer_key] = wr

        return wr

    def _build_writer_key(self, columns):
        """
        Returns a writer key / complete or extended one. Updates the complete header set.
        :param columns:
        :return:
        """
        if not set(columns).issubset(self.fieldnames) or not self._complete_writer_key:
            new_header = self._update_complete_header(columns)
            self._complete_writer_key = self._hash_method(list(new_header))

        return self._complete_writer_key

    @staticmethod
    def _generate_hashed_header_key(columns):
        # sort cols
        columns.sort()
        return hashlib.md5('_'.join(columns).encode('utf-8')).hexdigest()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Close all output streams / files and build and move the final result file.
        Has to be called before result processing.

        :return:
        """
        final_header = list(self.fieldnames)
        final_writer = self._get_or_add_cached_writer(final_header)
        final_writer_key = self._build_writer_key(final_header)
        if len(self._writer_cache) == 1:
            # headers were the same
            self._tmp_file_cache[final_writer_key].close()
        else:
            self._writer_cache.pop(final_writer_key)
            self._append_missing_rows_and_close(final_writer, self._writer_cache, final_writer_key)

        src_file = os.path.join(self.temp_directory, final_writer_key)

        # write the result and add header.
        with open(src_file, 'r', encoding=self.encoding) as source_file, open(self.result_path, 'w',
                                                                              buffering=self._buffering,
                                                                              encoding=self.encoding) as target_file:
            if not self._write_header:
                source_file.readline()
            # this will truncate the file, so need to use a different file name:
            shutil.copyfileobj(source_file, target_file)

        # cleanup
        shutil.rmtree(self.temp_directory)

    def _append_missing_rows_and_close(self, final_writer, writers: dict, final_writer_key):
        """
        Appends missing rows (with less columns) to a final writer
        :param final_writer: final writer with complete set of headers
        :param writers: writers with smaller header
        :return:
        """
        # close all writers and writer headers
        for wkey in writers:
            self._tmp_file_cache[wkey].close()
            file_path = os.path.join(self.temp_directory, wkey)
            self._append_data(final_writer, file_path)

        self._tmp_file_cache[final_writer_key].close()

    def _append_data(self, final_writer, partition_path):
        with open(partition_path, mode='rt', encoding='utf-8') as in_file:
            reader = DictReader(in_file)
            for r in reader:
                final_writer.writerow(r)

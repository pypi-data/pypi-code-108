# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk lookup file helper functions module"""
import csv
import platform
import sys

if platform.system() == "Windows":
    csv.field_size_limit(int((1 << 31) - 1))
else:
    csv.field_size_limit(sys.maxsize)


# From http://docs.splunk.com/Documentation/SplunkCloud/6.6.0/Knowledge/ConfigureCSVlookups:
LOOKUP_HEADER_CHAR_LIMIT = 4096
LOOKUP_EMPTY_MESSAGE = "Lookups should not be empty. Please remove this lookup."
LOOKUP_HEADER_CHAR_LIMIT_MESSAGE = (
    f"Lookups headers should contain no more than {LOOKUP_HEADER_CHAR_LIMIT} characters. "
    "Please edit/remove this lookup."
)
LOOKUP_MAC_LINE_ENDINGS_MESSAGE = (
    "Lookups should not contain pre-OS X (OS 9 or earlier) Macintosh-style"
    " line endings. Please edit/remove this lookup."
)
LOOKUP_COLUMN_MISMATCH_MESSAGE = (
    "The number of columns in row {row} ({row_column} columns) does not match the number of"
    " columns in the csv's header ({header_column} columns). The header is considered row"
    " 1. Please edit/remove this lookup."
)
LOOKUP_NON_UTF8_MESSAGE = (
    "Lookups should only contain utf-8 characters. Plain ascii text is"
    " supported, as is any character set that is also valid utf-8. Please"
    " edit/remove this lookup."
)

VALID_MESSAGE = "File is valid."


class LookupHelper(object):
    """Helper class for Splunk lookups.

    Standards for lookups are defined for Splunk Cloud, so using those since no other standards seem to exist:
    https://docs.splunk.com/Documentation/Splunk/7.2.4/Knowledge/Usefieldlookupstoaddinformationtoyourevents

    There are a few restrictions to the kinds of CSV files that can be used for CSV lookups:

     - The table represented by the CSV file should have at least two columns. One of those columns should represent a field with a set of values that includes those belonging to a field in your events. The column does not have to have the same name as the event field. Any column can have multiple instances of the same value, as this represents a multivalued field.
     - The CSV file cannot contain non-utf-8 characters. Plain ascii text is supported, as is any character set that is also valid utf-8.
     - The following are unsupported:
       - CSV files with pre-OS X (OS 9 or earlier) Macintosh-style line endings (carriage return ("\r") only)
       - CSV files with header rows that exceed 4096 characters.
    """

    @staticmethod
    def is_valid_csv(full_filepath):
        """Valid whether file is valid csv according to http://docs.splunk.com/Documentation/SplunkCloud/6.6.0/Knowledge/ConfigureCSVlookups
        and additional constaints - should have at least one row and number of
        columns must match for all rows

        Args:
            full_filepath (str): Local system filepath to lookup to be examined

        Returns:
            (bool) is_valid, (str) rationale
        """
        return_msg = VALID_MESSAGE
        with open(full_filepath, "rb") as csvfile:
            file_contents = csvfile.read().strip()
            if not file_contents:
                # empty file
                return False, LOOKUP_EMPTY_MESSAGE
            # if "\r" in file_contents and "\r\n" not in file_contents:
            #     return False, LOOKUP_MAC_LINE_ENDINGS_MESSAGE

            for i, _ in enumerate(file_contents):
                if (
                    file_contents[i : i + 1] == b"\r"
                    and i < len(file_contents) - 1
                    and file_contents[i + 1 : i + 2] != b"\n"
                    or file_contents[i : i + 1] == b"\r"
                    and i == len(file_contents) - 1
                ):
                    return_msg = LOOKUP_MAC_LINE_ENDINGS_MESSAGE

            try:
                file_contents.decode("utf8")
            except UnicodeDecodeError:
                return False, LOOKUP_NON_UTF8_MESSAGE
            csvfile.seek(0)  # point back to beginning of file

        if sys.version_info.major == 2:
            csvfile = open(full_filepath, "rU")
        elif sys.version_info.major == 3:
            csvfile = open(full_filepath, "r")
        else:
            raise ValueError("unexpected python version")

        try:
            lookup_header = csvfile.readline()
            if len(lookup_header) > LOOKUP_HEADER_CHAR_LIMIT:
                return False, LOOKUP_HEADER_CHAR_LIMIT_MESSAGE

            csvfile.seek(0)  # point back to beginning of file
            try:
                dialect = csv.Sniffer().sniff(lookup_header, [",", "\t", ";", " ", ":"])
                # https://www.reddit.com/r/learnpython/comments/2ivjju/read_csv_file_with_escaped_quotes/
                dialect.doublequote = True
            except csv.Error as e:
                if "Could not determine delimiter" in str(e):
                    dialect = None

            csv_data = list(csv.reader(csvfile, dialect=dialect))
            if not csv_data:
                return False, LOOKUP_EMPTY_MESSAGE
            header_columns = len(csv_data[0])
            # If each row of file has same number of columns, call it a valid
            # csv - some level of checking is needed as csv.reader() will
            # process just about anything without issue
            for row in range(1, len(csv_data)):
                row_columns = len(csv_data[row])
                if csv_data[row] and row_columns != header_columns:
                    return (
                        False,
                        LOOKUP_COLUMN_MISMATCH_MESSAGE.format(
                            row=row + 1,
                            row_column=row_columns,
                            header_column=header_columns,
                        ),
                    )
        except Exception:
            raise
        finally:
            csvfile.close()

        return True, return_msg

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import logging
import glob
from silx.io.url import DataUrl
from tomwer.core.process.reconstruction.nabu.castvolume import cast_volumes


_logger = logging.getLogger(__name__)


def extract_urls(file_patterns, input_data_path) -> tuple:
    res = []
    for file_pattern in file_patterns:
        print("look for file_pattern", {file_pattern})
        for file_ in glob.glob(file_pattern):
            print("file_", file_)
            if file_.lower().endswith((".tiff", ".tif")):
                res.append(DataUrl(file_path=file_, scheme="fabio"))
            else:
                _logger.warning(f"Unable to handle {file_}. Skip it")
    return tuple(res)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        help="Files or data url to be cast",
        nargs="+",
    )
    parser.add_argument(
        "--input-data-path",
        help="Optional input data path for hdf5 files",
        default=None,
    )
    parser.add_argument(
        "--output-data-type",
        help="data type to create",
        default="uint 16",
    )
    parser.add_argument(
        "--output-file-format",
        help="Output file format",
        default="tiff",
    )
    parser.add_argument(
        "output_file_path",
        help="file path or folder path to save the volume.",
    )
    # for now we only handle tiff as output
    # parser.add_argument(
    #     "--output-data-path",
    #     help="for hdf5 files you can provide a data path. Otherwise will store volume at the root level under volume",
    #     default="/volume",
    # )
    parser.add_argument(
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrite file or dataset if exists",
    )

    options = parser.parse_args(argv[1:])
    volume_urls = extract_urls(
        file_patterns=options.files, input_data_path=options.input_data_path
    )
    if len(volume_urls) == 0:
        _logger.warning("No input found")
        return

    cast_volumes(
        input_volume_urls=volume_urls,
        output_data_type=options.output_data_type,
        output_file_format=options.output_file_format,
        output_file_path=options.output_file_path,
        overwrite=options.overwrite,
    )


if __name__ == "__main__":
    main(sys.argv)

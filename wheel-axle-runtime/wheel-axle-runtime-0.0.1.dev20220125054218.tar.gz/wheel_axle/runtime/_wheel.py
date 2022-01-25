# -*- coding: utf-8 -*-
#
# (C) Copyright 2021 Karellen, Inc. (https://www.karellen.co/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import csv
import os
from distutils.errors import DistutilsPlatformError
from email.message import Message
from email.parser import Parser
from os.path import dirname, join as jp
from typing import Tuple, Dict, Set, List, cast, IO

from pip._internal.exceptions import UnsupportedWheel
from pip._internal.locations import get_scheme
from pip._internal.models.scheme import Scheme
from pip._internal.operations.install.wheel import get_csv_rows_for_installed, csv_io_kwargs, _normalized_outrows
from pip._internal.req.req_install import _get_dist
from pip._vendor.pkg_resources import Distribution

__all__ = ["get_current_scheme", "get_dist_meta", "wheel_root_is_purelib"]

IO = IO


def get_current_scheme(dist_info_dir, dist_name, wheel_meta):
    install_dir = dirname(dist_info_dir)

    scheme = get_scheme(dist_name)

    def check_correct_scheme(scheme, install_dir):
        if wheel_root_is_purelib(wheel_meta):
            scheme_dir = scheme.purelib
        else:
            scheme_dir = scheme.platlib

        if os.path.samefile(install_dir, scheme_dir):
            return True

        return False

    if not check_correct_scheme(scheme, install_dir):
        try:
            scheme = get_scheme(dist_name, True)
        except DistutilsPlatformError:
            raise RuntimeError("unable to determine current installation scheme")

        if not check_correct_scheme(scheme, install_dir):
            raise RuntimeError("unable to determine current installation scheme")

    return scheme


def wheel_root_is_purelib(wheel_meta: Message) -> bool:
    return wheel_meta.get("Root-Is-Purelib", "").lower() == "true"


def get_dist_meta(dist_info_dir: str) -> Tuple[Distribution, Message]:
    return _get_dist(dist_info_dir), wheel_metadata(dist_info_dir)


def wheel_metadata(dist_info_dir) -> Message:
    """Return the WHEEL metadata of an extracted wheel, if possible.
    Otherwise, raise UnsupportedWheel.
    """
    path = jp(dist_info_dir, "WHEEL")
    with open(path, "rb") as f:
        wheel_contents = f.read()

    try:
        wheel_text = wheel_contents.decode()
    except UnicodeDecodeError as e:
        raise UnsupportedWheel(f"error decoding {path!r}: {e!r}")

    # FeedParser (used by Parser) does not raise any exceptions. The returned
    # message may have .defects populated, but for backwards-compatibility we
    # currently ignore them.
    return Parser().parsestr(wheel_text)


def update_record(dist_info_dir: str,
                  dist_meta: Distribution,
                  wheel_meta: Message,
                  scheme: Scheme,
                  lib_dir: str,
                  installed: Dict[str, str],
                  changed: Set[str],
                  generated: List[str]):
    record_text = dist_meta.get_metadata_lines("RECORD")
    record_rows = list(csv.reader(record_text))

    rows = get_csv_rows_for_installed(
        record_rows,
        installed=installed,
        changed=changed,
        generated=generated,
        lib_dir=lib_dir,
    )

    # Record details of all files installed
    record_path = os.path.join(dist_info_dir, "RECORD")

    with open(record_path, **csv_io_kwargs("w")) as record_file:
        # Explicitly cast to typing.IO[str] as a workaround for the mypy error:
        # "writer" has incompatible type "BinaryIO"; expected "_Writer"
        writer = csv.writer(cast("IO[str]", record_file))
        writer.writerows(_normalized_outrows(rows))

# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import magic  # type: ignore
import os
import typing
import xml.etree.ElementTree as ET
import zipfile


def is_zip(file_handle: typing.BinaryIO) -> bool:
    file_handle.seek(0, os.SEEK_SET)
    header = file_handle.read(4)

    if header == b"PK\x03\x04":
        return True
    return False


def get_mime_type_from_content(file_handle: typing.BinaryIO) -> str:
    file_handle.seek(0, os.SEEK_SET)

    # This is needed to resolve an issue with the file handle
    # pointer not being reset despite the seek call
    file_content = file_handle.read(1024 * 1024)
    mime_type = magic.detect_from_content(file_content).mime_type

    return mime_type


def get_mime_type_from_handle(file_handle: typing.BinaryIO) -> str:
    recognized_office_formats = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }

    mime_type = "application/octet-stream"
    try:
        if is_zip(file_handle):
            zip_handle = zipfile.ZipFile(file_handle)
            xml_content = zip_handle.read("[Content_Types].xml")
            namespaces = {
                "ct": "http://schemas.openxmlformats.org/package/2006/content-types"
            }
            root = ET.fromstring(xml_content)
            content_types = [
                itm.attrib["ContentType"]
                for itm in root.findall("ct:Override", namespaces)
            ]

            for content_type in content_types:
                if content_type in recognized_office_formats:
                    mime_type = recognized_office_formats[content_type]
                    break
        else:
            file_handle.seek(0, os.SEEK_SET)
            mime_type = get_mime_type_from_content(file_handle)
    except:  # noqa (most likely: Corrupt zip file)
        file_handle.seek(0, os.SEEK_SET)
        mime_type = get_mime_type_from_content(file_handle)

    file_handle.seek(0, os.SEEK_SET)
    return mime_type

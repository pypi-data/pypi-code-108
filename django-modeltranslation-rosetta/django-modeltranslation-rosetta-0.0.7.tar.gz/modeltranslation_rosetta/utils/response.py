# coding: utf-8
from __future__ import unicode_literals

from django.http import HttpResponse
from django.utils.encoding import smart_str, smart_bytes


class FileResponse(HttpResponse):
    """
    DRF Response to render data as a PDF File.
    kwargs:
        - pdf (byte array). The PDF file content.
        - file_name (string). The default downloaded file name.
    """

    def __init__(
        self, file_content, file_name, download=True, content_type=None, *args, **kwargs
    ):
        disposition = 'filename="{}"'.format(smart_str(file_name))
        if download:
            disposition = "attachment; " + disposition

        headers = {
            "Content-Disposition": smart_bytes(disposition),
            "Content-Length": len(file_content),
        }

        super(FileResponse, self).__init__(
            file_content,
            content_type=content_type or "application/octet-stream",
            *args,
            **kwargs
        )

        for h, v in headers.items():
            self[h] = v

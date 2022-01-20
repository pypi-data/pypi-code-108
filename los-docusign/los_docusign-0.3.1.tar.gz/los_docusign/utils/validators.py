#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
import os

from django.core.exceptions import ValidationError


def validate_excel_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [".xls", ".xlsx", ".csv"]
    if not ext.lower() in valid_extensions:
        raise ValidationError(u"Unsupported file extension. Must be Excel File")


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [
        ".pdf",
        ".xls",
        ".xlsx",
        ".csv",
        ".doc",
        ".docx",
        ".jpg",
        ".jpeg",
        ".png",
    ]
    if not ext.lower() in valid_extensions:
        raise ValidationError(u"Unsupported file extension.")

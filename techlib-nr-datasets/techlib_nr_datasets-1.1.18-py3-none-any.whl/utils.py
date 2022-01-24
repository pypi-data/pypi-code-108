# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Dataset records celery tasks."""

from datetime import datetime

from flask import current_app
from edtf.parser import parse_edtf
from edtf.parser.edtf_exceptions import EDTFParseException


def access_rights_factory(slug):
    return f"https://{current_app.config['SERVER_NAME']}/2.0/taxonomies/accessRights/{slug}"


def edtf_to_date(edtf_string):
    ed = parse_edtf(edtf_string)
    return datetime(int(ed.year), int(ed.month), int(ed.day))

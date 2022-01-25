# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Dataset records celery tasks."""
from datetime import datetime

from edtf.parser.edtf_exceptions import EDTFParseException
from flask import current_app
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_rest.utils import obj_or_import_string
from oarepo_communities.constants import STATE_PUBLISHED
from sqlalchemy.orm.exc import NoResultFound

from nr_datasets.constants import embargoed_slug, open_access_slug, restricted_slug
from nr_datasets.utils import access_rights_factory, edtf_to_date


def _set_published_rights(record):
    try:
        date_available = edtf_to_date(record.get('dateAvailable'))
    except EDTFParseException:
        print(f"Record: {record['InvenioID']} has invalid/missing `dateAvailable`! Skipping...")
        raise
    if datetime.today() >= date_available:
        print(f"Fixing rights on : {record['InvenioID']}. Should be open-access.")
        record['accessRights'] = access_rights_factory(open_access_slug)
    else:
        print(f"Fixing rights on : {record['InvenioID']}. Should be embargoed.")
        record['accessRights'] = access_rights_factory(embargoed_slug)

    return record


def update_access_rights(deep=False):
    endpoints = current_app.config.get("RECORDS_REST_ENDPOINTS").endpoints
    for config in endpoints.values():
        try:
            pid_type: str = config["pid_type"]
            print(f'PID type: {pid_type}')
            record_class = obj_or_import_string(config["record_class"])
            pids = PersistentIdentifier.query.filter_by(pid_type=pid_type).all()
            for i, pid in enumerate(pids):
                try:
                    record = record_class.get_record(pid.object_uuid)
                except NoResultFound:
                    continue

                ar = record.get('accessRights')
                if ar and len(ar) == 1:
                    link = ar[0].get('links', {}).get('self')
                    slug = link.split('/')[-1]
                    if slug == embargoed_slug:
                        date_embargo = edtf_to_date(record.get('dateAvailable'))

                        if datetime.today() >= date_embargo:
                            print(f"Embargo expired. Setting OpenAccess rights on record: {record['InvenioID']}")
                            record['accessRights'] = access_rights_factory(open_access_slug)
                    elif slug == restricted_slug and deep:
                        # Fix access on restricted records that should be either embargoed or open
                        state = record._deep_get_state(record)
                        if state == STATE_PUBLISHED:
                            try:
                                _set_published_rights(record)
                            except EDTFParseException:
                                continue
                elif deep:
                    # Fix access on records with missing access rights
                    state = record._deep_get_state(record)
                    if state == STATE_PUBLISHED:
                        try:
                            _set_published_rights(record)
                        except EDTFParseException:
                            continue
                    else:
                        record['accessRights'] = access_rights_factory(restricted_slug)

                record.commit()
        finally:
            db.session.commit()

# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_args 1'] = [
    (
        'trace_func',
        (
            GenericRepr('sentinel.frame'),
            'call',
            None
        ),
        {
        }
    ),
    (
        'trace_func',
        (
            GenericRepr('sentinel.frame'),
            'line',
            None
        ),
        {
        }
    )
]

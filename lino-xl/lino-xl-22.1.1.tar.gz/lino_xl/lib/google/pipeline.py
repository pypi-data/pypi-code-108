# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime

def intercept_extra_data(backend, user, response, *args, **kwargs):
    return kwargs

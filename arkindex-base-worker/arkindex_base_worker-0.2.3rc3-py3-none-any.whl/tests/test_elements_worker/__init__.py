# -*- coding: utf-8 -*-
# API calls during worker configuration
BASE_API_CALLS = [
    ("GET", "http://testserver/api/v1/user/"),
    ("GET", "http://testserver/api/v1/imports/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff/"),
    (
        "GET",
        "http://testserver/api/v1/workers/versions/12341234-1234-1234-1234-123412341234/",
    ),
]

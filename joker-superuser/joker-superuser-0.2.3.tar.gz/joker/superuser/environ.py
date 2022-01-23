#!/usr/bin/env python3
# coding: utf-8

import joker.environ


class GlobalInterface(joker.environ.GlobalInterface):
    package_name = 'joker.superuser'

    default_config = {
        "urls": {
            "youtube.com/watch": ["v"],
            "youtube.com/playlist": ["list"],
        }
    }


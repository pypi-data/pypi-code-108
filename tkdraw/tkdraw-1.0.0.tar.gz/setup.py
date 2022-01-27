#!/usr/bin/env python3
import sys
import site
import setuptools

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]
setuptools.setup()

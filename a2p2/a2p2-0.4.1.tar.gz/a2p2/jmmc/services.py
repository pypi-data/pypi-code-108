#!/usr/bin/env python

__all__ = []

import logging

from .catalogs import Catalog
from .webservices import CallIper

logger = logging.getLogger(__name__)

#  TODO list and give access to whole services and their beta/alpha / pre-prod instances if existing

oidb_catalog = Catalog("oidb")

calliper = CallIper()

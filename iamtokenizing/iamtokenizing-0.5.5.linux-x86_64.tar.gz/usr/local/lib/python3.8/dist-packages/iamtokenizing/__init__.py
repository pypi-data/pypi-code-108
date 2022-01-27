#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pkg_resources import get_distribution
__version__ = get_distribution("iamtokenizing").version

from .ngrams import NGrams
from .chargrams import CharGrams
from .regex_detector import RegexDetector
from .context_detector import ContextDetector



# -*- coding: utf-8 -*-
"""This module contains the exceptions used in the iTunes Store API wrapper
"""

__all__ = ['ITunesException', 'NoResultsFoundException']

class ITunesException(Exception):
    """Base iTunes request exception"""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return '{type}: {msg}'.format(type=self.__class__.__name__,
                                      msg=self.message)


class NoResultsFoundException(ITunesException):
    """iTunes error for when no results are returned from a Lookup"""
    def __init__(self):
        super(self.__class__, self).__init__('No Results Found')
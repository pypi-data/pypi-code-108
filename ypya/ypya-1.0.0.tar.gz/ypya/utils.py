'''
ypya.utils
'''
from logging import Filter
from logging.handlers import SocketHandler


from .base import YBase


class YExclusion(Filter):
    NS_SEP = '.'


class YLogHandler(YBase, SocketHandler):
    '''
    A simple logging handler
    '''

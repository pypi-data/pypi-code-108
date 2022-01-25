'''Utilities for working with task output.
'''

from dataclasses import dataclass

from .__init__ import timestamp


@dataclass
class OutputText:
    '''Stores content of a single output operation with timestamp.
    '''
    text: str
    '''Output text content.'''
    timestamp: str
    '''Output timestamp. Defined automatically when instance is created.'''
    stream: str
    '''Output stream. For example `stdout`.'''

    def __init__(self, text: str, stream: str = 'stdout'):
        '''
        Args:
            text: Output text content.
            stream: Output stream. Defaults to `stdout`.
        '''
        self.text = text
        self.stream = stream
        self.timestamp = timestamp()

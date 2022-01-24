import warnings
import cerberus_kind
import json
import inspect
from pprint import pprint
warnings.simplefilter("ignore", UserWarning)
        
class Validator(cerberus_kind.Validator):
    def _validate_description(self, constraint, field, value):
        '''For use YAML Editor'''

    def _validate_multiline(self, constraint, field, value):
        '''For use YAML Editor'''

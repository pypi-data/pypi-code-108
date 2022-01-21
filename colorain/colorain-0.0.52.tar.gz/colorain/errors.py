##################################################
# Error handling #
##################################################
class InvalidPropError(Exception):
    def __init__(self, msg, prop):
        self.prop = prop

    def __str__(self):
        return f'The prop {self.prop} does not exist.'

class InvalidValueError(Exception):
    def __init__(self, prop, val):
        self.prop = prop
        self.val = val
    
    def __str__(self):
        return f'The value {self.val} is invalid for prop {self.prop}.'

class MissingValueError(Exception):
    def __init__(self, prop):
        self.prop = prop
    
    def __str__(self):
        return f'The value for the prop {self.prop} is unspecified.'

class TokenSyntaxError(Exception):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return f'Invalid syntax for token {self.token}.'

class EmptyTokenError(Exception):
    def __init__(self):
        super().__init__("The start token is empty")

class MissingEndTagError(Exception):
    def __init__(self):
        super().__init__("The input doesn't have an end tag.")

class InvalidInputError(Exception):
    def __init__(self, inp_type):
        self.inp_type = inp_type
    
    def __str__(self):
        return f"The input is of unsupported datatype: {self.inp_type}"
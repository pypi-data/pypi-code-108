'''
Calculate the limit up and limit down price of a ticker in TW stock market
'''
import math
import sys
from . import config

def base_floor(number, base):
    '''
    Apply math.floor() based on the value of "base".
    The return value must be a multiple of "number".
    '''
    return base * math.floor(number/base)

def base_ceil(number, base):
    '''
    Apply math.ceil() based on the value of "base".
    The return value must be a multiple of "number".
    '''
    return base * math.ceil(number/base)

def get_base(number):
    '''
    Determine the base of the input number
    '''
    for price_step in config.price_base_map:
        if price_step['price'] > number:
            return price_step['base']
    raise Exception(f'No stock price should be greater than {sys.maxsize}!')

def get_limit_up_price(price):
    '''
    Calculate the limit up price of a ticker in TW stock market
    '''
    if math.isnan(price):
        return price
    limit_up_raw_value = price * ( 1 + config.limit_up_percent/100)
    base = get_base(limit_up_raw_value)
    return round(base_floor(limit_up_raw_value, base), 2)

def get_limit_down_price(price):
    '''
    Calculate the limit down price of a ticker in TW stock market
    '''
    if math.isnan(price):
        return price
    limit_up_raw_value = price * ( 1 + config.limit_down_percent/100)
    base = get_base(limit_up_raw_value)
    return round(base_ceil(limit_up_raw_value, base), 2)

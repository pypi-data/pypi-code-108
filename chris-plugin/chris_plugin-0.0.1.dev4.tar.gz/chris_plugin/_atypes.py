"""
A hack to extract private types out from :mod:`argparse`
"""
import argparse

__parser = argparse.ArgumentParser()
__store = __parser.add_argument('-a', action='store')
__store_const = __parser.add_argument('-b', action='store_const', const='b')
__store_true = __parser.add_argument('-c', action='store_true')
__store_false = __parser.add_argument('-d', action='store_false')

StoreAction = type(__store)
StoreConstAction = type(__store_const)
StoreTrueAction = type(__store_true)
StoreFalseAction = type(__store_false)

del __parser
del __store
del __store_const
del __store_true
del __store_false

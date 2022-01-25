"""
Authors: Peter Mawhorter
Consulted:
Date: 2022-1-23
Purpose: Tests for basic functions using optimism
"""

import math

import functions

import optimism as opt

# indentMessage tests
m = opt.testFunction(functions.indentMessage)
m.case('hi', 4).checkResult('  hi')
m.case('hello', 4).checkResult('hello')


# printMessage tests
m = opt.testFunction(functions.printMessage)
m.case('hi', 4).checkOutputLines('  hi')
m.case('hello', 4).checkOutputLines('hello')


# ellipseArea tests
m = opt.testFunction(functions.ellipseArea)
m.case(1, 1).checkResult(math.pi)
m.case(2, 3).checkResult(6 * math.pi)


# No way to define test cases for polygon...

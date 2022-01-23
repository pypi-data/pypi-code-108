"""
Authors: Peter Mawhorter
Consulted:
Date: 2022-1-23
Purpose: Tests for basic functions using optimism (alternate)
"""

import math

import functions

import optimism as opt

# indentMessage tests
m = opt.testFunction(functions.indentMessage)
m.case('hello', 8).checkResult('   hello')
m.case('hi', 1).checkResult('hi')
m.case('hi', 3).checkResult(' hi')


# printMessage tests
m = opt.testFunction(functions.printMessage)
m.case('hello', 8).checkOutputLines('   hello')
m.case('hi', 1).checkOutputLines('hi')
m.case('has\nnewline', 3).checkOutputLines('has', 'newline')
m.case('has\nnewline', 14).checkOutputLines('   has', 'newline')


# ellipseArea tests
m = opt.testFunction(functions.ellipseArea)
m.case(1, 1).checkResult(math.pi)
m.case(3, 2).checkResult(6 * math.pi)
m.case(0.4, 0.5).checkResult(0.2 * math.pi)


# No way to define test cases for polygon...

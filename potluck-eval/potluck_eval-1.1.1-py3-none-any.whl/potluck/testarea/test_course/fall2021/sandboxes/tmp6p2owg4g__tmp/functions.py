"""
functions.py

Your name: Peter Mawhorter
Your username: pmwh
Submission date: 2021-6-22

A few functions to practice with.
"""

import optimism as opt


def indentMessage(message, targetLength):
    """
    Returns a string that's at least the given target length. If given a
    longer string, it returns it as-is, but if given a shorter string, it
    adds spaces to the front of the string to make it the required
    length.
    """
    indent = max(0, targetLength - len(message))
    return ' ' * indent + message


opt.expect(indentMessage('hi', 4), '  hi')
opt.expect(indentMessage('hello', 4), 'hello')


def printMessage(message, width):
    """
    Prints a message, taking up at least the required width (will be
    wider if the message itself is wider). Uses indentMessage.
    """
    print(indentMessage(message, width))


m = opt.testFunction(printMessage)
m.case('hi', 4).checkOutputLines('  hi')
m.case('hello', 4).checkOutputLines('hello')


import math # noqa


def ellipseArea(radius1, radius2):
    """
    Computes the area of an ellipse with the given radii (you may specify
    the major and minor radii in either order). Returns the result as a
    floating-point number.
    """
    return radius1 * radius2 * math.pi


m = opt.testFunction(ellipseArea)
c = m.case(1, 1).checkResult(math.pi)
c = m.case(2, 3).checkResult(6 * math.pi)


from turtle import * # noqa


def polygon(sideLength, nSides):
    """
    Draws a polygon with the given side length and number of sides.
    """
    for _ in range(nSides):
        fd(sideLength) # noqa
        lt(360 / nSides) # noqa

"""
turtleBeads.py

Turtle graphics library for drawing various shapes centered on the
cursor.

In general, these functions draw things centered at the cursor, and put
the cursor back where it started afterwards. Set the pensize and pencolor
before drawing a shape to control what is drawn. For most shapes you can
also use fillcolor and begin_fill/end_fill to fill in the shape.
"""

__version__ = "0.7.6"

import math
import random

from turtle import *

# Setup function
#---------------

def setupTurtle():
    """
    Sets up the turtle window using default size, speed, pen size, and
    pen/fill colors.
    """
    try:
        setup()
    except Exception:
        pass
    setup()
    reset()
    pensize(1.5)
    color("black", "black")
    # TODO: Move turtle window to front


# Print control
#--------------

PRINT_RESULTS = True
"""
Whether or not to print each time we draw something. Includes printing
for built-in turtle functions forward, back, circle, and begin/end_fill.
"""

PRINT_LINES = True
"""
Global to enable/disable printing for the forward and backward commands
(and their aliases). Useful because turtleBeads wants to use those
commands as part of larger shapes but print a higher-level summary of the
larger shape instead.
"""

CURRENT_DESCRIPTION = None
"""
A custom description of what is currently being drawn.
"""

def describeAngle(angle, normalize=360):
    """
    Converts an angle (in floating-point degrees) to a string description
    of that angle. The second argument (default 360) should be either
    a number or None, and controls normalization. When it's exactly the
    integer 180 (not 180.0), angles 0, and 180 will be described as
    "horizontal" and angles 90 and 270 will be described as "vertical".
    When it's exactly the integer 360, angles 0, 90, 180, and 270 will be
    described using the cardinal directions (according to the default
    right-handed coordinate system). If normalize is None, then no
    normalization is performed, and, for example, negative angles will
    remain negative. The angle will always be rounded to the nearest
    tenth of a degree.
    """
    if type(normalize) == int and normalize == 180:
        norm = ((round(angle, 1) % 180) + 180) % 180
        if norm == 0.0:
            return "horizontal"
        elif norm == 90.0:
            return "vertical"
        # otherwise fall out
    elif type(normalize) == int and normalize == 360:
        norm = ((round(angle, 1) % 360) + 360) % 360
        if norm == 0.0:
            return "East"
        elif norm == 90.0:
            return "North"
        elif norm == 180.0:
            return "West"
        elif norm == 270.0:
            return "South"
        # otherwise fall out
    elif normalize != None:
        norm = ((round(angle, 1) % normalize) + normalize) % normalize
    else:
        norm = round(angle, 1)

    return withTenths(norm) + '°'


def describeColor(color):
    """
    Describes a color.
    """
    if isinstance(color, (list, tuple)):
        return "RGB" + repr(color)
    else:
        return color


def withTenths(val):
    """
    Returns a string containing the given floating-point value rounded to
    the tenths place, with the decimal and zero dropped if it's an even
    number.
    """
    result = "{:.1f}".format(val)
    if result[-1] == '0':
        result = result[:-2]
    return result


def describePen(pensize, pencolor):
    """
    Returns a string describing the pen format for the given size &
    color.
    """
    return "{}-pensize {}".format(withTenths(pensize), describeColor(pencolor))


def decorateBuiltins():
    """
    Handles the decoration of built-in turtle functions so that they
    print a report when called.
    """
    global fd, forward, bk, back, backward, circle, begin_fill, end_fill,\
           write
    import turtle # so we can wrap in case of a subsequent import
    # (there's nothing we can do about prior import *s)
    def wrapLineFcn(basefcn):
        """
        Wrapper for line functions (fd/bk/etc.) that announces the line
        drawn.
        """
        def wrapped(*args, **kwargs):
            """ PLACEHOLDER """
            if (
                PRINT_RESULTS
            and CURRENT_DESCRIPTION is None
            and PRINT_LINES
            and isdown()
            ):
                # Preliminary info
                wasAt = position()
                angle = describeAngle(heading(), normalize=180)
                fmt = describePen(pensize(), pencolor())

                # Call the wrapped function
                basefcn(*args, **kwargs)

                # Gather final info
                nowAt = position()

                print(
                    "A {} {} line from ({}, {}) to ({}, {}).".format(
                        fmt,
                        angle,
                        round(wasAt[0]),
                        round(wasAt[1]),
                        round(nowAt[0]),
                        round(nowAt[1])
                    )
                )
            else:
                basefcn(*args, **kwargs)

        wrapped.__name__ = basefcn.__name__
        wrapped.__doc__ = basefcn.__doc__ + """

    This version also prints a description of the line it draws if the
    pen is down.
"""
        return wrapped

    # Wrap forward & backward functions
    for lf in (fd, forward, bk, back, backward):
        lf = wrapLineFcn(lf)
        setattr(turtle, lf.__name__, wrapLineFcn(getattr(turtle, lf.__name__)))
        globals()[lf.__name__] = lf

    orig_circle = circle
    def loudCircle(radius, degrees=360):
        """ PLACEHOLDER """
        global PRINT_LINES
        if PRINT_RESULTS and CURRENT_DESCRIPTION is None and isdown():
            # Collect preliminary info
            wasAt = position()
            wasFacing = heading()
            fmt = describePen(pensize(), pencolor())

            # Draw the circle (w/out reporting lines)
            wasPrintingLines = PRINT_LINES
            PRINT_LINES = False
            orig_circle(radius, degrees)
            PRINT_LINES = wasPrintingLines

            # Collect final info
            nowAt = position()
            nowFacing = heading()

            # Compute center
            center = (
                wasAt[0] + math.cos(math.radians(wasFacing + 90)) * radius,
                wasAt[1] + math.sin(math.radians(wasFacing + 90)) * radius
            )

            if degrees >= 360:
                print(
                    (
                        "A {} circle centered at ({}, {}) with radius"
                      + " {}."
                    ).format(
                        fmt,
                        round(center[0]),
                        round(center[1]),
                        withTenths(radius)
                    )
                )
            else:
                print(
                    "A {} arc from ({}, {}) facing {} to ({}, {}) facing {}."
                    .format(
                        fmt,
                        round(wasAt[0]),
                        round(wasAt[1]),
                        describeAngle(wasFacing),
                        round(nowAt[0]),
                        round(nowAt[1]),
                        describeAngle(nowFacing)
                    )
                )
        else:
            orig_circle(radius, degrees)

    loudCircle.__name__ = circle.__name__
    loudCircle.__doc__ = circle.__doc__ + """

    This version also prints a description of the circle or arc it
    draws if the pen is down.
"""

    circle = loudCircle
    turtle.circle = loudCircle

    orig_bf = begin_fill
    def loudBeginFill():
        """ PLACEHOLDER """
        orig_bf()
        if PRINT_RESULTS and CURRENT_DESCRIPTION is None:
            print("Start of filled shape.")

    orig_ef = end_fill
    def loudEndFill():
        """ PLACEHOLDER """
        color = fillcolor()
        orig_ef()
        if PRINT_RESULTS and CURRENT_DESCRIPTION is None:
            print("Filled in shape using {}.".format(color))

    loudBeginFill.__name__ = begin_fill.__name__
    loudBeginFill.__doc__ = begin_fill.__doc__ + """

    This version also announces that filling has begun.
"""
    loudEndFill.__name__ = end_fill.__name__
    loudEndFill.__doc__ = begin_fill.__doc__ + """

    This version also announces that filling has ended, along with the
    current fill color.
"""

    begin_fill = loudBeginFill
    turtle.begin_fill = loudBeginFill

    end_fill = loudEndFill
    turtle.end_fill = loudEndFill

    orig_write = write
    def loudWrite(text, move=False, align="left", font=("Arial", 8, "normal")):
        """ PLACEHOLDER """
        if PRINT_RESULTS and CURRENT_DESCRIPTION is None:
            # Collect preliminary info
            wasAt = position()
            angle = describeAngle(heading())
            fmt = "{}pt {}{}".format(
                font[1],
                font[0],
                ' ' + font[2] if font[2] != "normal" else ''
            )

            # Draw the text
            orig_write(text, move=move, align=align, font=font)

            # Print a message
            print(
                "The text '{}' in {} font{}".format(
                    text,
                    fmt,
                    (
                        ''
                        if angle == "East"
                        else (
                            " running " + angle
                            if angle in ("North", "West", "South")
                            else (
                                " tilted at " + angle
                            )
                        )
                    )
                )
            )
        else:
            write(text, move=move, align=align, font=font)

    loudWrite.__name__ = write.__name__
    loudWrite.__doc__ = write.__doc__ + """

    This version also announces the text that is drawn.
"""
    write = loudWrite
    turtle.write = loudWrite


def beSilent():
    """
    Disables printed output of turtle drawing. Re-enable it with
    `beLoud`.
    """
    global PRINT_RESULTS
    PRINT_RESULTS = False


def beLoud():
    """
    Re-enables printed output of turtle drawing if it's been turned off
    using `beSilent`.
    """
    global PRINT_RESULTS
    PRINT_RESULTS = True


def describeAs(description):
    """
    Sets the given description and turns announcements off until
    `endDescription` or `beLoud` is called. Calling `endDescription` will
    print the provided description. Calling `describeAs` again will
    print the current description if there is one before setting a new
    description.

    While a custom description is active, default description messages
    will not be printed.
    """
    global CURRENT_DESCRIPTION
    if PRINT_RESULTS and CURRENT_DESCRIPTION != None:
        print(CURRENT_DESCRIPTION)
    CURRENT_DESCRIPTION = description


def endDescription():
    """
    Prints out the current description if there is one, and sets it to
    None, so that default descriptions will be produced.
    """
    global CURRENT_DESCRIPTION
    if PRINT_RESULTS and CURRENT_DESCRIPTION != None:
        print(CURRENT_DESCRIPTION)
    CURRENT_DESCRIPTION = None


def quietLines():
    """
    Disables printed output for forward/back commands and their aliases.
    Re-enable with `loudLines`.
    """
    global PRINT_LINES
    PRINT_LINES = False


def loudLines():
    """
    Re-enables printed output for forward/back commands if it was
    disabled with `quietLines`.
    """
    global PRINT_LINES
    PRINT_LINES = True


# Apply decorations even on import
decorateBuiltins()


# Trace control
#--------------

def noTrace():
    """
    Disables turtle tracing, so that drawing will be near-instant (much
    faster than even speed 0). However, nothing will be displayed until
    you call showPicture.
    """
    tracer(0, 0)


def doTrace():
    """
    Re-enables tracing, so that the turtle will move along the path that
    it draws and you can see each line being drawn. This function first
    updates the picture to display any lines drawn since tracing was
    disabled (if it had been).
    """
    update()
    # TODO: What args here?
    tracer(1, 1)


def showPicture():
    """
    Shows any lines drawn so far. Required when noTrace has been called
    to disable real-time drawing.
    """
    update()


# Movement shortcuts
#-------------------

def realign():
    """
    Sets the turtle's heading back to the default (0 degrees = facing
    right).
    """
    setheading(0)


def teleport(x, y):
    """
    Penup + goto + pendown.
    """
    downNow = isdown()
    penup()
    goto(x, y)
    if downNow:
        pendown()


def leap(dist):
    """
    Penup + fd + pendown. You can use a negative number to go backwards.
    """
    downNow = isdown()
    penup()
    fd(dist)
    if downNow:
        pendown()

def hop(dist):
    """
    Lifts the pen and moves the given distance to the left of the current
    turtle position without changing the orientation of the turtle (hops
    sideways). Use a negative number to hop to the right. Puts the pen
    back down when it's done if the pen was down beforehand.
    """
    downNow = isdown()
    penup()
    lt(90)
    fd(dist)
    rt(90)
    if downNow:
        pendown()


# Drawing parameters
#-------------------

BASE_CURVE_STEPS = 32  # Default number of sides of a circle
MAX_CURVE_STEPS = 128  # Maximum number of sides for a circle
TARGET_SEGMENT_LENGTH = 3  # Ideal length for each side of a circle

# "Beads" functions
#------------------

def drawCircle(radius):
    """
    Draws a circle centered at the given position with the given radius,
    and puts the turtle back where it started when it's done.

    Actually, it draws a many-sided polygon, but the difference should
    usually be hard to see.
    """
    downNow = isdown()

    # Start a description if there isn't a custom description active
    describing = False
    if CURRENT_DESCRIPTION is None and downNow:
        describing = True
        x, y = position()
        fmt = describePen(pensize(), pencolor())
        describeAs(
            "A {} circle centered at ({}, {}) with radius {}".format(
                fmt,
                round(x),
                round(y),
                withTenths(radius)
            )
        )

    steps = BASE_CURVE_STEPS
    segmentLength = (2 * math.pi * radius) / steps
    while segmentLength > TARGET_SEGMENT_LENGTH and steps < MAX_CURVE_STEPS:
        steps += 1
        segmentLength = (2 * math.pi * radius) / steps
    start = pos()
    starth = heading()
    penup()
    lt(90)
    fd(radius)
    rt(90)
    if downNow:
        pendown()
    fd(segmentLength / 2)
    rt(360 / steps)
    for i in range(steps - 1):
        fd(segmentLength)
        rt(360 / steps)
    penup()
    fd(segmentLength / 2)
    goto(start[0], start[1])
    seth(starth)
    if downNow:
        pendown()

    if describing:
        endDescription()


def ellipsePointAt(major, minor, angle):
    """
    Takes an angle in degrees and computes the ellipse point for that many
    degrees clockwise from the top of the ellipse where the given minor
    radius is vertical and the given major radius is horizontal. Uses the
    trammel drawing method from:

    https://www.joshuanava.biz/engineering-3/methods-of-drawing-an-ellipse.html

    The angle specified is interpreted as the trammel angle, not an angle
    of a ray from the center of the ellipse through the given point.
    """
    rad = math.radians(90 - angle)
    yIntercept = -(major - minor) * math.sin(rad)
    xValue = major * math.cos(rad)
    yValue = yIntercept + major * math.sin(rad)

    return (xValue, yValue)


def drawEllipse(radius, aspectRatio, arcAngle=None):
    """
    Draws an ellipse with the given radius and aspect ratio. If aspectRatio
    is less than 1, the given radius will be the ellipse's larger radius,
    and the ellipse will stretch farther to the sides of the turtle than
    in front of and behind it, otherwise the given radius will be the
    smaller radius, and the ellipse will stretch farther to the front and
    back than to the sides (the given radius is always the distance from
    the turtle's current position to the sides of the ellipse directly
    left and right of the turtle).

    There is an optional argument 'arcAngle,' which will cause this
    function to draw only part of an ellipse. The ellipse segment is
    drawn starting at the left of the current cursor position if the
    aspect ratio is greater than or equal to 1, or starting behind the
    current cursor position if the aspect ration is less than 1.
    """
    # Measure starting position/orientation
    downNow = isdown()
    startPos = pos()
    startHeading = heading()

    headingAdjust = 0

    # Start a description if there isn't a custom description active
    describing = False
    if CURRENT_DESCRIPTION is None and downNow:
        describing = True
        fmt = describePen(pensize(), pencolor())
        if aspectRatio < 1:
            majorlen = radius
            minorlen = radius * aspectRatio
            majorAngle = describeAngle(heading() + 90, normalize=180)
        else:
            majorlen = radius * aspectRatio
            minorlen = radius
            majorAngle = describeAngle(heading(), normalize=180)

        if majorAngle in ("horizontal", "vertical"):
            major = majorAngle + " major axis"
        else:
            major = "major axis at " + majorAngle

        axes = "a {}-unit {} and a {}-unit minor axis".format(
            withTenths(majorlen),
            major,
            withTenths(minorlen)
        )

        describeAs(
            "{a} {fmt} ellipse centered at ({x}, {y}) with {axes}".format(
                a=(
                    "A"
                    if arcAngle == None
                    else str(round(arcAngle)) + "° of a"
                ),
                fmt=fmt,
                x=round(startPos[0]),
                y=round(startPos[1]),
                axes=axes
            )
        )

    # Decide minor/major axes and start angle based on aspect ratio:
    if aspectRatio >= 1:
        minor = radius
        major = radius * aspectRatio
        startAngle = 0

        # Get into position to start the ellipse:
        penup()
        lt(90)
        fd(minor)
        rt(90)
        if downNow:
            pendown()
        here = (0, minor)

    else:
        minor = radius * aspectRatio
        major = radius
        startAngle = -90
        headingAdjust = -90

        # Get into position to start the ellipse:
        penup()
        lt(90)
        fd(major)
        rt(90)
        if downNow:
            pendown()
        here = (-major, 0)

    # Compute number of segments to draw based on estimated segment length:
    steps = BASE_CURVE_STEPS
    segmentLength = (2 * math.pi * major) / steps
    while segmentLength > TARGET_SEGMENT_LENGTH and steps < MAX_CURVE_STEPS:
        steps += 1
        segmentLength = (2 * math.pi * major) / steps

    # Actually draw the ellipse:
    stop = False
    for i in range(1, steps + 1):
        nextAngle = startAngle + i * 360 / steps
        if arcAngle is not None and nextAngle > startAngle + arcAngle:
            stop = True
            there = ellipsePointAt(major, minor, startAngle + arcAngle)
        else:
            there = ellipsePointAt(major, minor, nextAngle)
        vec = (there[0] - here[0], there[1] - here[1])

        # Compute heading in unrotated ellipse and distance to travel:
        towardsNext = math.degrees(math.atan2(vec[1], vec[0]))
        dist = (vec[0] * vec[0] + vec[1] * vec[1]) ** 0.5

        # Draw segment:
        setheading(startHeading + headingAdjust + towardsNext)
        fd(dist)

        # Update here -> there
        here = there

        if stop:
            break

    # Return to original position and heading:
    penup()
    goto(startPos[0], startPos[1])
    setheading(startHeading)
    if downNow:
        pendown()

    if describing:
        endDescription()


def drawDot(radius):
    """
    Draws a circle filled with the current pen color of the given radius.
    Does not move the turtle. For large circles, this may be more round
    than the result of the drawCircle function, and it will also be
    faster, but the limitation is that the circle will always be filled
    in, and the pen color will be used as the fill color (can't have
    separate border + fill colors).
    """
    # Start a description if there isn't a custom description active
    describing = False
    if CURRENT_DESCRIPTION is None and isdown():
        describing = True
        describeAs(
            "A {} dot with radius {}.".format(
                describeColor(pencolor()),
                radius
            )
        )
    oldSize = pensize()
    pensize(radius * 2)
    fd(0)
    pensize(oldSize)

    if describing:
        endDescription()


def drawSquare(size):
    """
    Draws a square of the given size centered on the current turtle
    position. Puts the turtle back when it's done.
    """
    drawRectangle(size, size)


def drawRectangle(length, width):
    """
    Draws a rectangle of the given length (in front of and behind the turtle)
    and width (to the left and right of the turtle) centered on the current
    turtle position. Puts the turtle back when it's done.
    """
    downNow = isdown()

    # Start a description if there isn't a custom description active
    describing = False
    if CURRENT_DESCRIPTION is None and downNow:
        describing = True
        fmt = describePen(pensize(), pencolor())
        x, y = position()

        # If it's square
        if width == length:
            angle = describeAngle(heading(), normalize=90)
            describeAs(
                (
                    "A {fmt} {side} by {side} square centered at"
                  + " ({x}, {y}){angle}."
                ).format(
                    fmt=describeColor(pencolor()),
                    side=length,
                    x=round(x),
                    y=round(y),
                    angle=(
                        " tilted at " + angle
                        if angle != "0°"
                        else ""
                    )
                )
            )
        else: # it has long/short axes

            # Figure out the real length/width/angle where length is longer
            dlen = length
            dwid = width
            dangle = heading()
            if width > length:
                dlen = width
                dwid = length
                dangle = heading() + 90

            angle = describeAngle(dangle, normalize=180)
            if angle in ("horizontal", "vertical"):
                angleString = "a {} long axis".format(angle)
            else:
                angleString = "a long axis at {}".format(angle)

            describeAs(
                (
                    "A {fmt} {length} by {width} rectangle centered at"
                  + " ({x}, {y}) with {angle}."
                ).format(
                    fmt=describeColor(pencolor()),
                    length=dlen,
                    width=dwid,
                    x=round(x),
                    y=round(y),
                    angle=angleString
                )
            )

    penup()
    lt(90)
    fd(width / 2)
    rt(90)
    bk(length / 2)
    if downNow:
        pendown()
    fd(length)
    rt(90)
    fd(width)
    rt(90)
    fd(length)
    rt(90)
    fd(width)
    rt(90)
    penup()
    fd(length / 2)
    rt(90)
    fd(width / 2)
    lt(90)
    if downNow:
        pendown()

    if describing:
        endDescription()


POLYGON_NAMES = [
    "point",
    "line",
    "hinge",
    "triangle",
    "quadrilateral",
    "pentagon",
    "hexagon",
    "heptagon",
    "octagon"
    "nonagon",
    "decagon",
    None, # it's called a "hendecagon," "undecagon," or "endecagon" but
    # who the heck knows that?
    "dodecagon",
]
"""
Names of polygons with various numbers of sides.
"""

def polygon_name(n):
    """
    The name for a polygon with N sides.
    """
    if n in range(len(POLYGON_NAMES)) and POLYGON_NAMES[n] != None:
        return POLYGON_NAMES[n]
    else:
        return str(n) + '-gon'


def drawPolygon(sideLength, numSides):
    """
    Draws a polygon with the given side length and number of sides,
    centered at the current position. numSides must be at least 3, or
    nothing will be drawn. The polygon created is always equilateral, and
    always has one side perpendicular to the current heading that's to the
    left of the current turtle position (left based on the current turtle
    heading).
    """
    if numSides < 3:
        return

    downNow = isdown()

    # Start a description if there isn't a custom description active
    describing = False
    if CURRENT_DESCRIPTION is None and downNow:
        describing = True
        fmt = describePen(pensize(), pencolor())
        x, y = position()
        angle = describeAngle(heading() + 90, normalize=360)
        describeAs(
            (
                "A {fmt} {shape} with side length {side} centered at"
              + " ({x}, {y}) with a flat side facing {angle}."
            ).format(
                fmt=describeColor(pencolor()),
                shape=polygon_name(numSides),
                side=sideLength,
                x=round(x),
                y=round(y),
                angle=angle
            )
        )

    # (sideLength/2) / center-side distance = tan(theta/2)
    # so center-side distance = (sideLength/2) / tan(theta/2)
    sideAngle = 360 / numSides
    centerSideDist = (
        (sideLength / 2)
      / math.tan(math.radians(sideAngle) / 2)
    )
    penup()
    lt(90)
    fd(centerSideDist)
    rt(90)
    if downNow:
        pendown()
    fd(sideLength / 2)
    rt(sideAngle)
    for i in range(numSides - 1):
        fd(sideLength)
        rt(sideAngle)

    fd(sideLength / 2)
    penup()
    rt(90)
    fd(centerSideDist)
    lt(90)
    if downNow:
        pendown()

    if describing:
        endDescription()


# Text drawing
#-------------

FONT_SIZE = 18
TEXT_ALIGN = "center"

def fontsize(size):
    """
    Sets the current font size. The default font size is 18. The argument
    must be a number, and will be rounded to the nearest integer.
    """
    global FONT_SIZE
    FONT_SIZE = int(abs(size))

def align(where):
    """
    Sets the current text alignment. The default is "center". The
    argument must be one of the strings "center", "left", or "right",
    or there will be no effect.
    """
    global TEXT_ALIGN
    if where in ("center", "left", "right"):
        TEXT_ALIGN = where


def drawText(text):
    """
    Draws the given text using the current font size and alignment (see
    the fontsize and align functions). The text is drawn due North of the
    current turtle position, no matter what direction the turtle is
    facing, and cannot be rotated. Either the left edge, the center, or
    the right edge of the text will be directly above the turtle,
    depending on the current alignment setting. The turtle is not moved
    by this command.

    If the text contains a newline character, multiple lines of text will
    be written.
    """
    # Note: This will be loudWrite, which will describe itself
    write(text, False, TEXT_ALIGN, ("Arial", FONT_SIZE, "normal"))


# Random Color Functions
#-----------------------

def randomPastelColor():
    """
    Returns a random pastel color.
    """
    return random.choice([
        # Purple
        "Plum",
        "Thistle",
        # Bluish
        "LightSkyBlue",
        "PaleTurquoise",
        # Green-blue
        "Aquamarine",
        # Greenish
        "PaleGreen",
        # Yellowish/cream
        "LightYellow",
        "BlanchedAlmond",
        # Redish
        "LightPink",
        "MistyRose",
    ])


def randomVibrantColor():
    """
    Returns a random well-saturated color.
    """
    return random.choice([
        "Blue",
        "Navy",
        "Red",
        "DarkRed",
        "Green",
        "ForestGreen",
        "Yellow",
        "Purple",
        "SaddleBrown",
        "SeaGreen",
        "Orange",
        "VioletRed",
    ])


def randomMutedColor():
    """
    Returns a random faded color.
    """
    return random.choice([
        "Aquamarine3",
        "DarkSeaGreen3",
        "DarkOrange3",
        "GoldenRod3",
        "DarkSlateGray4",
        "IndianRed3",
        "Salmon3",
        "MediumPurple2",
        "Plum3",
        "OliveDrab3",
        "PaleGreen3",
    ])


def randomWarmColor():
    """
    Returns a random well-saturated warm color.
    """
    return random.choice([
        # Pinks
        "DeepPink",
        "Salmon",
        # Reds
        "Red",
        "DarkRed",
        "Tomato",
        # Oranges
        "Orange",
        "DarkOrange",
        "Coral",
        # Yellows & browns
        "Yellow",
        "SaddleBrown",
        "Sienna",
        # Greens
        "Chartreuse",
        "YellowGreen",
    ])


def randomCoolColor():
    """
    Returns a random well-saturated cool color.
    """
    return random.choice([
        "Purple",
        "BlueViolet",
        "Blue",
        "DodgerBlue",
        "RoyalBlue",
        "Navy",
        "DarkSlateBlue",
        "Turquoise",
        "SeaGreen",
        "DarkGreen",
        "ForestGreen",
    ])

# Testing
#--------

def testTurtleBeads():
    """
    Tests this module by drawing various shapes in a grid.
    """
    setupTurtle()

    noTrace()

    teleport(-200, 200)
    drawCircle(50)
    print("Circle done...")

    teleport(-100, 200)
    drawEllipse(50, 0.5)
    print("Ellipse 1 done...")

    teleport(0, 200)
    drawEllipse(40, 1.5)
    print("Ellipse 2 done...")

    teleport(100, 200)
    drawDot(25)
    print("Filled circle done...")

    teleport(200, 200)
    drawSquare(50)
    print("Square done...")

    teleport(-200, 100)
    drawRectangle(50, 75)
    print("Rectangle 1 done...")

    teleport(-100, 100)
    drawRectangle(75, 50)
    print("Rectangle 2 done...")

    teleport(0, 100)
    drawPolygon(40, 3)
    print("Polygon 1 done...")

    teleport(100, 100)
    drawPolygon(40, 5)
    print("Polygon 2 done...")

    teleport(200, 100)
    drawPolygon(20, 12)
    print("Polygon 3 done...")

    teleport(0, 0)
    drawText("Hello\nWorld")
    print("Text done...")

    showPicture()

    teleport(-200, -80)
    for i in range(10):
        fillcolor("navy")
        begin_fill()
        lt(18.182 * i)
        drawSquare(20.1827 + 1.802938 * i)
        rt(18.182 * i)
        end_fill()
        leap(50)
    print("Row of squares is done...")

    teleport(-200, -160)
    for i in range(10):
        fillcolor("navy")
        begin_fill()
        lt(18.182 * i)
        drawEllipse(20.1827 + 1.802938 * i, 1.345 + 0.03 * i)
        rt(18.182 * i)
        end_fill()
        leap(50)
    print("Row of ellipses is done...")
    showPicture()


if __name__ == "__main__":
    testTurtleBeads()
    input("Press enter when done...")

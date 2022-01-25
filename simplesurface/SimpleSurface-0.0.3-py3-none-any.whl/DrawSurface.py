"""
Draw on an SimpleSurface object.

This class extends existing pycairo drawing functionality and introduces
some new functionality. The code is intended to be clean and accessible,
producing vector drawings that are both predictable and complex.
"""
import functools
import math

import cairo


def polygon_wrapper(func):
    """
    Wrapper function to perform the setup and teardown of polygon
    attributes before and after creating the polygon.

    Keyword arguments:
            func (function) -- the function to draw the polygon.
    """

    @functools.wraps(func)
    def draw_polygon(self, *args, **kwargs):
        """
        Setup the Context, draw the polygon with attributes applied, and
        teardown the environment.
        """
        # Save the Context so we can restore it when this is done
        self.context.save()

        # Initialize the polygon's attributes
        self._init_attributes(**kwargs)

        # Call the function
        result = func(self, *args, **kwargs)

        # Fill the polygon, if it's being filled
        if self.fill:
            self.context.fill_preserve()

        # Set the outline fill_color and outline the polygon
        self.calling_surface._set_color(self.line_color)
        self.context.stroke()

        # Restore the Context now that the polygon is drawn
        self.context.restore()

        return result

    return draw_polygon


class DrawSurface:
    """Draw a polygon on an SimpleSurface object."""

    def __init__(self, calling_surface):
        """
        Initialize the DrawSurface object.

        Keyword arguments:
                calling_surface (SimpleSurface) -- the surface to be drawn onto.

        Class attributes:
                fill_color (4-tuple) -- the RGBA fill_color of the polygon.
                fill (bool) -- whether or not the polygon is filled with fill_color.
                line_cap (str) -- the pycairo rendering of the endpoint of a line.
                line_join (str) -- the pycairo rendering for the vertex
                        connecting two joined lines.
                line_width (int) -- the thickness of the polygon's outline, in pixels.
                line_color (4-tuple) -- the RGBA fill_color of the polygon's outline.
        """
        self.calling_surface = calling_surface
        self.context = self.calling_surface.context

        self.fill_color = None
        self.fill = None
        self.line_cap = None
        self.line_join = None
        self.line_width = None
        self.line_color = None

    @polygon_wrapper
    def dot(self, x, y, radius=1, **kwargs):
        # Calculate the width and height of the inner section of the dot
        width = radius * 2 - self.line_width
        height = radius * 2 - self.line_width

        # Parse the x- and y-coordinates if they were sent in as strings.
        # The parsing methods return the top-left corner of the bounding box,
        # so we have to move the coordinates back to the center of the dot.
        if isinstance(x, str):
            x = self._parse_x(x, width) + width / 2
        if isinstance(y, str):
            y = self._parse_y(y, height) + height / 2

        # Draw the dot by moving to the center and drawing a circle with the
        # given radius, accounting for the width of the outline.
        self.context.arc(x, y, radius - self.line_width / 2, 0, 2 * math.pi)

    @polygon_wrapper
    def ellipse(self, x, y, width, height, **kwargs):
        # Determine the x and y coordinates based on other attributes
        x, y, width, height = self._adjust_params(x, y, width, height)

        # Draw an ellipse by scaling the Context by the width and height,
        # and drawing a unit circle
        self.context.save()
        self.context.translate(x + width / 2, y + height / 2)
        self.context.scale(width / 2, height / 2)
        self.context.arc(0, 0, 1, 0, 2 * math.pi)
        self.context.restore()

    def line(self, x1, y1, x2, y2, **kwargs):
        # Save the Context so we can restore it after the line is drawn
        self.context.save()

        # Initialize the shape's attributes
        self._init_attributes(**kwargs)

        # The color is actually from line_color, not fill_color
        self.calling_surface._set_color(self.line_color)

        # Establish parameters not sent in. In this case we don't need these
        # affecting anything, so we're setting them all to 0.
        width = 0
        height = 0
        self.line_width = 0

        # Parse the x and y coordinates, if need be
        x1, y1 = self._adjust_params(x1, y1, width, height)[0:2]
        x2, y2 = self._adjust_params(x2, y2, width, height)[0:2]

        # Draw the line
        self.context.move_to(x1, y1)
        self.context.line_to(x2, y2)
        self.context.stroke()

        # Restore the Context
        self.context.restore()

    @polygon_wrapper
    def polygon(self, points, **kwargs):
        # Parse each set of points
        for i, (x, y) in enumerate(points):
            points[i] = (self._parse_x(x, 0), self._parse_y(y, 0))

        # Trace a line for each edge of the shape
        self.context.move_to(points[0][0], points[0][1])
        for x, y in points[1:]:
            self.context.line_to(x, y)
        self.context.close_path()

    @polygon_wrapper
    def rectangle(self, x, y, width, height, **kwargs):
        # Parse and adjust the parameters sent in
        x, y, width, height = self._adjust_params(x, y, width, height)

        # Draw the rectangle
        self.context.rectangle(x, y, width, height)

    @polygon_wrapper
    def rounded_rectangle(self, x, y, width, height, radius, **kwargs):
        # Parse and adjust the parameters sent in
        x, y, width, height = self._adjust_params(x, y, width, height)

        # (x, y)-coordinates of the four corners.
        # The four corners are: bottom-right, bottom-left, top-left, top-right.
        # This order is due to the origin and direction that pycairo goes in
        # when it draws an arc (starts at the rightmost point of the circle and
        # moves clockwise).
        corners = [
            [x + width - radius, y + height - radius],
            [x + radius, y + height - radius],
            [x + radius, y + radius],
            [x + width - radius, y + radius],
        ]

        # Draw the four corners
        for i, (corner_x, corner_y) in enumerate(corners):
            self.context.arc(
                corner_x, corner_y, radius, (i % 4) * (math.pi / 2), ((i + 1) % 4) * (math.pi / 2)
            )

        # Draw the path connecting them together
        self.context.close_path()

    def _adjust_params(self, x, y, width, height):
        """
        Return the adjusted x, y, width, and height of the object being drawn,
        based on what's sent in and the size of the outline.

        Keyword arguments:
                x (int/str) -- the x-coordinate sent in.
                y (int/str) -- the y-coordinate sent in.
                width (int) -- the width sent in.
                height (int) -- the height sent in.
        """
        # Adjust the width and height to account for half the outline
        # on both sides of the polygon (so a full outline in total)
        width -= self.line_width
        height -= self.line_width

        # Parse the x- and y-coordinates
        x = self._parse_x(x, width)
        y = self._parse_y(y, height)

        # Return the adjusted x, y, width, and height
        return x, y, width, height

    def _init_attributes(self, **kwargs):
        """
        Initialize the attributes for the polygon being drawn,
        and set some of those attributes.

        Keyword arguments:
                fill_color (3- or 4-tuple) -- the RGB(A) fill_color of the polygon
                        (default (0, 0, 0) (black)).
                fill (bool) -- whether or not to fill the polygon with fill_color
                        (default True).
                line_cap (cairo.LINE_CAP) -- the cap at the end of the line
                        (default cairo.LINE_CAP_SQUARE).
                line_join(cairo.LINE_JOIN) -- the rendering between two
                        joining lines (default cairo.LINE_JOIN_MITER).
                line_width (int) -- the thickness of a line
                    or polygon's outline, in pixels (default 1).
                line_color (3- or 4-tuple) -- the RGB(A) fill_color of the
                        polygon's outline (default 'fill_color').
        """
        # Initialize attributes based on keyword parameters
        self.fill_color = kwargs.get("fill_color", (0, 0, 0))
        self.fill = kwargs.get("fill", True)
        self.line_cap = kwargs.get("line_cap", cairo.LINE_CAP_SQUARE)
        self.line_join = kwargs.get("line_join", cairo.LINE_JOIN_MITER)
        self.line_width = kwargs.get("line_width", 1)
        self.line_color = kwargs.get("line_color", self.fill_color)

        # Update the Context based on the attributes sent in
        self.calling_surface._set_color(self.fill_color)
        self.context.set_line_cap(self.line_cap)
        self.context.set_line_join(self.line_join)
        self.context.set_line_width(self.line_width)

    def _parse_x(self, x, width=0):
        """
        Parse the x-coordinate.

        Keyword arguments:
                x (int/str) -- the x-coordinate to parse.
                width (int) -- the width of the polygon (default 0).
        """
        # Make sure the coordinate is in the correct format
        if isinstance(x, str):
            assert x in ["left", "center", "right"], (
                f"parameter 'x' cannot be '{x}', must be either a number "
                "or one of 'left', 'center', or 'right'"
            )

        # Parse the x-coordinate, adjusting for any potential outline
        if x == "left":
            x = self.line_width / 2
        elif x == "center":
            x = (self.calling_surface.get_width() - width) / 2
        elif x == "right":
            x = self.calling_surface.get_width() - (width + self.line_width / 2)
        else:
            x += self.line_width / 2

        return x

    def _parse_y(self, y, height=0):
        """
        Parse the y-coordinate.

        Keyword arguments:
                y (int/str) -- the y-coordinate to parse.
                height (int) -- the height of the polygon (default 0).
        """
        # Make sure the coordinate is in the correct format
        if isinstance(y, str):
            assert y in ["top", "center", "bottom"], (
                f"parameter 'y' cannot be '{y}', must be either a number "
                "or one of 'top', 'center', or 'bottom'"
            )

        # Parse the y-coordinate, adjusting for any potential outline
        if y == "top":
            y = self.line_width / 2
        elif y == "center":
            y = (self.calling_surface.get_height() - height) / 2
        elif y == "bottom":
            y = self.calling_surface.get_height() - (height + self.line_width / 2)
        else:
            y += self.line_width / 2

        return y

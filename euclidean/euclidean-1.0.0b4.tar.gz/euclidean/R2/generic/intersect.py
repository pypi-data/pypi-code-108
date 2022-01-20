from multipledispatch import dispatch

from euclidean.R2.line import Line, LineSegment
from euclidean.R2.circle import Circle
from euclidean.R2.polygon import Polygon
from euclidean.R2.cartesian import P2, V2


@dispatch(Line, Line)
def intersect(line_1, line_2):
    point = line_1.intersection(line_2)
    return {point} if point else set()


@intersect.register(LineSegment, LineSegment)
def _(line_segment_1, line_segment_2):
    point = line_segment_1.intersection(line_segment_2)
    return {point} if point else set()


@intersect.register(Line, LineSegment)
def _(line, line_segment):
    return line_line_segment_intersection(line, line_segment)


@intersect.register(LineSegment, Line)
def _(line_segment, line):
    return line_line_segment_intersection(line, line_segment)


@intersect.register(Line, Circle)
def _(line, circle):
    return line_circle_intersection(line, circle)


@intersect.register(Circle, Line)
def _(circle, line):
    return line_circle_intersection(line, circle)


@intersect.register(LineSegment, Circle)
def _(line_segment, circle):
    return line_segment_circle_intersection(line_segment, circle)


@intersect.register(Circle, LineSegment)
def _(circle, line_segment):
    return line_segment_circle_intersection(line_segment, circle)


@intersect.register(Circle, Circle)
def _(circle_1, circle_2):
    return circle_circle_intersection(circle_1, circle_2)


@intersect.register(Polygon, Line)
def _(polygon, line):
    return polygon_intersection(polygon, line)


@intersect.register(Line, Polygon)
def _(line, polygon):
    return polygon_intersection(polygon, line)


@intersect.register(Polygon, LineSegment)
def _(polygon, line_segment):
    return polygon_intersection(polygon, line_segment)


@intersect.register(LineSegment, Polygon)
def _(line_segment, polygon):
    return polygon_intersection(polygon, line_segment)


@intersect.register(Polygon, Circle)
def _(polygon, circle):
    raise NotImplementedError("todo")


@intersect.register(Circle, Polygon)
def _(circle, polygon):
    raise NotImplementedError("todo")


# implementations


def line_line_segment_intersection(line, line_segment):
    point = line.intersection(line_segment.line())
    if line_segment.contains(point):
        return {point}
    return set()


def line_circle_intersection(line, circle):
    vector = circle.center.vector()
    line = line.translate(-vector)
    if line._cy == 0:
        p1 = P2(line.x(0), 0)
        p2 = P2(line.x(1), 1)
    else:
        p1 = P2(0, line.y(0))
        p2 = P2(1, line.y(1))

    dv = p2 - p1
    dr2 = dv.magnitude() ** 2
    determinant = p1.x * p2.y - p1.y * p2.x
    discriminant = circle.radius ** 2 * dr2 - determinant ** 2
    if discriminant < 0:
        return set()

    x0 = determinant * dv.y / dr2
    y0 = -determinant * dv.x / dr2

    central = P2(x0, y0) + vector

    if discriminant == 0:
        return {central}

    sqrt_descriminant = discriminant ** 0.5
    sign_y = -1 if dv.y < 0 else 1
    x_off = sign_y * dv.x * sqrt_descriminant / dr2
    y_off = abs(dv.y) * sqrt_descriminant / dr2
    offset = V2(x_off, y_off)

    return {central + offset, central - offset}


def line_segment_circle_intersection(line_segment, circle):
    points = intersect(line_segment.line(), circle)
    return set(p for p in points if line_segment.contains(p))


def circle_circle_intersection(circle_1, circle_2):
    return circle_1.intersection(circle_2)


def polygon_intersection(polygon, other):
    points = set()

    for edge in polygon.edges():
        points = points | intersect(edge, other)

    return points

from multipledispatch import dispatch

from euclidean.R2.line import Line, LineSegment
from euclidean.R2.circle import Circle
from euclidean.R2.polygon import Polygon


@dispatch(Circle, Circle)
def does_intersect(circle1, circle2):
    return circle1.does_intersect(circle2)


@does_intersect.register(Line, Line)
def _(line1, line2):
    return line1.does_intersect(line2)


@does_intersect.register(LineSegment, LineSegment)
def _(line_segment1, line_segment2):
    return line_segment1.does_intersect(line_segment2)


@does_intersect.register(Polygon, Polygon)
def _(polygon1, polygon2):
    # grab max and min points of polygons and return False if disjoint?

    for e1 in polygon1.edges():
        for e2 in polygon2.edges():
            if e1.does_intersect(e2):
                return True
    return False


@does_intersect.register(Line, LineSegment)
def _(line, line_segment):
    return __does_intersect_line_line_segment(line, line_segment)


@does_intersect.register(LineSegment, Line)
def _(line_segment, line):
    return __does_intersect_line_line_segment(line, line_segment)


@does_intersect.register(Circle, Line)
def _(circle, line):
    return __does_intersect_circle_line(circle, line)


@does_intersect.register(Line, Circle)
def _(line, circle):
    return __does_intersect_circle_line(circle, line)


@does_intersect.register(Circle, LineSegment)
def _(circle, line_segment):
    return __does_intersect_circle_line_segment(circle, line_segment)


@does_intersect.register(LineSegment, Circle)
def _(line_segment, circle):
    return __does_intersect_circle_line_segment(circle, line_segment)


@does_intersect.register(Polygon, Line)
def _(polygon, line):
    return __does_intersect_polygon_line_like(polygon, line)


@does_intersect.register(Line, Polygon)
def _(line, polygon):
    return __does_intersect_polygon_line_like(polygon, line)


@does_intersect.register(Polygon, LineSegment)
def _(polygon, line_segment):
    return __does_intersect_polygon_line_like(polygon, line_segment)


@does_intersect.register(LineSegment, Polygon)
def _(line_segment, polygon):
    return __does_intersect_polygon_line_like(polygon, line_segment)


def __does_intersect_circle_line(circle, line):
    eq = abs(line._equation(circle.center) - line._c)
    dist = eq / (line._cx ** 2 + line._cy ** 2) ** 0.5
    return dist <= circle.radius


def __does_intersect_circle_line_segment(circle, line_segment):
    closest = line_segment.line().closest(circle.center)
    p_min, p_max = line_segment.ordered()
    if closest > p_max:
        closest = p_max
    elif closest < p_min:
        closest = p_min

    dist_vec = circle.center - closest
    if dist_vec.dot(dist_vec) > circle.radius ** 2:
        return False
    return not circle.contains(p_min) or not circle.contains(p_max)


def __does_intersect_polygon_line_like(polygon, line):
    return any(does_intersect(line, edge) for edge in polygon.edges())


def __does_intersect_line_line_segment(line, line_segment):
    s1 = line.on_side(line_segment._p1)
    s2 = line.on_side(line_segment._p2)
    if s1 == 0 and s2 == 0:
        raise ValueError("Line Segment is a segment of Line.")
    return s1 != s2

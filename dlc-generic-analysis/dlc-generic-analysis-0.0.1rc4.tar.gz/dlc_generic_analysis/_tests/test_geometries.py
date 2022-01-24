from dlc_generic_analysis import geometries


def test_line_from_mx_b():
    line0 = geometries.Line(slope=2, intercept=0)
    assert line0._end1 == (0, 0)
    assert line0._end2 == (1, 2)


def test_line_from_points():
    line1 = geometries.Line((0, 5), (10, 10))
    assert line1.intercept == 5
    assert line1.slope == 0.5


def test_line_setter():
    line1 = geometries.Line((0, 0), (1, 1))
    line1.end2 = (10, 15)
    line1.end1 = (0, 10)
    assert line1.intercept == 10
    assert line1.slope == 0.5

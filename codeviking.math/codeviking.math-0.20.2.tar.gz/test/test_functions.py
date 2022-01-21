from codeviking.math.functions import *
from codeviking.math.primitives import smooth101, smooth010, rect, \
    wrap_to_interval, wrap_to_centered_interval, smooth_step_down, \
    smooth_step_up, bump, clamp01, clamp, min_max

TOL = 1.0E-7
N_SAMPLES = 10

from codeviking.math.comparisons import make_absolute_equals, make_seq_equals
from codeviking.math import sign

f_equals = make_absolute_equals(1e-7)

fl_equals = make_seq_equals(f_equals)


def check_func_values(f, x, y):
    fx = [f(xx) for xx in x]
    assert fl_equals(fx, y)


def is_strictly_monotonic(f, x0, x1, n):
    dx = (x1 - x0) / n
    assert (x0 < x1)
    assert (n > 0)
    x_samples = [x0 + dx * i for i in range(n + 1)]
    fx = [f(x) for x in x_samples]
    signs = set([sign(fx[i + 1] - fx[i]) for i in range(n)])
    n_signs = len(signs)
    if n_signs == 1:
        return signs.pop()
    return None


def check_intervals_and_knots(name, func, x_knots, y_knots, monotonicity):
    check_func_values(func, x_knots, y_knots)
    for i in range(len(monotonicity)):
        slope = is_strictly_monotonic(func,
                                      x_knots[i],
                                      x_knots[i + 1],
                                      N_SAMPLES)
        assert slope == monotonicity[i]


def test_step_slopes_0():
    assert is_strictly_monotonic(smooth_step_down, -19.0, 0.0, N_SAMPLES) == 0


def test_step_slopes_1():
    assert is_strictly_monotonic(smooth_step_down, 0.0, 1.0, N_SAMPLES) == -1


def test_step_slopes_2():
    assert is_strictly_monotonic(smooth_step_down, 1.0, 10.0, N_SAMPLES) == 0


def test_make_clamp():
    check_func_values(make_clamp(1.0, 4.5),
                      [0.0, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0],
                      [1.0, 1.0, 2.0, 3.0, 4.0, 4.5, 4.5])


def test_clamp01():
    check_func_values(clamp01,
                      [-1.0, -0.1, 0.0, 0.1, 0.5, 0.9, 1.0, 1.1, 1.9, 2.0],
                      [0.0, 0.0, 0.0, 0.1, 0.5, 0.9, 1.0, 1.0, 1.0, 1.0])


def test_mix():
    check_func_values(make_mix(0.0, 1.0),
                      [-1.0, -0.1, 0.0, 0.1, 0.5, 0.9, 1.0, 1.1, 1.9, 2.0],
                      [0.0, 0.0, 0.0, 0.1, 0.5, 0.9, 1.0, 1.0, 1.0, 1.0])


def test_mix_inverse():
    check_func_values(make_mix(1.0, 0.0),
                      [-1.0, -0.1, 0.0, 0.1, 0.5, 0.9, 1.0, 1.1, 2.0],
                      [1.0, 1.0, 1.0, 0.9, 0.5, 0.1, 0.0, 0.0, 0.0])


def test_make_mix_large():
    check_func_values(make_mix(10.0, -10.0),
                      [-1.0, -0.1, 0.0, 0.1, 0.5, 0.9, 1.0, 1.1, 2.0],
                      [10.0, 10.0, 10.0, 8.0, 0.0, -8.0, -10.0, -10.0, -10.0])


def test_make_interval_func():
    check_func_values(make_interval_func(-2.0, 3.0, 4.0,
                                         lambda x: x * x, 9.0),
                      [-5.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 5.0, 10.0],
                      [4.0, 4.0, 1.0, 0.0, 1.0, 4.0, 9.0, 9.0, 9.0])


def test_rect():
    check_func_values(rect,
                      [-1.0, -0.51, -0.5, 0.0, 0.5, 0.51, 1.0],
                      [0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0])


def test_asymmetric():
    f = make_rect_func(1.5, 4.5, 2.0, 5.0, -1.0)
    check_func_values(f,
                      [-1.0, 1.49, 1.5, 3.0, 4.5, 4.51, 5.5],
                      [2.0, 2.0, 5.0, 5.0, 5.0, -1.0, -1.0])


def test_inverted():
    f = make_rect_func(1.0, 10.0, 5.0, -2.0, 4.0)
    check_func_values(f,
                      [-1.0, 0.99, 1.0, 5.5, 10.0, 10.01, 19.0],
                      [5.0, 5.0, -2.0, -2.0, -2.0, 4.0, 4.0])


def test_smooth010():
    check_intervals_and_knots("testSmooth010",
                              smooth010,
                              [-1.0, -0.5, 0.0, 0.5, 1.0],
                              [0.0, 0.5, 1.0, 0.5, 0.0],
                              [1, 1, -1, -1])


def test_smooth101():
    check_intervals_and_knots("testSmooth101",
                              smooth101,
                              [-1.0, -0.5, 0.0, 0.5, 1.0],
                              [1.0, 0.5, 0.0, 0.5, 1.0],
                              [-1, -1, 1, 1])


def test_smooth_step_up():
    check_intervals_and_knots("smooth_step_up",
                              smooth_step_up,
                              [-10.0, 0.0, 0.5, 1.0, 10.0],
                              [0.0, 0.0, 0.5, 1.0, 1.0],
                              [0, 1, 1, 0])


def test_smooth_step_down():
    check_intervals_and_knots("smooth_step_down",
                              smooth_step_down,
                              [-10.0, 0.0, 0.5, 1.0, 10.0],
                              [1.0, 1.0, 0.5, 0.0, 0.0],
                              [0, -1, -1, 0])


def test_bump():
    check_intervals_and_knots("bump",
                              bump,
                              [-10.0, -1.0, -0.5, 0.0, 0.5, 1.0, 10.0],
                              [0.0, 0.0, 0.5, 1.0, 0.5, 0.0, 0.0],
                              [0, 1, 1, -1, -1, 0])


def test_make_bump_func_0():
    ff = make_bump_func(-3.0, -1.0, 5.0, 1.0, 4.0, 2.0)
    check_intervals_and_knots("make_bump_func asym", ff,
                              [-10.0, -3.0, -2.0, -1.0, 2.0, 5.0, 10.0],
                              [1.0, 1.0, 2.5, 4.0, 3.0, 2.0, 2.0],
                              [0, 1, 1, -1, -1, 0])


def test_make_bump_func_1():
    ff = make_bump_func(-2.0, 1.0, 7.0,
                        3.0, -13.0, -7.0)
    check_intervals_and_knots("make_bump_func asym invert", ff,
                              [-10.0, -2.0, -0.5, 1.0, 4.0, 7.0, 10.0],
                              [3.0, 3.0, -5.0, -13.0, -10.0, -7.0, -7.0],
                              [0, -1, -1, 1, 1, 0])


def test_make_bump_func_2():
    ff = make_bump_func(-1.0, 0.0, 1.0,
                        -1.0, 0.0, 1.0)
    check_intervals_and_knots("make_bump_func sigmoid", ff,
                              [-10.0, -1.0, -0.5, 0.0, 0.5, 1.0, 10.0],
                              [-1.0, -1.0, -0.5, 0.0, 0.5, 1.0, 1.0],
                              [0, 1, 1, 1, 1, 0])


def test_make_smooth_step_up():
    ff = make_smooth_step(-3.0, -1.0, y0=1.0, y1=4.0)
    check_intervals_and_knots("make_smooth_step up", ff,
                              [-10.0, -3.0, -2.0, -1.0, 10.0],
                              [1.0, 1.0, 2.5, 4.0, 4.0],
                              [0, 1, 1, 0])


def test_make_smooth_step_down():
    ff = make_smooth_step(0.0, 2.0, y0=3.0, y1=-1.0)
    check_intervals_and_knots("make_smooth_step down", ff,
                              [-10.0, 0.0, 1.0, 2.0, 10.0],
                              [3.0, 3.0, 1.0, -1.0, -1.0],
                              [0, -1, -1, 0])


def test_wrap():
    x_values = [-1.0, -0.1, 0.0, 1.0, 2.0, 3.0, 4.0, 3.99]
    y_values = [4.0, 4.9, 1.0, 2.0, 3.0, 4.0, 1.0, 4.99]
    dx = 4.0
    x0 = 1.0
    ff = lambda xx: wrap_to_interval(xx, x0, dx)
    for n in range(-10, 10):
        for i in range(len(x_values)):
            x = x0 + n * dx + x_values[i]
            y = y_values[i]
            assert f_equals(ff(x), y)


def test_centered_wrap():
    x_values = [-1.0, -0.1, 0.0, 1.0, 2.0, 3.0, 4.0, 3.99]
    y_values = [4.0, 4.9, 1.0, 2.0, 3.0, 4.0, 1.0, 4.99]
    half_width = 2.0
    center = 3.0
    dx = 4.0
    x0 = 1.0
    ff = lambda xx: wrap_to_centered_interval(xx, center, half_width)
    for n in range(-10, 10):
        for i in range(len(x_values)):
            x = x0 + n * dx + x_values[i]
            y = y_values[i]
            assert f_equals(ff(x), y)


def test_triangle_0():
    x_values = [-2.0, -1.0, 0.5, 2.0, 6.0, 10.0, 11.0]
    y_values = [1.0, 1.0, 4.0, 7.0, 3.0, -1.0, -1.0]
    ff = make_triangle_func(-1.0, 2.0, 10.0, 1.0, 7.0, -1.0)
    fx = [ff(x) for x in x_values]
    assert fl_equals(fx, y_values)


def test_triangle_1():
    x_values = [-2.0, -1.0, 0.5, 2.0, 6.0, 10.0, 11.0]
    y_values = [-1.0, -1.0, -4.0, -7.0, -3.0, 1.0, 1.0]
    ff = make_triangle_func(-1.0, 2.0, 10.0, -1.0, -7.0, 1.0)
    fx = [ff(x) for x in x_values]
    assert fl_equals(fx, y_values)


def test_step_0():
    ff = make_step(1.0)
    x_values = [-2.0, 0.99, 1.0, 1.1, 2.0, 10.0]
    y_values = [0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
    fx = [ff(x) for x in x_values]
    assert fl_equals(fx, y_values)


def test_step_1():
    ff = make_step(-7.0, 10, 5)
    x_values = [-8.0, -7.01, -7.0, -6.99]
    y_values = [10.0, 10.0, 5.0, 5.0]
    fx = [ff(x) for x in x_values]
    assert fl_equals(fx, y_values)


def test_piecewise1_0():
    f0 = lambda x: -x
    f1 = lambda x: x * x
    ff = piecewise_func1(1.0, f0, f1)
    x_values = [0.0, 0.5, 1.0, 2]
    y_values = [0.0, -0.5, 1.0, 4.0]
    fx = [ff(x) for x in x_values]
    assert fl_equals(fx, y_values)


def test_piecewise2_0():
    f0 = lambda x: -x
    f1 = lambda x: x * x
    f2 = lambda x: x
    ff = piecewise_func2(-1.0, 5.0, f0, f1, f2)
    x_values = [-2.0, -1.0, 2.0, 5.0, 6.0]
    y_values = [2.0, 1.0, 4.0, 5.0, 6.0]
    fx = [ff(x) for x in x_values]
    assert fl_equals(fx, y_values)


def test_clamp():
    assert clamp(0.0, 1.0, 2.0) == 1.0
    assert clamp(2.5, 1.0, 2.0) == 2.0
    assert clamp(1.4, 1.0, 2.0) == 1.4
    assert clamp(1.0, 1.0, 2.0) == 1.0
    assert clamp(2.0, 1.0, 2.0) == 2.0


"""
    xv = [ff(x0 + dx * i) for i in range()]

    for (int n = 0 n < 10n++) {
        for (int i = 0 i < x_values.lengthi++) {
double x = X0 + n * S + x_values[i]
double y = y_values[i]
expect(ff(x), f_equals(y))
}
}
})
double
C = 6.0
double
gg(double
xx) = > wrapToCenteredInterval(xx, C, S / 2)
test("wrapToCenteredInterval", ()
{
for (int n = 0 n < 10n++) {
for (int i = 0 i < x_values.lengthi++) {
double x = X0 + n * S + x_values[i]
double y = y_values[i]
expect(gg(x), f_equals(y))
}
}
})
}

def testFunctions():
    group("[Clamp]", testClamp)
    group("[Mix]", testMix)
    group("[IntervalFunc]", testIntervalFunc)
    group("[smooth010]", testSmooth010)
    group("[smooth101]", testSmooth101)
    group("[smoothStepUp]", testSmoothStepUp)
    group("[smoothStepDown]", testSmoothStepDown)
    group("[makeSmoothStep]", testMakeSmoothStep)
    group("[bump]", testMakeBumpFunc)
    group("[makeBumpFunc]", testMakeBumpFunc)
    group("[rect]", testRect)
"""


def test_map_to_01():
    m0 = make_map_to_01(-1, 5)
    assert m0(-4) == -0.5
    assert m0(-1) == 0
    assert m0(2.0) == 0.5
    assert m0(5.0) == 1
    assert m0(8.0) == 1.5
    m1 = make_map_to_01(5, -1)
    assert m1(-4) == 1.5
    assert m1(-1) == 1.0
    assert m1(2.0) == 0.5
    assert m1(5.0) == 0.0
    assert m1(8.0) == -0.5
    m2 = make_map_to_01(10, 10)
    assert m2(10) == 0
    assert m2(20) == 0
    assert m2(0) == 0


def test_map_from_01():
    m0 = make_map_from_01(-1, 5)
    assert m0(-0.5) == -4.0
    assert m0(0) == -1.0
    assert m0(0.5) == 2.0
    assert m0(1.0) == 5.0
    assert m0(1.5) == 8.0
    m1 = make_map_from_01(5, -1)
    assert m1(-0.5) == 8.0
    assert m1(0) == 5.0
    assert m1(0.5) == 2.0
    assert m1(1.0) == -1.0
    assert m1(1.5) == -4.0
    m2 = make_map_from_01(10, 10)
    assert m2(0) == 10
    assert m2(1) == 10


def test_map_to_01c():
    m0 = make_map_to_01c(-1, 5)
    assert m0(-4) == 0
    assert m0(-1) == 0
    assert m0(2.0) == 0.5
    assert m0(5.0) == 1
    assert m0(8.0) == 1
    m1 = make_map_to_01c(5, -1)
    assert m1(-4) == 1
    assert m1(-1) == 1.0
    assert m1(2.0) == 0.5
    assert m1(5.0) == 0.0
    assert m1(8.0) == 0
    m2 = make_map_to_01c(10, 10)
    assert m2(10) == 0
    assert m2(20) == 0
    assert m2(0) == 0


def test_map_from_01c():
    m0 = make_map_from_01c(-1, 5)
    assert m0(-0.5) == -1.0
    assert m0(0) == -1.0
    assert m0(0.5) == 2.0
    assert m0(1.0) == 5.0
    assert m0(1.5) == 5.0
    m1 = make_map_from_01c(5, -1)
    assert m1(-0.5) == 5.0
    assert m1(0) == 5.0
    assert m1(0.5) == 2.0
    assert m1(1.0) == -1.0
    assert m1(1.5) == -1.0

    m2 = make_map_from_01c(10, 10)
    assert m2(0) == 10
    assert m2(1) == 10


def test_min_max():
    assert min_max(0, 10) == (0, 10)
    assert min_max(132, 23) == (23, 132)

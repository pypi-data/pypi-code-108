import pytest
import adutils

adutils.init("logger")
from adutils import setup_logger

setup_logger()
import numpy as np

from adannealing import Annealer


def wrong_loss(x, y) -> float:
    return (x ** 2 + y ** 2) ** 2 - (x ** 2 + y ** 2)


def loss_func(w) -> float:
    x = w[0]
    return (x - 5) * (x - 2) * (x - 1) * x


def loss_func_2d(w) -> float:
    x = w[0]
    y = w[1]
    return (x - 5) * (x - 2) * (x - 1) * x + 10 * y ** 2


#
# # noinspection PyTypeChecker
# @pytest.mark.parametrize(
#     "loss,"
#     "weights_step_size,"
#     "bounds,"
#     "init_states,"
#     "temp_0,"
#     "temp_min,"
#     "alpha,"
#     "iterations,"
#     "verbose,"
#     "expected_error_type,"
#     "expected_error_message",
#     [
#         (
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             TypeError,
#             "The loss function must be callable",
#         ),
#         (
#             wrong_loss,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             ValueError,
#             "The loss function must accept exactly 1 parameter(s)",
#         ),
#         (
#             loss_func,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             TypeError,
#             "'weights_step_size' can not be None",
#         ),
#         (
#             loss_func,
#             np.array([1]),
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             TypeError,
#             "'alpha' can not be None",
#         ),
#         (
#             loss_func,
#             np.array([1]),
#             None,
#             None,
#             None,
#             None,
#             0.85,
#             None,
#             None,
#             TypeError,
#             "'temp_min' can not be None",
#         ),
#         (
#             loss_func,
#             np.array([1]),
#             None,
#             None,
#             None,
#             0,
#             0.85,
#             None,
#             None,
#             TypeError,
#             "'iterations' can not be None",
#         ),
#         (
#             loss_func,
#             np.array([1]),
#             None,
#             None,
#             None,
#             0,
#             0.85,
#             1000,
#             True,
#             ValueError,
#             "At least one of 'init_states' and 'bounds' must be specified",
#         ),
#         (
#             loss_func,
#             np.array([1, 1]),
#             np.array([-10, 10]),
#             None,
#             None,
#             0,
#             0.85,
#             1000,
#             None,
#             ValueError,
#             "'bounds' dimension should be (any, 2), got ",
#         ),
#         (
#             loss_func,
#             np.array([1, 1]),
#             np.array([[-10, 10, 0]]),
#             None,
#             None,
#             0,
#             0.85,
#             1000,
#             None,
#             ValueError,
#             "'bounds' dimension should be (any, 2), got ",
#         ),
#         (
#             loss_func,
#             np.array([1, 1]),
#             np.array([[10, -10]]),
#             None,
#             None,
#             0,
#             0.85,
#             1000,
#             None,
#             ValueError,
#             "Bounds are not valid",
#         ),
#         (
#             loss_func,
#             np.array([1, 1]),
#             np.array([[-10, 10]]),
#             None,
#             None,
#             0,
#             0.85,
#             1000,
#             None,
#             ValueError,
#             "Shape of 'weights_step_size' should be (1,)",
#         ),
#         (
#             loss_func,
#             1,
#             np.array([(-10, 10), (-10, 10)]),
#             None,
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             None,
#             "",
#         ),
#         (
#             loss_func,
#             (1, 1),
#             np.array([(-10, 10), (-10, 10)]),
#             None,
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             None,
#             "",
#         ),
#         (
#             loss_func,
#             np.array((1, 1)),
#             np.array([(-10, 10), (-10, 10)]),
#             None,
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             None,
#             "",
#         ),
#         (
#             loss_func,
#             [1, 1],
#             np.array([(-10, 10), (-10, 10)]),
#             None,
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             None,
#             "",
#         ),
#         (
#             loss_func,
#             [1, np.nan],
#             np.array([(-10, 10), (-10, 10)]),
#             None,
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             ValueError,
#             "can not contain NANs",
#         ),
#         (
#             loss_func,
#             np.nan,
#             np.array([(-10, 10), (-10, 10)]),
#             None,
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             ValueError,
#             "can not be NAN",
#         ),
#         (
#             loss_func,
#             1,
#             np.array([(-10, 10), (-10, 10)]),
#             np.nan,
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             ValueError,
#             "'init_states' can not be NAN",
#         ),
#         (
#             loss_func,
#             1,
#             np.array([(-10, 10), (-10, 10)]),
#             np.array([(-10, 10), (-10, 10)]),
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             ValueError,
#             "'init_states' must be a 1-D numpy array",
#         ),
#         (
#             loss_func,
#             1,
#             np.array([(-10, 10), (-10, 10)]),
#             [0, 0],
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             None,
#             "",
#         ),
#         (
#             loss_func,
#             1,
#             np.array([(-10, 10), (-10, 10)]),
#             (0, 0),
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             None,
#             "",
#         ),
#         (
#             loss_func,
#             1,
#             np.array([(-10, 10), (-10, 10)]),
#             np.array([0, 0]),
#             20,
#             0,
#             0.85,
#             1000,
#             True,
#             None,
#             "",
#         ),
#     ],
# )
# def test_init(
#     loss,
#     weights_step_size,
#     bounds,
#     init_states,
#     temp_0,
#     temp_min,
#     alpha,
#     iterations,
#     verbose,
#     expected_error_type,
#     expected_error_message,
# ):
#     if expected_error_type is not None:
#         with pytest.raises(expected_error_type) as e:
#             _ = Annealer(
#                 loss,
#                 weights_step_size,
#                 bounds,
#                 init_states,
#                 temp_0,
#                 temp_min,
#                 alpha,
#                 iterations,
#                 verbose,
#             )
#         assert expected_error_message in str(e.value)
#     else:
#         ann = Annealer(
#             loss,
#             weights_step_size,
#             bounds,
#             init_states,
#             temp_0,
#             temp_min,
#             alpha,
#             iterations,
#             verbose,
#         )
#         assert isinstance(ann.weights_step_size, np.ndarray)
#         assert ann.weights_step_size.dtype == float
#         assert isinstance(ann.init_states, np.ndarray)
#         assert ann.init_states.dtype == float
#         assert isinstance(ann.temp_0, float)
#         assert isinstance(ann.temp_min, float)
#         assert isinstance(ann.alpha, float)
#         assert isinstance(ann.verbose, bool)
#         assert isinstance(ann.dimensions, int)
#         assert isinstance(ann.iterations, int)
#
#
# @pytest.mark.parametrize(
#     "init_states,bounds,acceptance",
#     [
#         (None, ((0, 6),), None),
#         (None, ((0, 6),), 0.01),
#         (3.0, None, None),
#         (3.0, None, 0.01),
#         (3.0, ((0, 6),), None),
#         (3.0, ((0, 6),), 0.01),
#     ],
# )
# def test_fit_1d(init_states, bounds, acceptance):
#     attempts = 0
#     max_attempts = 5
#     while attempts < max_attempts:
#         ann = Annealer(loss=loss_func, weights_step_size=0.1, init_states=init_states, bounds=bounds, verbose=True)
#         w0, lmin, _, _, _, _ = ann.fit(stopping_limit=acceptance)
#         print(w0, lmin)
#         if (np.isclose(w0, 4.0565, rtol=5e-1, atol=5e-1) and np.isclose(lmin, -24.057, rtol=5e-2, atol=5e-2)) or (
#             np.isclose(w0, 0.39904, rtol=5e-1, atol=5e-1) and np.isclose(lmin, -1.7664, rtol=5e-2, atol=5e-2)
#         ):
#             break
#         attempts += 1
#     if attempts == max_attempts:
#         raise AssertionError("Fit failed")


@pytest.mark.parametrize(
    "init_states,bounds,acceptance",
    [
        (None, ((0, 5), (-1, 1)), None),
        (None, ((0, 5), (-1, 1)), 0.01),
        ((3.0, 0.5), None, None),
        ((3.0, 0.5), None, 0.01),
        ((3.0, 0.5), ((0, 5), (-1, 1)), None),
        ((3.0, 0.5), ((0, 5), (-1, 1)), 0.01),
    ],
)
def test_fit_2d_microcanonical(init_states, bounds, acceptance):
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        ann = Annealer(loss=loss_func_2d, weights_step_size=0.1, init_states=init_states, bounds=bounds, verbose=True)
        w0, lmin, _, _, _, _ = ann.fit(stopping_limit=acceptance, annealing_type="microcanonical", iterations=10000)
        print(w0, lmin)
        if (
            np.isclose(w0[0], 4.0565, rtol=5e-1, atol=5e-1)
            and np.isclose(w0[1], 0, rtol=5e-1, atol=5e-1)
            and np.isclose(lmin, -24.057, rtol=5e-2, atol=5e-2)
        ) or (
            np.isclose(w0[0], 0.39904, rtol=5e-1, atol=5e-1)
            and np.isclose(w0[1], 0, rtol=5e-1, atol=5e-1)
            and np.isclose(lmin, -1.7664, rtol=5e-2, atol=5e-2)
        ):
            break
        attempts += 1
    if attempts == max_attempts:
        raise AssertionError("Fit failed")


@pytest.mark.parametrize(
    "init_states,bounds,acceptance,schedule,alpha",
    [
        (None, ((0, 5), (-1, 1)), None, None, 0.85),
        (None, ((0, 5), (-1, 1)), 0.01, None, 0.85),
        ((3.0, 0.5), None, None, None, 0.85),
        ((3.0, 0.5), None, 0.01, None, 0.85),
        ((3.0, 0.5), ((0, 5), (-1, 1)), None, None, 0.85),
        ((3.0, 0.5), ((0, 5), (-1, 1)), 0.01, None, 0.85),
        (None, ((0, 5), (-1, 1)), None, "linear", 0.5),
        (None, ((0, 5), (-1, 1)), 0.01, "linear", 0.5),
        ((3.0, 0.5), None, None, "linear", 0.5),
        ((3.0, 0.5), None, 0.01, "linear", 0.5),
        ((3.0, 0.5), ((0, 5), (-1, 1)), None, "linear", 0.5),
        ((3.0, 0.5), ((0, 5), (-1, 1)), 0.01, "linear", 0.5),
        (None, ((0, 5), (-1, 1)), None, "logarithmic", 1),
        (None, ((0, 5), (-1, 1)), 0.01, "logarithmic", 1),
        ((3.0, 0.5), None, None, "logarithmic", 1),
        ((3.0, 0.5), None, 0.01, "logarithmic", 1),
        ((3.0, 0.5), ((0, 5), (-1, 1)), None, "logarithmic", 1),
        ((3.0, 0.5), ((0, 5), (-1, 1)), 0.01, "logarithmic", 1),
        (None, ((0, 5), (-1, 1)), None, "geometric", 0.85),
        (None, ((0, 5), (-1, 1)), 0.01, "geometric", 0.85),
        ((3.0, 0.5), None, None, "geometric", 0.85),
        ((3.0, 0.5), None, 0.01, "geometric", 0.85),
        ((3.0, 0.5), ((0, 5), (-1, 1)), None, "geometric", 0.85),
        ((3.0, 0.5), ((0, 5), (-1, 1)), 0.01, "geometric", 0.85),
    ],
)
def test_fit_2d(init_states, bounds, acceptance, schedule, alpha):
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        ann = Annealer(loss=loss_func_2d, weights_step_size=0.1, init_states=init_states, bounds=bounds, verbose=True)
        w0, lmin, _, _, _, _ = ann.fit(
            stopping_limit=acceptance,
            alpha=alpha,
            cooling_schedule=schedule,
            iterations=5000 if schedule != "logarithmic" else 10000,
        )
        print(w0, lmin)
        if (
            np.isclose(w0[0], 4.0565, rtol=5e-1, atol=5e-1)
            and np.isclose(w0[1], 0, rtol=5e-1, atol=5e-1)
            and np.isclose(lmin, -24.057, rtol=5e-2, atol=5e-2)
        ) or (
            np.isclose(w0[0], 0.39904, rtol=5e-1, atol=5e-1)
            and np.isclose(w0[1], 0, rtol=5e-1, atol=5e-1)
            and np.isclose(lmin, -1.7664, rtol=5e-2, atol=5e-2)
        ):
            break
        attempts += 1
    if attempts == max_attempts:
        raise AssertionError("Fit failed")


@pytest.mark.parametrize(
    "init_states,bounds,acceptance,multiproc",
    [
        (None, ((0, 5), (-1, 1)), None, False),
        (None, ((0, 5), (-1, 1)), 0.01, False),
        (None, ((0, 5), (-1, 1)), None, True),
        (None, ((0, 5), (-1, 1)), 0.01, True),
    ],
)
def test_fit_2d_multipoint(init_states, bounds, acceptance, multiproc):
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        if multiproc:
            Annealer.set_cpu_limit(2)
        else:
            Annealer.set_cpu_limit(1)
        # noinspection PyTypeChecker
        ann = Annealer(loss=loss_func_2d, weights_step_size=0.1, init_states=init_states, bounds=bounds, verbose=True)
        results = ann.fit(npoints=3, stopping_limit=acceptance)
        assert len(results) == 3
        success = 0
        for w0, lmin, _, _, _, _ in results:
            print(w0, lmin)
            if (
                np.isclose(w0[0], 4.0565, rtol=5e-1, atol=5e-1)
                and np.isclose(w0[1], 0, rtol=5e-1, atol=5e-1)
                and np.isclose(lmin, -24.057, rtol=5e-2, atol=5e-2)
            ) or (
                np.isclose(w0[0], 0.39904, rtol=5e-1, atol=5e-1)
                and np.isclose(w0[1], 0, rtol=5e-1, atol=5e-1)
                and np.isclose(lmin, -1.7664, rtol=5e-2, atol=5e-2)
            ):
                success += 1
        if success == 3:
            break
        attempts += 1
    if attempts == max_attempts:
        raise AssertionError("Fit failed")


@pytest.mark.parametrize(
    "init_states,bounds,acceptance,multiproc,npoints",
    [
        (None, ((0, 5), (-1, 1)), None, False, 3),
        (None, ((0, 5), (-1, 1)), 0.01, False, 3),
        (None, ((0, 5), (-1, 1)), None, True, 3),
        (None, ((0, 5), (-1, 1)), 0.01, True, 3),
        (None, ((0, 5), (-1, 1)), None, False, 4),
        (None, ((0, 5), (-1, 1)), 0.01, False, 4),
        (None, ((0, 5), (-1, 1)), None, True, 4),
        (None, ((0, 5), (-1, 1)), 0.01, True, 4),
        (None, ((0, 5), (-1, 1)), None, False, 5),
        (None, ((0, 5), (-1, 1)), 0.01, False, 5),
        (None, ((0, 5), (-1, 1)), None, True, 5),
        (None, ((0, 5), (-1, 1)), 0.01, True, 5),
    ],
)
def test_fit_2d_multipoint_stop_soon(init_states, bounds, acceptance, multiproc, npoints):
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        if multiproc:
            Annealer.set_cpu_limit(2)
        else:
            Annealer.set_cpu_limit(1)
        # noinspection PyTypeChecker
        ann = Annealer(loss=loss_func_2d, weights_step_size=0.1, init_states=init_states, bounds=bounds, verbose=True)
        w0, lmin, _, _, _, _ = ann.fit(npoints=npoints, stopping_limit=acceptance, stop_at_first_found=True)
        print(w0, lmin)
        if (
            np.isclose(w0[0], 4.0565, rtol=5e-1, atol=5e-1)
            and np.isclose(w0[1], 0, rtol=5e-1, atol=5e-1)
            and np.isclose(lmin, -24.057, rtol=5e-2, atol=5e-2)
        ) or (
            np.isclose(w0[0], 0.39904, rtol=5e-1, atol=5e-1)
            and np.isclose(w0[1], 0, rtol=5e-1, atol=5e-1)
            and np.isclose(lmin, -1.7664, rtol=5e-2, atol=5e-2)
        ):
            break
        attempts += 1
    if attempts == max_attempts:
        raise AssertionError("Fit failed")

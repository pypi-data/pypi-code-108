from typing import List, Optional, Union
from userinput import UserInput
import numpy as np
import abserdes

def test_deserialize_user_input_float_list():
    user_input = UserInput()
    user_input.deserialize("xmls/user_input.xml", user_input=True)
    assert user_input.positive_float_list == [
        1.0, 2.0, 3.0
    ]
    assert user_input.positive_float_list_of_lists == [
        [1.0, 2.0, 3.0], 
        [1.0, 2.0, 3.0], 
        [1.0, 2.0, 3.0], 
    ]
    assert user_input.negative_float_list== [
        -1.0, -2.0, -3.0
    ]
    assert user_input.negative_float_list_of_lists == [
        [-1.0, -2.0, -3.0], 
        [-1.0, -2.0, -3.0], 
        [-1.0, -2.0, -3.0], 
    ]
    assert user_input.mixed_float_list == [
        1.0, -2.0, 3.0
    ]
    assert user_input.mixed_float_list_of_lists == [
        [1.0, -2.0, 3.0], 
        [1.0, -2.0, 3.0], 
        [1.0, -2.0, 3.0], 
    ]
    assert user_input.positive_int_list == [
        1, 2, 3
    ]
    assert user_input.positive_int_list_of_lists == [
        [1, 2, 3], 
        [1, 2, 3], 
        [1, 2, 3], 
    ]
    assert user_input.negative_int_list== [
        -1, -2, -3
    ]
    assert user_input.negative_int_list_of_lists == [
        [-1, -2, -3], 
        [-1, -2, -3], 
        [-1, -2, -3], 
    ]
    assert user_input.mixed_int_list == [
        1, -2, 3
    ]
    assert user_input.mixed_int_list_of_lists == [
        [1, -2, 3], 
        [1, -2, 3], 
        [1, -2, 3], 
    ]
    assert user_input.mixed_int_list_of_lists == [
        [1, -2, 3], 
        [1, -2, 3], 
        [1, -2, 3], 
    ]

    assert np.array_equal(
        user_input.positive_float64_numpy_array,
        np.array([1., 2., 3.], dtype=np.float64)
    ) == True

    assert np.array_equal(
        user_input.positive_float64_numpy_array_of_numpy_arrays,
        np.array([
            [1., 2., 3.],
            [1., 2., 3.],
            [1., 2., 3.]
        ], dtype=np.float64)
    ) == True

    assert np.array_equal(
        user_input.negative_default_float_numpy_array,
        np.array([-1., -2., -3.])
    ) == True

    assert np.array_equal(
        user_input.negative_default_float_numpy_array_of_numpy_arrays,
        np.array([
            [-1., -2., -3.],
            [-1., -2., -3.],
            [-1., -2., -3.]
        ])
    ) == True

    assert np.array_equal(
        user_input.mixed_complex128_numpy_array,
        np.array([1.+0.j, -2.+0.j, 3.+0.j], dtype=np.complex128)
    ) == True

    assert np.array_equal(
        user_input.mixed_complex128_numpy_array_of_numpy_arrays,
        np.array([
            [1.+0.j, -2.+0.j, 3.+0.j],
            [1.+0.j, -2.+0.j, 3.+0.j],
            [1.+0.j, -2.+0.j, 3.+0.j]
        ], dtype=np.complex128)
    ) == True

    assert np.array_equal(
        user_input.mixed_complex64_numpy_array,
        np.array([1.+0.j, -2.+0.j, 3.+0.j], dtype=np.complex64)
    ) == True

    assert np.array_equal(
        user_input.mixed_complex64_numpy_array_of_numpy_arrays,
        np.array([
            [1.+0.j, -2.+0.j, 3.+0.j],
            [1.+0.j, -2.+0.j, 3.+0.j],
            [1.+0.j, -2.+0.j, 3.+0.j]
        ], dtype=np.complex64)
    ) == True

    assert np.array_equal(
        user_input.positive_int32_numpy_array,
        np.array([1, 2, 3], dtype=np.int32)
    ) == True

    assert np.array_equal(
        user_input.positive_int32_numpy_array_of_numpy_arrays,
        np.array([
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3]
        ], dtype=np.int32)
    ) == True

    assert np.array_equal(
        user_input.mixed_int64_numpy_array,
        np.array([1, -2, 3], dtype=np.int64)
    ) == True

    assert np.array_equal(
        user_input.mixed_int64_numpy_array_of_numpy_arrays,
        np.array([
            [1, -2, 3],
            [1, -2, 3],
            [1, -2, 3]
        ], dtype=np.int64)
    ) == True

    assert np.array_equal(
        user_input.negative_int_float_cast_numpy_array,
        np.array([-1., -2., -3.])
    ) == True

    assert np.array_equal(
        user_input.negative_int_float_cast_numpy_array_of_numpy_arrays,
        np.array([
            [-1., -2., -3.],
            [-1., -2., -3.],
            [-1., -2., -3.]
        ])
    ) == True

    assert user_input.str_list == [
        "Langevin",
        "OpenMM"
    ]


    assert user_input.str_expr_list == [
        "step(distance(g1, g2)^2 - radius^2",
        "0.5*k*(theta-theta0)^2",
    ]
    
    

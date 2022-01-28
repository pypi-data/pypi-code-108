from hypothesis import given, settings, note
from ......util import recursive_arrays


def stringify(array):
    if isinstance(array, list):
        return f"[{', '.join(stringify(item) for item in array)}]"
    return str(array)


@given(expected=recursive_arrays(operations=True))
@settings(deadline=1000)  # See #292.
def test_array_fuzzing(fuzz_value_parse_compare, expected):
    """Test that arrays parse properly."""
    array = stringify(expected)
    note(f"Array: {array}")
    fuzz_value_parse_compare(array, expected)

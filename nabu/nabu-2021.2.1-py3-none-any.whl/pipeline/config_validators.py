import os
path = os.path
from ..utils import is_writeable
from .params import *

"""
A validator is a function with
  - input: a value
  - output: the input value, or a modified input value
  - possibly raising exceptions in case of invalid value.
"""




# ------------------------------------------------------------------------------
# ---------------------------- Utils -------------------------------------------
# ------------------------------------------------------------------------------


def raise_error(section, key, msg=""):
    raise ValueError(
        "Invalid value for %s/%s: %s"
        % (section, key, msg)
    )

def validator(func):
    """
    Common decorator for all validator functions.
    It modifies the signature of the decorated functions !
    """
    def wrapper(section, key, value):
        try:
            res = func(value)
        except AssertionError as e:
            raise_error(section, key, e)
        return res
    return wrapper


def convert_to_int(val):
    val_int = 0
    try:
        val_int = int(val)
        conversion_error = None
    except ValueError as exc:
        conversion_error = exc
    return val_int, conversion_error


def convert_to_float(val):
    val_float = 0.0
    try:
        val_float = float(val)
        conversion_error = None
    except ValueError as exc:
        conversion_error = exc
    return val_float, conversion_error


def convert_to_bool(val):
    val_int, error = convert_to_int(val)
    res = None
    if not error:
        res = (val_int > 0)
    else:
        if val.lower() in ["yes", "true"]:
            res = True
            error = None
        if val.lower() in ["no", "false"]:
            res = False
            error = None
    return res, error


def convert_to_bool_noerr(val):
    res, err = convert_to_bool(val)
    if err is not None:
        raise ValueError("Could not convert to boolean: %s" % str(val))
    return res


def name_range_checker(name, valid_names, descr, replacements=None):
    name = name.strip().lower()
    if replacements is not None and name in replacements:
        name = replacements[name]
    valid = (name in valid_names)
    assert valid, "Invalid %s '%s'. Available are %s" % (descr, name, str(valid_names))
    return name


# ------------------------------------------------------------------------------
# ---------------------------- Validators --------------------------------------
# ------------------------------------------------------------------------------

@validator
def optional_string_validator(val):
    if len(val.strip()) == 0:
        return None
    return val

@validator
def file_name_validator(name):
    assert len(name) >= 1, "Name should be non-empty"
    return name

@validator
def file_location_validator(location):
    assert path.isfile(location), "location must be a file"
    return location

@validator
def optional_file_location_validator(location):
    if len(location.strip()) > 0:
        assert path.isfile(location), "location must be a file"
        return location
    return None

@validator
def optional_values_file_validator(location):
    if len(location.strip()) == 0:
        return None
    if path.splitext(location)[-1].strip() == "":
        # Assume path to h5 dataset. Validation is done later.
        if "://" not in location:
            location = "silx://" + location
    else:
        # Assume plaintext file
        assert path.isfile(location), "Invalid file path"
    return location

@validator
def directory_location_validator(location):
    assert path.isdir(location), "location must be a directory"
    return location

@validator
def optional_directory_location_validator(location):
    if len(location.strip()) > 0:
        assert is_writeable(location), "Directory must be writeable"
        return location
    return None

@validator
def dataset_location_validator(location):
    if not(path.isdir(location)):
        assert path.isfile(location) and path.splitext(location)[-1].split(".")[-1].lower() in files_formats, "Dataset location must be a directory or a HDF5 file"
    return location

@validator
def directory_writeable_validator(location):
    assert is_writeable(location), "Directory must be writeable"
    return location

@validator
def optional_output_directory_validator(location):
    if len(location.strip()) > 0:
        return directory_writeable_validator(location)
    return None

@validator
def optional_output_file_path_validator(location):
    if len(location.strip()) > 0:
        dirname, fname = path.split(location)
        assert os.access(dirname, os.W_OK), "Directory must be writeable"
        return location
    return None

@validator
def integer_validator(val):
    val_int, error = convert_to_int(val)
    assert error is None, "number must be an integer"
    return val_int

@validator
def nonnegative_integer_validator(val):
    val_int, error = convert_to_int(val)
    assert error is None and val_int >= 0, "number must be a non-negative integer"
    return val_int

@validator
def positive_integer_validator(val):
    val_int, error = convert_to_int(val)
    assert error is None and val_int > 0, "number must be a positive integer"
    return val_int

@validator
def optional_positive_integer_validator(val):
    if len(val.strip()) == 0:
        return None
    val_int, error = convert_to_int(val)
    assert error is None and val_int > 0, "number must be a positive integer"
    return val_int

@validator
def nonzero_integer_validator(val):
    val_int, error = convert_to_int(val)
    assert error is None and val_int != 0, "number must be a non-zero integer"
    return val_int

@validator
def binning_validator(val):
    if val == "":
        val = "1"
    val_int, error = convert_to_int(val)
    assert error is None and val_int >= 0, "number must be a non-negative integer"
    return max(1, val_int)

@validator
def optional_file_name_validator(val):
    if len(val) > 0:
        assert len(val) >= 1, "Name should be non-empty"
        assert path.basename(val) == val, "File name should not be a path (no '/')"
        return val
    return None

@validator
def boolean_validator(val):
    res, error = convert_to_bool(val)
    assert error is None, "Invalid boolean value"
    return res

@validator
def boolean_or_auto_validator(val):
    res, error = convert_to_bool(val)
    if error is not None:
        assert val.lower() == "auto", "Valid values are 0, 1 and auto"
        return val
    return res

@validator
def float_validator(val):
    val_float, error = convert_to_float(val)
    assert error is None, "Invalid number"
    return val_float

@validator
def optional_float_validator(val):
    if isinstance(val, float):
        return val
    elif len(val.strip()) >= 1:
        val_float, error = convert_to_float(val)
        assert error is None, "Invalid number"
    else:
        val_float = None
    return val_float

@validator
def optional_nonzero_float_validator(val):
    if isinstance(val, float):
        val_float = val
    elif len(val.strip()) >= 1:
        val_float, error = convert_to_float(val)
        assert error is None, "Invalid number"
    else:
        val_float = None
    if val_float is not None:
        if abs(val_float) < 1e-6:
            val_float = None
    return val_float

@validator
def optional_tuple_of_floats_validator(val):
    if len(val.strip()) == 0:
        return None
    err_msg = "Expected a tuple of two numbers, but got %s" % val
    try:
        res = tuple(float(x) for x in val.strip("()").split(","))
    except Exception as exc:
        raise ValueError(err_msg)
    if len(res) != 2:
        raise ValueError(err_msg)
    return res


@validator
def cor_validator(val):
    val_float, error = convert_to_float(val)
    if error is None:
        return val_float
    if len(val.strip()) == 0:
        return None
    val = name_range_checker(
        val.lower(),
        set(cor_methods.values()),
        "center of rotation estimation method",
        replacements=cor_methods
    )
    return val

@validator
def tilt_validator(val):
    val_float, error = convert_to_float(val)
    if error is None:
        return val_float
    if len(val.strip()) == 0:
        return None
    val = name_range_checker(
        val.lower(),
        set(tilt_methods.values()),
        "automatic detector tilt estimation method",
        replacements=tilt_methods
    )
    return val

@validator
def slice_num_validator(val):
    val_int, error = convert_to_int(val)
    if error is None:
        return val_int
    else:
        assert val in ["first", "middle", "last"], "Expected start_z and end_z to be either a number or first, middle or last"
        return val

@validator
def generic_options_validator(val):
    if len(val.strip()) == 0:
        return None
    return val

cor_options_validator = generic_options_validator

@validator
def cor_slice_validator(val):
    if len(val) == 0:
        return None
    val_int, error = convert_to_int(val)
    if error:
        supported = ["top", "first", "bottom", "last", "middle"]
        assert val in supported, "Invalid value, must be a number or one of %s" % supported
        return val
    else:
        return val_int

@validator
def flatfield_enabled_validator(val):
    return name_range_checker(
        val,
        set(flatfield_modes.values()),
        "flatfield mode",
        replacements=flatfield_modes
    )

@validator
def phase_method_validator(val):
    return name_range_checker(
        val,
        set(phase_retrieval_methods.values()),
        "phase retrieval method",
        replacements=phase_retrieval_methods
    )

@validator
def unsharp_method_validator(val):
    return name_range_checker(
        val,
        set(unsharp_methods.values()),
        "unsharp mask method",
        replacements=phase_retrieval_methods
    )

@validator
def padding_mode_validator(val):
    return name_range_checker(
        val,
        set(padding_modes.values()),
        "padding mode",
        replacements=padding_modes
    )

@validator
def reconstruction_method_validator(val):
    return name_range_checker(
        val,
        set(reconstruction_methods.values()),
        "reconstruction method",
        replacements=reconstruction_methods
    )

@validator
def fbp_filter_name_validator(val):
    return name_range_checker(
        val,
        set(fbp_filters.values()),
        "FBP filter",
        replacements=fbp_filters,
    )


@validator
def iterative_method_name_validator(val):
    return name_range_checker(
        val,
        set(iterative_methods.values()),
        "iterative methods name",
        replacements=iterative_methods
    )

@validator
def optimization_algorithm_name_validator(val):
    return name_range_checker(
        val,
        set(optim_algorithms.values()),
        "optimization algorithm name",
        replacements=iterative_methods
    )

@validator
def output_file_format_validator(val):
    return name_range_checker(
        val,
        set(files_formats.values()),
        "output file format",
        replacements=files_formats
    )

@validator
def distribution_method_validator(val):
    val = name_range_checker(
        val,
        set(distribution_methods.values()),
        "workload distribution method",
        replacements=distribution_methods
    )
    if val != "local":
        raise NotImplementedError("Computation method '%s' is not implemented yet" % val)
    return val

@validator
def sino_normalization_validator(val):
    val = name_range_checker(
        val,
        set(sino_normalizations.values()),
        "sinogram normalization method",
        replacements=sino_normalizations
    )
    return val

@validator
def sino_deringer_methods(val):
    val = name_range_checker(
        val,
        set(rings_methods.values()),
        "sinogram rings artefacts correction method",
        replacements=rings_methods,
    )
    return val

@validator
def list_of_int_validator(val):
    ids = val.replace(",", " ").split()
    res = list(map(convert_to_int, ids))
    err = list(filter(lambda x: x[1] is not None or x[0] < 0, res))
    if err != []:
        raise ValueError("Could not convert to a list of GPU IDs: %s" % val)
    return list(set(map(lambda x: x[0], res)))


@validator
def resources_validator(val):
    val = val.strip()
    is_percentage = False
    if "%" in val:
        is_percentage = True
        val = val.replace("%", "")
    val_float, conversion_error = convert_to_float(val)
    assert conversion_error is None, str("Error while converting %s to float" % val)
    return (val_float, is_percentage)

@validator
def walltime_validator(val):
    # HH:mm:ss
    vals = val.strip().split(":")
    error_msg = "Invalid walltime format, expected HH:mm:ss"
    assert len(vals) == 3, error_msg
    hours, mins, secs = vals
    hours, err1 = convert_to_int(hours)
    mins, err2 = convert_to_int(mins)
    secs, err3 = convert_to_int(secs)
    assert err1 is None and err2 is None and err3 is None, error_msg
    err = (hours < 0 or mins < 0 or mins > 59 or secs < 0 or secs > 59)
    assert err is False, error_msg
    return hours, mins, secs


@validator
def nonempty_string_validator(val):
    assert val != "", "Value cannot be empty"
    return val

@validator
def logging_validator(val):
    return name_range_checker(
        val,
        set(log_levels.values()),
        "logging level",
        replacements=log_levels
    )

@validator
def no_validator(val):
    return val


from pathlib import Path
import numpy as np

# Bytearray serialization code inspired from:
#  tensorflow/lite/python/util.py
#  Copyright 2018, Tensorflow Authors, Apache 2.0 license


def _bytes_to_hexa(data, max_line_width=80):
    """Returns the representation of a bytearray as a comma-separated list of
     hexadecimal values.
    """

    starting_pad = "  "
    array_lines = []
    array_line = starting_pad
    for value in bytearray(data):
        if (len(array_line) + 4) > max_line_width:
            array_lines.append(array_line + "\n")
            array_line = starting_pad
        array_line += " 0x%02x," % value
    if len(array_line) > len(starting_pad):
        array_lines.append(array_line + "\n")
    return "".join(array_lines)


def _cpp_implementation(name, declarations):
    """Wrap CPP declarations into a CPP implementation source
    """

    template = """
#include "{name}.h"

// Following tflite example, align on 32-bit if possible.
#ifdef __has_attribute
#define HAVE_ATTRIBUTE(x) __has_attribute(x)
#else
#define HAVE_ATTRIBUTE(x) 0
#endif
#if HAVE_ATTRIBUTE(aligned) || (defined(__GNUC__) && !defined(__clang__))
#define DATA_ALIGN_ATTRIBUTE __attribute__((aligned(4)))
#else
#define DATA_ALIGN_ATTRIBUTE
#endif
{declarations}
"""
    return template.format(name=name, declarations=declarations)


def _c_header(name, declarations):
    """Wrap CPP declarations into a CPP header source
    """

    include_guard = "AKIDA_" + name.upper() + "_DATA_H_"
    template = """
#ifndef {include_guard}
#define {include_guard}
{declarations}
#endif  // {include_guard}
"""
    return template.format(name=name,
                           declarations=declarations,
                           include_guard=include_guard)


def _bytearray_to_cpp(data, name, max_line_width=80):
    """Returns strings representing a CPP constant array containing `data`
     implementation and declaration.
    """

    values = _bytes_to_hexa(data, max_line_width)
    length = len(data)

    declarations = """
const unsigned char {name}[] DATA_ALIGN_ATTRIBUTE = {{
{values}}};
const int64_t {name}_len = {length};
""".format(name=name, values=values, length=length)

    source_text = _cpp_implementation(name, declarations)

    declarations = """
#include <cstdint>
extern const unsigned char {name}[];
extern const int64_t {name}_len;
""".format(name=name)

    header_text = _c_header(name, declarations)

    return source_text, header_text


def _np_array_to_cpp(np_array, name, max_line_width=80):
    """Returns strings representing a CPP constant array containing `data`
     implementation and declaration.
    """

    data = np_array.tobytes()
    values = _bytes_to_hexa(data, max_line_width)
    length = len(data)
    shape = str(np_array.shape)[1:-1]

    if np_array.dtype == np.uint8:
        tensor_type = "akida::TensorType::uint8"
    elif np_array.dtype == np.int32:
        tensor_type = "akida::TensorType::int32"
    elif np_array.dtype == np.float32:
        tensor_type = "akida::TensorType::float32"
    else:
        raise ValueError("Unsupported array type")

    declarations = """
const unsigned char {name}[] DATA_ALIGN_ATTRIBUTE = {{
{values}}};
const int64_t {name}_len = {length};
const std::vector<uint32_t> {name}_shape{{{shape}}};
const akida::TensorType {name}_type = {tensor_type};
""".format(name=name,
           values=values,
           length=length,
           shape=shape,
           tensor_type=tensor_type)

    source_text = _cpp_implementation(name, declarations)

    declarations = """
#include <cstdint>
#include <vector>
#include "akida/tensor.h"
extern const unsigned char {name}[];
extern const int64_t {name}_len;
extern const std::vector<uint32_t> {name}_shape;
extern const akida::TensorType {name}_type;
""".format(name=name)

    header_text = _c_header(name, declarations)

    return source_text, header_text


def array_to_cpp(path, array, name):
    """Generates CPP source files representing a python array

    This creates a pair of header (.h)  and implementation (.cpp) containing
    the declaration and implementation of a CPP bytes buffer whose content
    matches the source array content.

    If the source buffer is a bytearray, the following symbols are declared:

    extern const unsigned char {name}[];
    extern const int64_t {name}_len;

    If the source buffer is an np.ndarray, the following additional symbols are
    declared:

    extern const std::vector<uint32_t> {name}_shape;
    extern const akida::TensorType {name}_type;

    Args:
        path (str): the path to the generated source files directory
        array (bytearray or np.ndarray): the source array
        name: the source files name (without the extension)
    """
    if isinstance(array, np.ndarray):
        source_text, header_text = _np_array_to_cpp(array, name)
    else:
        source_text, header_text = _bytearray_to_cpp(array, name)
    # Create directory if it does not exist
    Path(path).mkdir(parents=True, exist_ok=True)
    # Save header and source file
    with open(path + '/' + name + '.h', 'w') as file:
        file.write(header_text)
    with open(path + '/' + name + '.cpp', 'w') as file:
        file.write(source_text)

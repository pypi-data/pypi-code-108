"""C converter for deep neural network models (like pytorch)

This script provides a toolkit to convert deepl learning models to c.

This file can also be imported as a module and contains the following
functions:

To build the layer route:

    * entry - returns a list with the input builder as initial element.
    * relu - returns a builder to add the relu function to the c model.
    * dense - returns a builder to add a dense layer to the c model.
    * activation_binarization - returns a builder to add binarization of the activation vector.
    * argmax - returns a builder to add the argmax function.

To transform the list of layers to c code:
    * model_transform - transforms the list of layer objects to _C_ source code.


"""

import itertools
from string import Template
from typing import Callable, NamedTuple


def map_to_carray(name: str, ctype: str, parameters: list):
    return f"{ctype} {name}[] = {{{', '.join([str(cint) for cint in parameters])}}}"


def map_to_binarray(parameters: list, int_bytes: int):
    binvalues = [1 if x == 1 else 0 for x in parameters]
    values = list(itertools.zip_longest(*[iter(binvalues)] * int_bytes, fillvalue=0))
    return [int("".join(str(x) for x in lst), 2) for lst in values]


class CArray(NamedTuple):
    name: str
    ctype: str
    values: list[int]


def build_bin_array(name: str, ctype: str, byte_size: int, values: list[int]):
    return CArray(name, ctype, map_to_binarray(values, byte_size))


def build_carray(name: str, ctype: str, values: list[int]):
    return CArray(name, ctype, values)


class CodePart(NamedTuple):
    name: str
    size: int
    declaration: list[CArray]
    definition: str


def entry(size: int) -> list[Callable[[str, str, int], CodePart]]:
    """Initializes the deep neural net layer builder

    Parameters
    ----------
    size : int
        The size of the input array

    Returns
    -------
    list
        a list with an input builder layer element.
    """

    def build_layer(name: str, prev_name: str, prev_size: int) -> CodePart:
        declaration = [build_carray(name, "uint8_t", [0] * size)]

        return CodePart(name, size, declaration, "")

    return [build_layer]


def dense(size: int, weights: list[int]) -> Callable[[str, str, int], CodePart]:
    """Dense layer builder

    Parameters
    ----------
    size : int
        The size of the output array
    weights : list[int]
        The weights array

    Returns
    -------
    Callable[[str, str, int], CodePart]
        a dense builder function.
    """

    def build_layer(
        name: str,
        prev_name: str,
        prev_size: int,
        bin_array_type: str = "unsigned long long",
        array_type: str = "int",
        byte_size: int = 32,
    ) -> CodePart:
        weight_name = name + "_weights"

        build = f"linear({prev_size}, {size}, {weight_name}, {prev_name}, {name})"

        declaration = [
            build_bin_array(weight_name, "const " + bin_array_type, byte_size, weights),
            build_carray(name, array_type, [0] * size),
        ]
        return CodePart(name, size, declaration, build)

    return build_layer


def relu() -> Callable[[str, str, int], CodePart]:
    """Dense layer builder

    Returns
    -------
    Callable[[str, str, int], CodePart]
        a relu function layer builder function.
    """

    def build_layer(name: str, prev_name: str, prev_size: int) -> CodePart:
        build = f"brelu({prev_size}, {prev_name}, {name})"

        return CodePart(name, prev_size, [], build)

    return build_layer


def activation_binarization() -> Callable[[str, str, int], CodePart]:
    """Activation binarization builder

    Returns
    -------
    Callable[[str, str, int], CodePart]
        an activation binarization builder function.
    """

    def build_layer(
        name: str,
        prev_name: str,
        prev_size: int,
        bin_array_type: str = "unsigned long long",
        array_type: str = "int",
        byte_size: int = 32,
    ) -> CodePart:
        build = f"binarize({prev_size}, {prev_name}, {name})"

        declaration = [
            build_bin_array(name, bin_array_type, byte_size, [0] * prev_size)
        ]
        return CodePart(name, prev_size, declaration, build)

    return build_layer


def argmax() -> Callable[[str, str, int], CodePart]:
    """argmax function layer builder

    The argmax function returns the position of the max element within an array

    Returns
    -------
    Callable[[str, str, int], CodePart]
        a argmax function builder function.
    """

    def build_layer(
        name: str, prev_name: str, prev_size: int, array_type: str = "int"
    ) -> CodePart:
        build = f"{name}[0] = argmax({prev_size}, {prev_name})"

        declaration = [build_carray(name, array_type, [0])]

        return CodePart(name, 1, declaration, build)

    return build_layer


def create_declaration(declarations: list[CArray]):
    def write(elements: list):
        return ";\n".join(elements) + ";"

    return write(
        [map_to_carray(arr.name, arr.ctype, arr.values) for arr in declarations]
    )


def create_layers(definitions):
    def write_tab(elements: list):
        return ";\n\t".join(elements) + ";"

    return write_tab(definitions)


def model_extract(
    layers: list[Callable[[str, str, int], CodePart]], input_name: str = "input"
) -> list[CodePart]:
    name = input_name
    prev_name = ""
    size = 0
    res: list[CodePart] = []
    for i, layer in enumerate(layers, start=1):
        (prev_name, size, declaration, definition) = layer(name, prev_name, size)
        res.append(CodePart(prev_name, size, declaration, definition))
        name = "layer_" + str(i)
    return res


def model_transform(layers: list[Callable[[str, str, int], CodePart]], template: str):
    """model transformator

    Transforms the model (list of builder functions) to C code (string)

    Parameters
    ----------
    layers : list[Callable[[str, str, int], CodePart]]
        list of builder functions
    template : str
        path of a text template

    Returns
    -------
    str
        The generated C source code.
    """
    code_parts = model_extract(layers)

    with open(template) as f:
        s = Template(f.read())
    definitions = [d for _, _, _, d in code_parts]
    declarations: list[CArray] = list(
        itertools.chain(*[d for _, _, d, _ in code_parts])
    )
    return s.substitute(
        {
            "input_name": code_parts[0].name,
            "input_type": code_parts[0].declaration[0].ctype,
            "input_size": code_parts[0].size,
            "declaration": create_declaration(declarations),
            "layers": create_layers(definitions),
            "output_value": code_parts[-1].name,
        }
    )

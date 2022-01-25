from typing import Union, Iterable, Callable

from cytoolz.curried import map, curry, valfilter

from genomoncology.parse import ensures
from genomoncology.parse.doctypes import DocType, __TYPE__, __CHILD__

SPEC_REGISTRY = {}


def register(
    transformer: Callable,
    output_type: Union[Iterable[DocType], DocType],
    input_type: Union[Iterable[DocType], DocType, None] = None,
    is_header: bool = False,
):

    for out_item in ensures.ensure_collection(output_type):
        # register glom/cytoolz transformation map (see ./specs.py)
        if input_type:
            for in_item in ensures.ensure_collection(input_type):
                SPEC_REGISTRY[(in_item, out_item, is_header)] = transformer

        # register callable catch-all class (e.g. VariantMapper)
        else:
            SPEC_REGISTRY[out_item] = transformer


def get_transformer(
    output_type: DocType,
    input_type: Union[DocType, str] = None,
    is_header: bool = False,
) -> Callable:

    transformer = None

    if input_type:
        input_type = DocType(input_type)
        key = (input_type, output_type, is_header)
        transformer = SPEC_REGISTRY.get(key)

    transformer = transformer or SPEC_REGISTRY.get(output_type)

    return transformer


@curry
def do_transform_to(output_type: DocType, value: dict):
    input_type = value.get(__TYPE__)
    is_header = DocType.HEADER.value == input_type
    if is_header:
        input_type = value.get(__CHILD__)

    transformer = get_transformer(
        output_type=output_type, input_type=input_type, is_header=is_header
    )

    value = transformer(value) if transformer else value
    return value


def create_transformer(output_type: str, state):
    output_type = DocType.create(output_type)

    transformer_cls = get_transformer(output_type)

    # handle class-based transformers (see mapper_classes.py)
    if transformer_cls and isinstance(transformer_cls, type):
        meta = valfilter(
            lambda x: x is not None,
            dict(run_id=state.run_id, pipeline=state.pipeline),
        )
        return map(transformer_cls(**meta))

    # handle functional (i.e. glom, cytoolz) based (see specs.py)
    else:
        return map(do_transform_to(output_type))

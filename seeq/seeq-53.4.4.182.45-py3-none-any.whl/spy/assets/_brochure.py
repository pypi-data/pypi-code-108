import json
import os
import textwrap

from types import ModuleType
from typing import List, Optional, Union, Type

import markdown
from mako.template import Template

from seeq.spy._errors import *

from seeq.spy.assets import _build
from seeq.spy.assets import _model

from seeq.spy.assets._model import _AssetBase, BuildContext, BuildMode, MethodType


def brochure(model: Union[ModuleType, Type[_AssetBase], List[Type[_AssetBase]]], output: str = 'dict') \
        -> Union[dict, str]:
    """
    Generates a description of a template's requirements and attributes for the
    purposes of advertising what the template offers and how it is useful.

    Docstrings for each requirement/attribute/component/etc are included in the
    output.

    Parameters
    ----------
    model : {ModuleType, type, List[type]}
        A Python module, a spy.assets.Asset or list of spy.asset.Assets
        representing the model to inspect to produce the brochure.

    output : str, default 'dict'
        The desired format of the output. Can be one of the following:

        'dict' - A dictionary of the template and all of its members, including
                 the documentation in Markdown format.
        'json' - The same as 'dict' but converted to a JSON string.
        'html' - An HTML document (in string form) where the documentation
                 has been converted from Markdown to HTML.

    Returns
    -------
    {dict, str}
        A dictionary or string according to the specified "output" argument.
    """

    if output not in ('dict', 'json', 'html'):
        raise SPyValueError('"output" argument must be either "dict", "json" or "html"')

    build_templates = _build.get_build_templates(model)

    templates_list = list()
    brochure_dict = {'Templates': templates_list}

    for build_template in build_templates:
        obj: _AssetBase = build_template(BuildContext(mode=BuildMode.BROCHURE), definition={})

        template_dict = {
            'Name': obj.template_friendly_name,
            'Description': _cleanse_doc(build_template.__doc__, output)
        }

        templates_list.append(template_dict)

        for method_type in MethodType:
            methods = obj.get_model_methods(method_type)
            method_list = list()
            template_dict[method_type.value] = method_list
            for method in methods:
                method_dict = {
                    'Name': getattr(method, _model.FRIENDLY_NAME_ATTR),
                    'Description': method.__doc__
                }

                if method_type == MethodType.REQUIREMENT:
                    method_dict.update(method())

                if 'Description' in method_dict:
                    method_dict['Description'] = _cleanse_doc(method_dict['Description'], output)

                method_list.append(method_dict)

    if output == 'dict':
        return brochure_dict
    elif output == 'json':
        return json.dumps(brochure_dict)
    elif output == 'html':
        return _dict_to_html(brochure_dict)


def _dict_to_html(brochure_dict: dict) -> str:
    template = Template(filename=os.path.join(os.path.dirname(__file__), 'brochure.html'),
                        input_encoding='utf-8')
    return template.render(brochure=brochure_dict)


def _cleanse_doc(doc: str, output: str) -> Optional[str]:
    if not doc:
        return None

    doc = textwrap.dedent(doc).strip()

    if output == 'html':
        return markdown.markdown(doc)
    else:
        return doc

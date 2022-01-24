"""
path manipulation
"""

import os

from splunk_appinspect.python_analyzer.ast_types import AstVariable
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    executable,
    tags,
)


@tags(TagConsts.PATH_MANIPULATION)
@executable
def join(args, keywords, **kwargs):
    """
    join arguments
    """
    if args:
        # only when all arguments are ready, concatenate all strings together
        for arg in args:
            if not AstVariable.is_string(arg):
                return AstVariable(None, {AstVariable.STRING_TYPE}, "?")
        root_path = args[0].variable_value
        paths = [arg.variable_value for arg in args[1:]]
        return AstVariable(
            None, {AstVariable.STRING_TYPE}, os.path.join(root_path, *paths)
        )
    else:
        return AstVariable(None, {AstVariable.STRING_TYPE}, "")

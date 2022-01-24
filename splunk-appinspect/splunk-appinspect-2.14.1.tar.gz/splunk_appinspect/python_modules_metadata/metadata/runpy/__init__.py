"""
The runpy module is used to locate and run Python modules without importing them first.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MODULE_IMPORTING)
def run_module(mod_name, init_globals=None, run_name=None, alter_sys=False):
    """Execute the code of the specified module and return the resulting module globals dictionary"""
    pass


@tags(TagConsts.MODULE_IMPORTING)
def run_path(file_path, init_globals=None, run_name=None):
    """Execute the code at the named filesystem location and return the resulting module globals dictionary"""
    pass

'''Run Jupyter notebooks as if they are functions.

Parameters can be passed to a Jupyter notebook, so that a development script can be productionised easily.

Hardcoded parameters must be moved to the first code cell of the notebook (Markdown and raw text can exist in cells above the first cell).

'''
from __future__ import absolute_import, division, print_function, unicode_literals

import nbformat
import nbconvert
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError

import ast

import os
import copy
import re

import os.path
import sys
import tokenize
import warnings
import asyncio

#TODO - go through stripping out everything we don't use

def run(notebook, timeout = None,relative_to_notebook=False, **kwargs):
    '''Run a Jupyter notebook, passing in parameters to the first cell of the notebook
    
    :param notebook: path to Jupyter notebook we wish to run
    :param timeout: timeout in seconds for notebook to run in - defaults to None
    :param relative_to_notebook: Run relative to the current working directory, or relative to the notebook? Default False - i.e. we run relative to the calling directory. Relative paths are run relative to the calling directory.
    :param **kwargs: keyword arguments that will be passed as parameters to the notebook
    '''
    
    #TODO -log as we go, using the logging queue passed in
    #TODO - do magic logging queue replacement
    #       parse calls to Site adding in logging queue magically
    
    #https://github.com/jupyter/nbconvert/issues/1372
    # See https://bugs.python.org/issue37373 :(
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        
    with open(notebook) as f:
        nb = nbformat.read(f, as_version=4)

    #We only write an output filename if there is an error
    notebook_filename_out = os.path.join(os.path.dirname(notebook), 'output_'+ os.path.basename(notebook))
    
    orig_parameters = _extract_parameters(nb)

    params = _parameter_values(orig_parameters, **kwargs)
    
    new_nb = _replace_definitions(nb, params)
    
    new_nb.metadata.filename = notebook
    
    #print('Filename:',new_nb.metadata.filename)
    
    #Replace output before running
    for cell in new_nb.cells:
        if cell["cell_type"] == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        
            try:
                #Comment out magic functions - e.g. %plot
                cell["source"] = '\n'.join(_tag_magics(cell["source"]))
            except KeyError:
                print(cell)
                raise
    #Now run the notebook - create a preprocessor
    ep = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
    
    #Now 'preprocess' the file - i.e. run it
    try:
        #Adjust the path - otherwise nothing will pick up from the directory
        if relative_to_notebook:
            working_directory = os.path.abspath(os.path.dirname(notebook))
        else:
            working_directory = os.path.abspath(os.getcwd())
        
        out = ep.preprocess(new_nb  , {'metadata': {'path': working_directory}}) 
        
    except Exception:
        #nbconvert fully expects you to save the 'preprocessed notebook'
        #but we don't want to convert the notebook, just run it
        #however, if it fails, we want to know why, so write the notebook out
        with open(notebook_filename_out, mode='wt') as f:
            nbformat.write(new_nb, f)

        out = None
        msg = 'Error executing the notebook "%s".\n\n' % notebook
        msg += 'See notebook "%s" for the traceback.' % notebook_filename_out
        print(msg)
        raise

#Modified from https://github.com/gammapy/gammapy/blob/089d552885256c560c3febdb4610b98b4e708bf0/gammapy/scripts/jupyter.py#L70 (3-clause BSD style license)

def _tag_magics(cellcode):
    """Comment magic commands."""
    MAGIC_TAG = "###-MAGIC TAG-"

    lines = cellcode.splitlines(False)
    for line in lines:
        if line.startswith("%") or line.startswith("!"):
            magic_line = MAGIC_TAG + line
            yield magic_line
        else:
            yield line        

class _Parameter(object):
    def __init__(self, name, vtype, value=None, metadata=None):
        self.name = name
        self.type = vtype
        self.value = value
        self.metadata = metadata or {}

    def __repr__(self):
        params = [repr(self.name), self.type.__name__]
        if self.value is not None:
            params.append("value=%r" % self.value)
        return "_Parameter(%s)" % ", ".join(params)

    def with_value(self, value):
        """Returns a copy with value set to a new value."""
        return type(self)(self.name, self.type, value, self.metadata or None)

def _first_code_cell(nb):
    for cell in nb.cells:
        if cell.cell_type == 'code':
            return cell

def _extract_parameters(nb, lang=None):
    """Returns a list of _Parameter instances derived from the notebook.
    This looks for assignments (like 'n = 50') in the first code cell of the
    notebook. The parameters may also have some metadata stored in the notebook
    metadata; this will be attached as the .metadata instance on each one.
    lang may be used to override the kernel name embedded in the notebook. For
    now, nbparameterise only handles 'python3' and 'python2'.
    """
    params = list(_extract_definitions(_first_code_cell(nb).source))

    # Add extra info from notebook metadata
    for param in params:
        param.metadata  = nb.metadata.get('parameterise', {}).get(param.name, {})

    return params

def _parameter_values(params, **kwargs):
    """Return a copy of the parameter list, substituting values from kwargs.
    Usage example::
        params = _parameter_values(params,
            stock='GOOG',
            days_back=300
        )
    Any parameters not supplied will keep their original value.
    """
    res = []
    for p in params:
        if p.name in kwargs:
            res.append(p.with_value(kwargs[p.name]))
        else:
            res.append(p)
    return res

def _replace_definitions(nb, values):
    """Return a copy of nb with the first code cell defining the given parameters.
    values should be a list of _Parameter objects (as returned by _extract_parameters),
    with their .value attribute set to the desired value.
    If execute is True, the notebook is executed with the new values.
    execute_resources is passed to nbconvert.ExecutePreprocessor; it's a dict,
    and if possible should contain a 'path' key for the working directory in
    which to run the notebook.
    lang may be used to override the kernel name embedded in the notebook. For
    now, nbparameterise only handles 'python3' and 'python2'.
    """
    nb = copy.deepcopy(nb)
    _first_code_cell(nb).source += '\n'+_build_definitions(values)
    return nb

def _check_fillable_node(node, path):
    if isinstance(node, (ast.Num, ast.Str)):
        return
    elif isinstance(node, ast.NameConstant) and (node.value in (True, False)):
        return
    
    raise _ASTMismatch(path, node, 'number, string or boolean')


def _type_and_value(node):
    if isinstance(node, ast.Num):
        # int or float
        return type(node.n), node.n
    elif isinstance(node, ast.Str):
        return str, node.s
    return (bool, node.value)

_definition_pattern = ast.Assign(targets=[ast.Name()], value=_check_fillable_node)
    
def _extract_definitions(cell):
    cell_ast = ast.parse(cell)
    for assign in _scan_ast_for_pattern(cell_ast,_definition_pattern):
        yield _Parameter(assign.targets[0].id, *_type_and_value(assign.value))

def _build_definitions(inputs):
    return "\n".join("{0.name} = {0.value!r}".format(i) for i in inputs)    
    
    
#Note - forked from https://github.com/takluyver/astsearch/blob/master/astcheck.py
# Would love to import it, but can't

"""Check Python ASTs against templates"""

def _format_path(path):
    formed = path[:1]
    for part in path[1:]:
        if isinstance(part, int):
            formed.append("[%d]" % part)
        else:
            formed.append("."+part)
    return "".join(formed)

class _ASTMismatch(AssertionError):
    """Base exception for differing ASTs."""
    def __init__(self, path, got, expected):
        self.path = path
        self.expected = expected
        self.got = got

    def __str__(self):
        return ("Mismatch at {}.\n"
                "Found   : {}\n"
                "Expected: {}").format(_format_path(self.path), self.got, self.expected)

class _ASTNodeTypeMismatch(_ASTMismatch):
    """An AST node was of the wrong type."""
    def __str__(self):
        expected = type(self.expected).__name__ if isinstance(self.expected, ast.AST) else self.expected
        return "At {}, found {} node instead of {}".format(_format_path(self.path), 
                        type(self.got).__name__, expected)

class _ASTNodeListMismatch(_ASTMismatch):
    """A list of AST nodes had the wrong length."""
    def __str__(self):
        return "At {}, found {} node(s) instead of {}".format(_format_path(self.path),
                len(self.got), len(self.expected))

class _ASTPlainListMismatch(_ASTMismatch):
    """A list of non-AST objects did not match.
    
    e.g. A :class:`ast.Global` node has a ``names`` list of plain strings
    """
    def __str__(self):
        return ("At {}, lists differ.\n"
                "Found   : {}\n"
                "Expected: {}").format(_format_path(self.path), self.got, self.expected)

class _ASTPlainObjMismatch(_ASTMismatch):
    """A single value, such as a variable name, did not match."""
    def __str__(self):
        return "At {}, found {!r} instead of {!r}".format(_format_path(self.path),
                    self.got, self.expected)

def _check_node_list(path, sample, template, start_enumerate=0):
    """Check a list of nodes, e.g. function body"""
    if len(sample) != len(template):
        raise _ASTNodeListMismatch(path, sample, template)

    for i, (sample_node, template_node) in enumerate(zip(sample, template), start=start_enumerate):
        if callable(template_node):
            # Checker function inside a list
            template_node(sample_node, path+[i])
        else:
            _assert_ast_like(sample_node, template_node, path+[i])

def _assert_ast_like(sample, template, _path=None):
    """Check that the sample AST matches the template.
    
    Raises a suitable subclass of :exc:`_ASTMismatch` if a difference is detected.
    
    The ``_path`` parameter is used for recursion; you shouldn't normally pass it.
    """
    if _path is None:
        _path = ['tree']

    if callable(template):
        # Checker function at the top level
        return template(sample, _path)

    if not isinstance(sample, type(template)):
        raise _ASTNodeTypeMismatch(_path, sample, template)

    for name, template_field in ast.iter_fields(template):
        sample_field = getattr(sample, name)
        field_path = _path + [name]
        
        if isinstance(template_field, list):
            if template_field and (isinstance(template_field[0], ast.AST)
                                     or callable(template_field[0])):
                _check_node_list(field_path, sample_field, template_field)
            else:
                # List of plain values, e.g. 'global' statement names
                if sample_field != template_field:
                    raise _ASTPlainListMismatch(field_path, sample_field, template_field)

        elif isinstance(template_field, ast.AST):
            _assert_ast_like(sample_field, template_field, field_path)
        
        elif callable(template_field):
            # Checker function
            template_field(sample_field, field_path)

        else:
            # Single value, e.g. Name.id
            if sample_field != template_field:
                raise _ASTPlainObjMismatch(field_path, sample_field, template_field)

def _is_ast_like(sample, template):
    """Returns True if the sample AST matches the template."""
    try:
        _assert_ast_like(sample, template)
        return True
    except _ASTMismatch:
        return False

#Note - forked from https://github.com/takluyver/astsearch/blob/master/astsearch.py
# Would love to import it, but can't

def _scan_ast_for_pattern(tree, pattern):
    """Walk an AST and yield nodes matching pattern.
    :param ast.AST tree: The AST in which to search
    :param ast.AST pattern: The node pattern to search for
    """
    nodetype = type(pattern)
    for node in ast.walk(tree):
        if isinstance(node, nodetype) and _is_ast_like(node, pattern):
            yield node


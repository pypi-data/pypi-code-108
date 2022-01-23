"""
Functions for loading submitted & solution code.

load.py
"""

import importlib
import os
import sys
import types
import tempfile
import shutil
import base64
import mimetypes

import bs4

from . import mast
from . import logging
from . import render


#-------#
# Setup #
#-------#

def setup(specs_dir, sandbox_dir):
    """
    Sets the specifications and sandbox directories.
    """
    global SPECS_DIR, SANDBOX_DIR
    SPECS_DIR = specs_dir
    SANDBOX_DIR = sandbox_dir
    # Ensure sandboxes directory exists
    os.makedirs(SANDBOX_DIR, exist_ok=True)


#------------------#
# Loader functions #
#------------------#


def load_task_spec(task_info):
    """
    Loads a task specification module for the specified task. Returns the
    imported module. Augments the module with the following values:

    - taskid: The task ID for the task
    - base_path: the path to the spec file
    - soln_path: the path to the solution files directory
    - starter_path: the path to the starter files directory
    - starter_src: the source code for the main starter file
        (or an empty string if there is no starter file or if the
        task requires more than one file)
    - soln_files: all files/directories in the solution directory (not
        full paths)
    - starter_files: all files/directories in the starter directory (not
        full paths)
    - helper_files: a list of strings naming files/directories which are
        in the starter directory and the solution directory but which
        aren't the main task file (or directory) itself. These are just
        the file names, not the full paths.
    """
    # Set up sys.path and import specifically:
    # Note: Relevant directories will need __init__.py files!
    logging.log("Loading specification for '{}'".format(task_info['id']))
    spec_target = os.path.join(SPECS_DIR, task_info["id"], "spec.py")
    logging.log("    loading from: {}".format(spec_target))
    sys.path.insert(0, SPECS_DIR)
    try:
        spec = importlib.import_module(task_info["id"] + '.spec')
    except Exception:
        logging.log("Fatal error: Unable to load task specification.")
        logging.log_current_exception()
        raise
    sys.path.pop(0)

    # Augment imported module
    here = os.path.dirname(spec.__file__)
    spec.taskid = task_info["id"]
    spec.base_path = here
    spec.soln_path = os.path.join(here, 'soln')
    spec.starter_path = os.path.join(here, 'starter')
    starter_file = os.path.join(spec.starter_path, task_info["target"])
    if os.path.isfile(starter_file):
        with open(starter_file, encoding="utf-8") as fin:
            spec.starter_src = fin.read()
    else:
        spec.starter_src = ""

    spec.soln_files = os.listdir(spec.soln_path)
    if os.path.exists(spec.starter_path):
        spec.starter_files = os.listdir(spec.starter_path)
    else:
        spec.starter_files = []
    spec.helper_files = list(
        (set(spec.soln_files) & set(spec.starter_files))
      - set([task_info["target"]])
    )

    logging.log("...done loading specification")

    return spec


def import_soln(taskspec):
    '''
    Uses importlib to import the solution module for the given task. If
    the module has already been imported, reloads it.

    Returns the imported module object.

    Fails if this task doesn't have a Python source file.
    '''
    # Here we temporarily both change cwd *and* push it onto our sys.path.
    original_directory = os.getcwd()
    os.chdir(taskspec.soln_path)
    sys.path.insert(0, os.getcwd())
    try:
        module_name = taskspec.src.replace('.py', '')
        if module_name in sys.modules:
            return importlib.reload(sys.modules[module_name])
        else:
            return importlib.import_module(module_name)
    finally:
        # Reset cwd and sys.path:
        os.chdir(original_directory)
        sys.path = sys.path[1:]


def load_instructions_html(spec):
    """
    Given a specifications module, loads the instructions for that module
    and converts them from markdown to HTML. This loads "instructions.md"
    in the spec folder, or if it's not present, the dosctring of the
    specs module. Logs a message about where it fetched the instructions
    from.

    Note that the instructions may need resources copied with them in
    order to render properly, but this function doesn't handle that
    completely. What it does do is look for resources it knows how to
    handle (img, audio, and video tags) and embed their data into the
    HTML result as base64-encoded data: URLs. This makes it easier for
    the instructions to be embedded in multiple contexts, although it
    does increase their overall size a bit.
    """
    # Default path to check
    src = os.path.join(spec.base_path, "instructions.md")
    if os.path.exists(src):
        with open(src, 'r', encoding="utf-8") as fin:
            instructions = fin.read()
        logging.log("Fetched instructions from '{}'...".format(src))
    elif spec.__doc__:
        # Pull from spec docstring if there's no instructions.md file
        instructions = spec.__doc__
        logging.log(
            "Fetched instructions from spec module's docstring..."
        )
    else:
        logging.log("Couldn't find any instructions...")
        instructions = "(no instructions available)"

    # Convert to HTML
    html = render.render_markdown(instructions)

    # Now we need to embed resource files...

    # Get a bs4 handle for it
    soup = bs4.BeautifulSoup(html, "html.parser")

    # Find all img, audio, or video tags with src attributes...
    for tag in soup.find_all(
        lambda tag: (
            tag.name in ("img", "audio", "video")
        and tag.has_attr("src")
        )
    ):
        orig_src = tag["src"]
        target = os.path.join(spec.base_path, orig_src)
        if os.path.isfile(target):
            mime, enc = mimetypes.guess_type(target, strict=False)
            if mime is None:
                mime = "text/plain"
            # TODO: Handle encoding guess!
            with open(target, 'rb') as fin:
                src_bytes = fin.read()
                data = base64.standard_b64encode(src_bytes).decode("utf-8")
            # Build a data URI and update the src attribute:
            data_uri = "data:{};base64,{}".format(mime, data)
            tag['src'] = data_uri
            # Log a message
            logging.log("Embedded resource '{}'".format(orig_src))
        else:
            # Log a warning and let it go...
            logging.log(
                "Warning: resource '{}' was not found.".format(orig_src)
            )

    return str(soup)


#--------------------------#
# Module loading & parsing #
#--------------------------#


def create_module_in_sandbox(
    node,
    filename,
    sandbox_dir=None,
    sandbox_links=None,
    sandbox_files=None,
    on_disk=None
):
    """
    Given an AST node and a filename, creates a temporary sandbox
    directory, runs the code in the sandbox to create a module object,
    and returns the module object that was created.

    An explicit sandbox directory that's already set up may be provided
    via the `sandbox_dir` parameter. If none is provided, a new sandbox
    will be created and then destroyed in the course of running this
    function. If an existing sandbox will be used, `sandbox_links` and
    `sandbox_files` are ignored.

    If a pre-existing sandbox isn't provided and extra files are needed
    in the sandbox, a dictionary mapping absolute paths to
    paths-in-sandbox can be supplied and those files will be symlinked in
    (see `link_mapping`). Alternatively, an equivalently-structured
    sandbox_files directory may be supplied to copying files rather than
    creating links, which is typically less efficient, but desirable if
    those files will be modified.

    If on_disk is provided, it should be a full path to the file that the
    code was parsed from, and will be used to provide a __file__
    variable while the code runs.
    """
    if sandbox_dir is not None:
        # A sandbox directory has been provided ready-to-use; ignore
        # sandbox_links and sandbox_files.

        # Create the module
        result = create_module_from_code(
            node,
            filename,
            on_disk=on_disk,
            sandbox=sandbox_dir
        )
    else:
        # We need to create our own sandbox directory
        with tempfile.TemporaryDirectory(
            suffix="__tmp",
            dir=SANDBOX_DIR
        ) as tmpdir:
            # Create symlinks
            if sandbox_links is not None:
                for filepath in sandbox_links:
                    to = os.path.join(tmpdir, sandbox_links[filepath])
                    os.symlink(filepath, to)

            # Copy files
            if sandbox_files is not None:
                for filepath in sandbox_files:
                    to = os.path.join(tmpdir, sandbox_files[filepath])
                    shutil.copy(filepath, to)

            # Create the module
            result = create_module_from_code(
                node,
                filename,
                on_disk=on_disk,
                sandbox=tmpdir
            )

    return result


def create_module_from_code(node, filename, on_disk=None, sandbox=None):
    """
    Given an AST node and a filename, creates a module object and
    registers it in sys.modules. The module name is the filename without
    any extension (.py or otherwise) and the module docstring is
    extracted from the given AST node if possible (i.e., when the first
    statement in the module body is a string constant).

    If on_disk is provided, it should be a full path to the file that the
    code was parsed from, and will be used to provide a __file__
    variable while the code runs.

    If a sandbox is provided, it should be a string indicating the path
    to a directory which should be set as current and added to the front
    of sys.path while we execute the code.
    """
    module_name = os.path.splitext(filename)[0]

    # Compile the AST node into executable code
    bytecode = compile(
        node,
        module_name + ".py", # necessary to get __name__ correct
        "exec"
    )

    # Grab module docstring if it exists
    try:
        module_docstring = node.body[0].value.value
    except Exception:
        module_docstring = ""

    # Create a new module and insert it into sys.modules (must
    # happen before execution of the module code!)
    module = types.ModuleType(module_name, module_docstring)
    sys.modules[module_name] = module
    module.__dict__["__name__"] = module_name + ".py"
    module.__dict__["__file__"] = on_disk

    if sandbox is None:
        # Execute the code in the module's dictionary, which fleshes
        # out the module
        exec(bytecode, module.__dict__, module.__dict__)
    else:
        # If we've been given a sandbox directory, use it
        prev_dir = os.getcwd()
        os.chdir(sandbox)
        sys.path.insert(0, sandbox)
        try:
            # Execute the code in the module's dictionary, which fleshes
            # out the module
            exec(bytecode, module.__dict__, module.__dict__)
        finally:
            sys.path = sys.path[1:]
            os.chdir(prev_dir)

    # Return our completed module
    return module


def fix_parse(codestring, filename, exn=None):
    '''
    Inherited from net.py in Codder.

    Tries to comment out lines with syntax errors to recover remaining
    code. Returns a tuple containing the (possibly edited) code string
    that was parsed, the AST object resulting from the parse, and a list
    of errors (Exception objects) encountered along the way. If it
    encounters an unrecoverable exception, it will return None in place
    of the AST object.

    This function is recursive, and if given an exception to work with,
    it starts by commenting out relevant lines of the file before
    attempting to parse it again.
    '''
    try:
        # if parsing fails for any reason we'll reattempt based on the
        # error...
        if exn:
            # if we encountered an exception, comment out that line and
            # any previous lines that end with ':' or which are empty or
            # comments...
            eindex = exn.lineno - 1
            lines = codestring.split('\n')
            lines[eindex] = '## SYNTAX ERROR ## ' + lines[eindex]

            # Grab lines above too, back to the nearest line which doesn't
            # end in ':', not counting comments or blank lines. This
            # helps ensure that if our syntax error is the only statement
            # in a loop or conditional, that loop/conditional dies with
            # it.
            for i in range(eindex - 1, 0, -1):
                predline = lines[i].strip()
                if (
                  predline.endswith(':')
               or predline.startswith('#')
               or len(predline) == 0
                ):
                    lines[i] = '## SYNTAX ERROR BUDDY ## ' + lines[i]
                else:
                    break
                pass
            pass

            # Rebuild our code string with the new comments in place
            codestring = '\n'.join(lines)
        pass

        # Whether or not we just commented out some code, we'll try to
        # parse what we've got. An error here will throw us into one of
        # the except clauses below, or bubble out if it's not one we're
        # expecting.
        tree = mast.parse(codestring, filename=filename)

        # Parsing at this level didn't encounter any errors, so our error
        # list will be empty. Whoever called us is responsible for adding
        # the error they encountered if they passed us an error to watch
        # out for.
        return (codestring, tree, [])

    except (mast.MastParseError, SyntaxError, IndentationError) as e:
        # These are expected parsing errors that we're prepared to
        # address by commenting out code

        # If it's a MastParseError, process the trigger instead...
        if isinstance(e, mast.MastParseError):
            e = e.trigger

        if not isinstance(e, (SyntaxError, IndentationError)):
            # A MastParseError not triggered by a syntax/indentation error
            logging.log("'{}' is not a valid Python file".format(filename))
            return (codestring, None, [e])

        if exn and e.lineno == exn.lineno:
            # if it persists on the same line of code despite introducing
            # a comment, we give up
            raise e
        else:
            # Recurse to try to fix this new error
            try:
                c, a, es = fix_parse(
                    codestring,
                    filename,
                    exn=e
                )
            except (SyntaxError, IndentationError) as e:
                # give up if we couldn't fix it
                return (codestring, None, [exn] if exn else [e])
            else:
                # If there isn't an exception, we can return the code
                # along with this error plus any other errors
                return (c, a, [e] + es)

    except TypeError as e:
        # Happens e.g., when the file is not a python file
        logging.log("'{}' is not a valid Python file".format(filename))
        return (codestring, None, [e])

    except Exception:
        logging.log(
            "Encountered unexpected exception when parsing '{}'"
            .format(filename)
        )
        logging.log_current_exception()

    # Let any other unexpected errors bubble out

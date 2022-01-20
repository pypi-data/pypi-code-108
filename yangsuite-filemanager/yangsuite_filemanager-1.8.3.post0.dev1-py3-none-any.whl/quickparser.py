# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Quick and dirty parsing of YANG files to extract module and dependency info.

Heavily based on symd - at present symd itself doesn't meet our needs for
several reasons:

1. symd uses a global variable 'G' to store its network graph, which will
   of course not work in our multi-user environment
2. symd automatically imports matplotlib, which is a pretty beefy package
3. symd presumes output to console or file, rather than providing clean
   APIs for use as a library.

In any case, we're only actually using a very small subset of symd,
so we can just implement our own version of that functionality here.

Again, this is *quick and dirty* parsing focused on very basic information
including module name and revision and imports/includes. If you want more
thorough, more foolproof parsing, use pyang or something like it instead.

This is NOT an attempt at implementing a full YANG parser like pyang,
and there are known cases where it *will* fail:

- YANG string concatenation - per the RFC, the following strings
  are all equivalent::

      hello
      "hello"
      'hello'
      "hel" + "lo"
      'hel' + "lo"

  The regexps used here will handle variant quoting but *not* concats.

- Extra or missing line wraps - per the RFC, these are both valid::

      module "foo" {
        import bar {
          prefix bar;
        }
      }

      module
          "foo"
      { import bar { prefix bar; } }

  but our regexps above only handle the former (albeit much more
  commonly seen) format.

- Comments - some modules (e.g., tailf-common) have comments that
  contain examples; since we're doing line-by-line checking with no
  parser state machine, we don't ignore the comment's contents and may
  pick up the comment lines as part of the perceived schema.
"""

import errno
import io
import os
import re
from yangsuite import get_logger

log = get_logger(__name__)


def name_and_revision_from_file(path, assume_correct_name=True):
    """Quickly retrieve the module name and revision from a YANG file.

    Args:
      path (str): Path to file to inspect
      assume_correct_name (bool): If True, assume that ``foo@bar.yang`` has
        already been confirmed to describe module 'foo' revision 'bar' and
        don't bother (re)checking the file contents.
        If False, trust no-one!

    Returns:
      tuple: (name, revision). If the YANG file has no defined revision
      (acceptable per the RFC), then revision will be 'unknown'.

    Raises:
      OSError: if the file does not exist
      ValueError: if unable to determine the name.
    """
    if not os.path.exists(path):
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), path)
    elif not os.path.isfile(path):
        raise OSError(errno.EINVAL, os.strerror(errno.EINVAL), path)
    name = None
    rev = None
    if not assume_correct_name:
        log.debug("Checking contents of %s to find module name/revision",
                  path)

        try:
            # quick_parse will either return name and revs or raise an error
            data = quick_parse(path)
            name = data['name']
            rev = data['revisions'][0]
        except (IOError, UnicodeDecodeError):
            log.warning("Error in parsing %s", path)
            # fallthrough

    if not name:
        # assume_correct_name == True, or quick_parse failed.
        # Either way, fall back to checking filename.
        filename, ext = os.path.splitext(os.path.basename(path))
        if ext != '.yang':
            raise ValueError("File '{0}' is probably not a YANG file?"
                             .format(os.path.basename(path)))
        # Hope file is correctly named as name[@revision].yang
        if '@' in filename:
            name, rev = filename.split('@')
        else:
            name, rev = filename, 'unknown'

    return (name, rev)


def module_listing(filepaths, assume_correct_name=False):
    """Given a list of files, return a list of (name, revision) tuples.

    Args:
      filepaths (list): List of .yang file paths, such as returned by
        :func:`.list_yang_files`
      assume_correct_name (bool): See :func:`name_and_revision_from_file`.

    Returns:
      list: [(name, rev, path), (name, rev, path), ...]
    """
    modules = []
    for filepath in filepaths:
        if not os.path.isfile(filepath):
            log.debug("Skipping non-file '%s'", filepath)
            continue
        name, rev = name_and_revision_from_file(
            filepath, assume_correct_name=assume_correct_name)
        modules.append((name, rev, filepath))

    return sorted(modules)


#
# Regular expressions for NAIVE, QUICK and DIRTY parsing of YANG files
#

IDENTIFIER = r"""["']?([a-zA-Z_][-a-zA-Z0-9_.]*)["']?"""
"""Regular expression matching YANG 'identifier' syntax w/ optional quoting."""

_SUBSTMT_MAND = r"""[ \t]*(?:\{|$|\+)"""
"""End of a YANG statement with at least one mandatory sub-statement."""

_SUBSTMT_OPT = r"""[ \t]*(?:;|\{|$|\+)"""
"""End of a YANG statement with optional but no mandatory sub-statements."""

_SUBSTMT_NONE = r"""[ \t]*(?:;|$)"""
"""End of a YANG statement with no sub-statements allowed."""

# 'module' has mandatory sub-statements
MODULE_STATEMENT = re.compile(
    '''^(sub)?module[ \t]+''' + IDENTIFIER + _SUBSTMT_MAND)
"""Regular expression matching the YANG 'module' or 'submodule' syntax."""

# 'revision' has only optional sub-statements
REVISION_STATEMENT = re.compile(
    '''^revision[ \t]+['"]?(\d{4}-\d{2}-\d{2})['"]?''' + _SUBSTMT_OPT)
"""Regular expression matching the YANG 'revision' statement syntax."""

# 'import' has mandatory sub-statement
IMPORT_STATEMENT = re.compile(
    '''^import[ \t]+''' + IDENTIFIER +
    '''[ \t]*(?:$|\+|\{[ \t]*(?:prefix[ \t]+''' + IDENTIFIER + ")?)")
"""Regular expression matching the YANG 'import' statement syntax.

May include inline 'prefix ...' substatement."""

# 'prefix' has no sub-statements
PREFIX_STATEMENT = re.compile(
    '''^prefix[ \t]+''' + IDENTIFIER)   # TODO: + _SUBSTMT_NONE ?

# 'include' has only optional sub-statements
INCLUDE_STATEMENT = re.compile(
    '''^include[ \t]+''' + IDENTIFIER + _SUBSTMT_OPT)
"""Regular expression matching the YANG 'include' statement syntax."""

# 'augment' has only optional sub-statements
AUGMENT_STATEMENT = re.compile(
    '''^augment[ \t]+["']?([-a-zA-Z0-9_.:/]+)["']?''' + _SUBSTMT_OPT)
"""Regular expression matching the YANG 'augment' statement syntax."""

PREFIX_IDENTIFIER_TOKEN = re.compile(
    '''([a-zA-Z_][-a-zA-Z0-9_.]*):([a-zA-Z_][-a-zA-Z0-9_.]*)''')
"""Regular expression matching a prefixed identifier token."""

# 'belongs-to' has mandatory 'prefix' sub-statement
BELONGS_TO_STATEMENT = re.compile(
    '''^belongs-to[ \t]+''' + IDENTIFIER + _SUBSTMT_MAND)

# 'identity' has only optional sub-statements
IDENTITY_STATEMENT = re.compile(
    '''^identity[ \t]+''' + IDENTIFIER + _SUBSTMT_OPT)

# 'base' has no sub-statements
BASE_STATEMENT = re.compile(
    '''^base[ \t]+["']?([-a-zA-Z0-9_.:]+)["']?''' + _SUBSTMT_NONE)


def quick_parse(path):
    """Quickly parse a YANG file for info about it and its relation to others.

    See also :func:`symd.parse_yang_module`

    As noted in the module docstring, this is NOT an attempt at implementing
    a full YANG parser like pyang, and there are known corner cases where it
    *will* fail. But it's a lot less heavy than pyang.

    Args:
      path (str): YANG file to attempt to parse.

    Returns:
      dict: with keys:

      - ``name`` - name of this module
      - ``kind`` - ``'module'`` or ``'submodule'``
      - ``imports`` - dict of {module: prefix} this imports
      - ``includes`` - list of submodules this includes
      - ``revisions`` - list of revisions declared in this module,
        in reverse chronological order
      - ``augments`` - list of modules this augments
      - ``belongs-to`` - if this is a submodule, the name of the parent module

    Raises:
      IOError: if the file does not contain a 'module' statement
    """
    result = {
        'name': None,
        'kind': None,
        'imports': {},
        'includes': [],
        'revisions': [],
        'augments': set(),
        'belongs-to': None,
        'derives-identities-from': set(),
    }

    import_prefixes = {}
    import_unknown_prefixes = []

    with io.open(path, 'r', encoding="utf-8", errors="replace") as fp:
        def readahead():
            pos = fp.tell()
            line = fp.readline()
            fp.seek(pos, io.SEEK_SET)
            if line:
                return line.strip()
            return ''

        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            # Note that we do character checks (quick!) before
            # regexp matching (slow!)
            if not result['name']:
                # Any chance of 'module' or 'submodule'?
                if not line[0] in 'ms':
                    continue
                match = MODULE_STATEMENT.match(line)
                if match:
                    result['name'] = match.group(2)
                    if match.group(1) == 'sub':
                        result['kind'] = 'submodule'
                    else:
                        result['kind'] = 'module'
            elif line[0] == 'i':
                match = IMPORT_STATEMENT.match(line)
                if match:
                    # In tailf-common, there's some example code in a comment
                    # with 'import x' that we falsely pick up. There shouldn't
                    # be a real module named 'x' in any case.
                    if match.group(1) == 'x':
                        continue
                    result['imports'][match.group(1)] = None
                    # Can we determine the prefix we assign to the import?
                    if match.group(2):
                        # Inline prefix statement (import foo { prefix bar })
                        import_prefixes[match.group(2)] = match.group(1)
                        result['imports'][match.group(1)] = match.group(2)
                    else:
                        # Prefix statement is probably on next line:
                        line2 = readahead()
                        match2 = PREFIX_STATEMENT.match(line2)
                        if match2:
                            import_prefixes[match2.group(1)] = match.group(1)
                            result['imports'][match.group(1)] = match2.group(1)
                        else:
                            import_unknown_prefixes.append(match.group(1))
                    continue

                match = INCLUDE_STATEMENT.match(line)
                if match:
                    # In CISCO-FIREWALL-TC, there's a line of text in a
                    # description that is simply "include them.".
                    # Don't be fooled by this.
                    if match.group(1) == "them.":
                        continue
                    result['includes'].append(match.group(1))
                    continue

                match = IDENTITY_STATEMENT.match(line)
                if match:
                    # Base statement is *usually* on the next line:
                    line2 = readahead()
                    match2 = BASE_STATEMENT.match(line2)
                    if match2:
                        # Is it a prefixed base?
                        match3 = PREFIX_IDENTIFIER_TOKEN.match(match2.group(1))
                        if match3:
                            pfx = match3.group(1)
                            if pfx in import_prefixes:
                                result['derives-identities-from'].add(
                                    import_prefixes[pfx])
                            else:
                                result['derives-identities-from'].update(
                                    import_unknown_prefixes)
                    continue
            elif line[0] == 'r':
                match = REVISION_STATEMENT.match(line)
                if match:
                    result['revisions'].append(match.group(1))
            elif line[0] == 'a':
                match = AUGMENT_STATEMENT.match(line)
                if match:
                    augment_target = match.group(1)
                    # Examples:
                    # /ocif:interfaces/ocif:interface/lag:aggregation
                    # /ocif:interfaces/ocif:interface/eth:ethernet
                    for pfx, ident in PREFIX_IDENTIFIER_TOKEN.findall(
                            augment_target):
                        if pfx in import_prefixes:
                            # We know we augment this module
                            result['augments'].add(import_prefixes[pfx])
                        else:
                            # Augmenting a module we can't determine,
                            # so flag all the modules we aren't sure about
                            # as possible augment targets
                            result['augments'].update(import_unknown_prefixes)
            elif line[0] == 'b' and result['kind'] == 'submodule':
                match = BELONGS_TO_STATEMENT.match(line)
                if match:
                    result['belongs-to'] = match.group(1)

    if not result['name']:
        raise IOError("No module statement found in {0}".format(path))

    if not result['revisions']:
        # pyang reports 'unknown' rather than None for no revision found.
        # Would prefer None but it's easier to follow their lead.
        result['revisions'] = ['unknown']

    result['includes'] = sorted(result['includes'])
    result['augments'] = sorted(result['augments'])
    result['revisions'] = list(reversed(sorted(result['revisions'])))
    result['derives-identities-from'] = sorted(
        result['derives-identities-from'])

    return result

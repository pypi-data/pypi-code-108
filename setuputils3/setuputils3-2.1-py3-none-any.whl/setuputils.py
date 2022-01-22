#!/usr/bin/env python3
"""
Module SETUPUTILS -- Utilities to automate boilerplate in Python setup scripts
Copyright (C) 2012-2022 by Peter A. Donis

Released under the Python Software Foundation License.

This module was originally released to help automate away much of the
boilerplate that goes into Python setup scripts. However, the tools
for packaging Python applications and libraries have evolved a lot since
then, and setuputils now supports a new mode of operation that takes
advantage of the updated standards and tools.

The preferred way to use setuputils now is to have it build a setup.cfg
file from inputs that you supply and from its ability to auto-discover
the things that typically go into a distribution of your Python application
or library. The main tool that uses setup.cfg, setuptools, also has much
the same capability, but the advantage with setuputils is that you get
to see all the output of the autodiscovery logic in the final setup.cfg
file *before* using it to build your distribution. With setuptools, you
have no way of getting an advance look at what the tool thinks should go
into your distribution; you only see what's in the distribution after it
is built.

Using setuputils in this mode is described in the README file that comes
with the setuputils distribution. This mode supports both being run as
a stand-alone tool to build setup.cfg prior to doing an sdist or wheel
build, and being run as a PEP 517 build backend that builds setup.cfg
before each build to ensure consistency with the current state of your
source tree. This mode also supports reading global variables from a
setup.py script if that is present (see further comments below); but if
setup.py is present, setuputils cannot be used as a build backend, it
can only be used to generate setup.cfg prior to doing a build.

(Note that extension modules are currently not supported in setup.cfg,
so you cannot use setuputils in setup.cfg mode if your distribution
contains any extension modules. You can still use it in "legacy" mode,
described below. There are some other setuptools keywords that are also
not supported in setup.cfg and so can only be used in "legacy" mode.
Setuputils will raise a RuntimeError if you attempt to use it to build
setup.cfg and any keywords not supported in that mode are present.)

This release of setuputils still supports the "legacy" mode of operation,
where you include the variables setuputils needs in your setup.py file.
However, this mode of operation is deprecated and may be removed in a
future release (although it is likely that the Python packaging
ecosystem will have to continue to support such "legacy" builds for
quite a while yet). The disadvantage of this mode is that you have to
include the setuputils.py file alongside your setup.py file in your
source distribution, whereas in the new mode above you can just install
setuputils as a normal Python library on your development machine,
and only include the setup.cfg file it generates in your distribution.

Typical usage in the original mode of operation was to put all of the
information needed by setuputils in your setup.py file, thus:

    # declare variables here, for example...
    
    name = "myprog"
    
    description = "My Python Program"
    
    # other variables depending on what you need, but the autodiscovery
    # capabilities of setuputils remove the need for a lot of manual
    # declarations, or at least make them easier
    
    if __name__ == '__main__':
        from setuputils import setup_py_vars
        from setuptools import setup
        setup(**setup_py_vars(globals()))

Or, you could take more fine-grained control over things by only
invoking particular sub-functions, for example:

    if __name__ == '__main__':
        from setuptools import setup
        from setuputils import autodiscover_packages
        setup(
            name="myprog",
            description="My Python Program",
            packages=autodiscover_packages(globals()),
            # other args
        )

You could even mix the two methods, disabling general autodiscovery
but using it for particular things:
    
    from setuputils import autodiscover_packages, setup_py_vars
    
    name = "myprog"
    
    description = "My Python Program"
    
    packages = autodiscover_packages(globals())
    
    if __name__ == '__main__':
        from setuptools import setup
        setup(**setup_py_vars(globals(), autodiscover=False))

Note that you call the ``setup_py_vars`` function in this mode
(in older versions of setuputils it was just ``setup_vars``, but
that is now an internal function used in both modes).

See the docstrings of the individual functions below for more
information on the various autodiscovery capabilities of
setuputils.
"""

import os


description_content_types = {
    ".md": "text/markdown",
    ".rst": "text/x-rst",
    ".txt": "text/plain",
}


def add_long_description(varmap, basename="README"):
    """Add file reference for long description if available.
    """
    
    for filename in os.listdir("."):
        if filename.startswith(basename):
            varmap['long_description'] = "file: {}".format(filename)
            ext = os.path.splitext(filename)[-1]
            content_type = description_content_types.get(ext)
            if content_type:
                varmap['long_description_content_type'] = content_type
            return


def add_pypi_url(varmap):
    """Add the PyPI URL for program ``name`` from the setup vars.
    """
    name = varmap.get('name')
    if name:
        varmap['url'] = "http://pypi.org/project/{}".format(name)


def add_vars(varmap):
    """Automate adding ``long_description`` and ``url`` setup vars.
    """
    
    if 'long_description' not in varmap:
        add_long_description(varmap)
    if 'url' not in varmap:
        add_pypi_url(varmap)
    # provides format changed and it's not used anyway, so don't automatically include it


def add_classifier_python(varmap):
    """Automate adding the Python language classifier.
    
    Since most programs using this module will be Python
    programs, this makes it easy to ensure that the Python
    language Trove classifier is present.
    """
    
    classifiers = varmap.setdefault('classifiers', [])
    if all(not c.startswith("Programming Language ::") for c in classifiers):
        classifiers.append("Programming Language :: Python :: 3")


license_map = dict(zip("""
AFL
Apache
BSD
AGPLv3
AGPLv3+
FDL
GPL
GPLv2
GPLv2+
GPLv3
GPLv3+
LGPLv2
LGPLv2+
LGPLv3
LGPLv3+
LGPL
MIT
MPL
MPL 1.1
MPL 2.0
CNRI
PSF
QPL
""".strip().splitlines(),"""
License :: OSI Approved :: Academic Free License (AFL)
License :: OSI Approved :: Apache Software License
License :: OSI Approved :: BSD License
License :: OSI Approved :: GNU Affero General Public License v3
License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)
License :: OSI Approved :: GNU Free Documentation License (FDL)
License :: OSI Approved :: GNU General Public License (GPL)
License :: OSI Approved :: GNU General Public License v2 (GPLv2)
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)
License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)
License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)
License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
License :: OSI Approved :: MIT License
License :: OSI Approved :: Mozilla Public License 1.0 (MPL)
License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)
License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)
License :: OSI Approved :: Python License (CNRI Python License)
License :: OSI Approved :: Python Software Foundation License
License :: OSI Approved :: Qt Public License (QPL)
""".strip().splitlines()))


def add_classifier_license(varmap):
    """Convert ``license`` setup var to Trove classifier.
    
    Allows short specification of common licenses while still
    including the full Trove classifier as expected by PyPI.
    """
    
    license = varmap.get('license')
    if license:
        c = license_map.get(license)
        if c:
            varmap.setdefault('classifiers', []).append(c)
            # PyPI docs say the "License" keyword should only be used for
            # licenses that don't have a Trove classifier, but nobody
            # seems to pay attention, so we don't delete the 'license' key here
            #del varmap['license']


devstatus_trove = """
Development Status :: 3 - Alpha
Development Status :: 4 - Beta
Development Status :: 5 - Production/Stable
Development Status :: 6 - Mature
Development Status :: 7 - Inactive
Development Status :: 1 - Planning
Development Status :: 2 - Pre-Alpha
""".strip().splitlines()


def add_classifier_dev_status(varmap):
    """Convert ``dev_status`` setup var to Trove classifier.
    
    Allows short specification of development status instead
    of having to type the full Trove classifier.
    """
    
    dev_status = varmap.get('dev_status')
    if dev_status:
        for c in devstatus_trove:
            if c.endswith(dev_status):
                varmap.setdefault('classifiers', []).append(c)
                break


def add_classifiers(varmap):
    """Automate adding standard classifiers to setup vars.
    
    Also sorts the list of classifiers for neatness.
    """
    
    add_classifier_python(varmap)
    add_classifier_license(varmap)
    add_classifier_dev_status(varmap)
    classifiers = varmap.get('classifiers')
    if classifiers:
        varmap['classifiers'] = sorted(classifiers)


def package_root(varmap):
    """Return correct directory for the root package.
    
    The "root" package is the one where modules which do not
    belong to a package are located (see the distutils docs).
    This function should not need to be called directly in
    your actual setup script, but it can be useful for testing.
    Note that it looks for a ``package_root`` setup var, which
    can be used as a shortcut if your "root" package is not in
    the standard place (which is your setup script directory),
    rather than having to declare a ``package_dir`` dictionary
    with a ``''`` key.
    """
    
    try:
        return varmap['package_dir']['']
    except KeyError:
        try:
            result = varmap['package_root']
        except KeyError:
            return "."
        else:
            dirmap = varmap.setdefault('package_dir', {})
            if '' not in dirmap:
                dirmap[''] = result
            return result


def autodiscover_modules(varmap, excludes=("setup", "setuputils")):
    """Return list of Python modules in your distro.
    
    Module names listed in ``excludes`` will not be included; by
    default only ``setup.py`` and ``setuputils.py`` are excluded,
    all other ``.py`` files in your "root" package are included.
    """
    
    excludes = varmap.get('mod_excludes', excludes)
    return [
        os.path.splitext(filename)[0]
        for filename in os.listdir(package_root(varmap))
        if (os.path.splitext(filename)[1] == ".py")
        and (os.path.splitext(filename)[0] not in excludes)
    ]


def add_py_modules(varmap):
    """Automatically fill in the ``py_modules`` setup var.
    """
    
    if 'py_modules' not in varmap:
        modules = autodiscover_modules(varmap)
        if modules:
            varmap['py_modules'] = modules


def marked(filenames):
    return "__init__.py" in filenames


def dir_to_package(dirname):
    return dirname.replace(os.sep, '.')


def package_paths(varmap):
    """Return list of directories in your distro that are Python packages.
    
    This function should not need to be called directly in
    your actual setup script, but it can be useful for testing.
    It uses the "root" package, as determined from your setup
    vars, to determine where to start the search.
    
    Note that this function detects PEP 420 implicit namespace packages,
    but only for a limited set of cases: it only includes directories that
    do not have an __init__.py file but which have at least one subdirectory
    that *does* have an __init__.py file. In other words, only implicit
    namespace packages that have non-namespace packages inside them will
    be detected. The PEP 420 spec allows implicit namespace packages "all the
    way down", so to speak, with no __init__.py files anywhere, but trying
    to auto-detect this, as setuptools does, either results in many false
    positives (for example, scripts in a "scripts" directory of your source
    distribution) or requires a "src" layout where all source code is put
    inside a subdirectory of your distribution (which is fine if it works
    for you, but might not be a good fit for all projects). For cases where
    the setuptools logic works, you can use its autodetection instead of
    the method here by putting "packages = find_namespace:" in your options.in
    file instead of leaving out "packages" altogether.
    """
    
    rootdir = package_root(varmap)
    packages = []
    for dirname, subdirs, filenames in os.walk(rootdir):
        if dirname != rootdir:
            if marked(filenames) or any(marked(os.listdir(os.path.join(dirname, subdir))) for subdir in subdirs):
                packages.append(dirname.split(os.sep, 1)[1])
            else:
                # Don't recurse into subdirs in non-packages
                subdirs[:] = []
    return packages


def _translate_pkg_names(dirnames):
    # Translate directory names to package names
    return [
        dir_to_package(dirname)
        for dirname in dirnames
    ]


def autodiscover_packages(varmap):
    """Return list of Python packages in your distro.
    """
    
    return _translate_pkg_names(package_paths(varmap))


def add_packages(varmap):
    """Automatically fill in the ``packages`` setup var.
    
    Note that "legacy" namespace packages (i.e., ones that do not use the
    PEP 420 implicit namespace package feature and have an __init__.py
    file) will need to be identified manually in the "namespace_packages"
    variable in your options.in file; setuputils has no way of auto-discovering
    these. (Note that this is true of the autodiscovery mechanism in setuptools
    as well.) Any packages included in the "namespace_packages" variable will not
    be included in the "packages" variable.
    """
    
    if 'packages' not in varmap:
        packages = autodiscover_packages(varmap)
        if packages:
            namespace_packages = varmap.get('namespace_packages', ())
            packages = [p for p in packages if p not in namespace_packages]
            if packages:
                varmap['packages'] = packages


def _package_data_paths(pathname, ext_srcdir):
    # Return list of package subdirectories that are not packages
    # themselves (and are therefore presumed to contain package data).
    # Implicit namespace packages are detected and filtered out of
    # the list using the same logic as in ``package_paths`` above.
    return [
        "{}/*.*".format(subdir)
        for subdir in os.listdir(pathname)
        if (subdir != "__pycache__")
        and (subdir != ext_srcdir)
        and os.path.isdir(os.path.join(pathname, subdir))
        and not marked(os.listdir(os.path.join(pathname, subdir)))
        and all(
            not marked(os.listdir(os.path.join(pathname, subdir, subsub)))
            for subsub in os.listdir(os.path.join(pathname, subdir))
            if os.path.isdir(os.path.join(pathname, subdir, subsub))
        )
    ]


def package_to_dir(pkgname):
    return pkgname.replace('.', os.sep)


def autodiscover_package_data(varmap, ext_srcdir=""):
    """Return mapping of package data paths to file lists.
    
    The ``ext_srcdir`` argument is used to exclude package
    subdirectories (if any) that contain extension source files.
    Leaving it blank (the default) means all subdirectories of
    all packages are checked.
    """
    
    ext_srcdir = varmap.get('ext_srcdir', ext_srcdir)
    return dict(
        (pkgname, _package_data_paths(package_to_dir(pkgname), ext_srcdir))
        for pkgname in varmap.get('packages', ())
        if _package_data_paths(package_to_dir(pkgname), ext_srcdir)
    )


def add_package_data(varmap):
    """Automatically fill in the ``package_data`` setup var.
    """
    
    if 'package_data' not in varmap:
        package_data = autodiscover_package_data(varmap)
        if package_data:
            varmap['package_data'] = package_data


def autodiscover_extensions(varmap,
                            ext_srcdir="",
                            ext_exts=(".c", ".cc", ".cpp", ".i")):
    """Return list of ``Extension`` instances for your distro.
    
    Looks at the ``ext_names`` setup var for the names of
    extension modules (dotted names indicate extensions that
    live inside packages). Each extension name is converted
    to a path relative to your "root" package in which the
    extension is located.
    
    The ``ext_srcdir`` argument, if non-blank, indicates that
    extension source files are in a subdirectory of the extension
    directory (for example, the ``src`` subdirectory).
    
    The ``ext_exts`` argument gives the file extensions for source
    files (the default should work for most cases).
    
    Note that this function assumes that only one extension
    "lives" in a given directory; multiple extensions in the
    same directory can't be autodiscovered using this mechanism.
    
    Note also that builds with extension modules are currently
    not supported in setup.cfg, so setuputils will raise a
    RuntimeError if it sees any extensions in that mode.
    """
    
    extnames = varmap.get('ext_names')
    if extnames:
        from setuptools import Extension
        rootdir = package_root(varmap)
        result = []
        ext_srcdir = varmap.get('ext_srcdir', ext_srcdir)
        ext_exts = varmap.get('ext_exts', ext_exts)
        for extname in extnames:
            srcpath = os.path.join(
                rootdir,
                os.path.dirname(extname.replace('.', os.sep))
            )
            if ext_srcdir:
                srcpath = os.path.join(srcpath, ext_srcdir)
            sources = [
                "{}/{}".format(srcpath, basename)
                for basename in os.listdir(srcpath)
                if os.path.splitext(basename)[1] in ext_exts
            ]
            result.append(
                Extension(extname, sources)
            )
        return result


def add_extensions(varmap):
    """Automatically fill in the ``ext_modules`` setup var.
    """
    
    if 'ext_modules' not in varmap:
        ext_modules = autodiscover_extensions(varmap)
        if ext_modules:
            varmap['ext_modules'] = ext_modules


def autodiscover_datafiles(varmap):
    """Return list of (dist directory, data file list) 2-tuples.
    
    The ``data_dirs`` setup var is used to give a list of
    subdirectories in your source distro that contain data
    files. It is assumed that all such files will go in the
    ``share`` subdirectory of the prefix where distutils is
    installing your distro (see the distutils docs); within
    that directory, a subdirectory with the same name as
    your program (i.e., the ``name`` setup var) will be
    created, and each directory in ``data_dirs`` will be a
    subdirectory of that. So, for example, if you have example
    programs using your distro in the ``"examples"`` directory
    in your distro, you would declare ``data_dirs = "examples"``
    in your setup vars, and everything under that source
    directory would be installed into ``share/myprog/examples``.
    """
    
    datadirs = varmap.get('data_dirs')
    name = varmap.get('name')
    if datadirs and name:
        result = {}
        pathprefix = "share/{}".format(name)
        for datadir in datadirs:
            for dirname, subdirs, filenames in os.walk(datadir):
                if filenames and ("." not in dirname):
                    distdir = dirname.replace(os.sep, '/')
                    distfiles = [
                        "{}/{}".format(distdir, filename)
                        for filename in filenames
                        if not filename.startswith(".")
                    ]
                    if distfiles:
                        distdir = dirname.replace(os.sep, '/')
                        result["{}/{}".format(pathprefix, distdir)] = distfiles
        return result


def add_datafiles(varmap):
    """Automatically fill in the ``data_files`` setup var.
    """
    
    if 'data_files' not in varmap:
        data_files = autodiscover_datafiles(varmap)
        if data_files:
            varmap['data_files'] = data_files


def add_entry_points(varmap):
    """Automatically fill in the ``entry_points`` setup var.
    """
    
    if 'entry_points' not in varmap:
        entry_points = varmap.get('entry_points_file')
        if entry_points:
            varmap['entry_points'] = entry_points


def autodiscover_scripts(varmap, dirname="scripts"):
    """Return a list of scripts in your distro.
    
    The ``dirname`` argument gives the directory in your source
    distro in which to look for scripts. The ``script_dir``
    setup var can be used to customize this if for some strange
    reason you can't use the default of ``"scripts"``.
    """
    
    dirname = varmap.get('script_dir', dirname)
    if os.path.isdir(dirname):
        return [
            os.path.join(dirname, filename)
            for filename in os.listdir(dirname)
        ]
    return []


def add_scripts(varmap):
    """Automatically fill in the ``scripts`` setup var.
    """
    
    if 'scripts' not in varmap:
        scripts = autodiscover_scripts(varmap)
        if scripts:
            varmap['scripts'] = scripts


def autodiscover_all(varmap):
    """Automatically fill in all auto-discovered setup variables.
    
    Note that even if you don't use all of these variables
    (for example, your distro may have only packages and no
    py_modules, or you may have no package data, extensions,
    etc.), you can still use this function; if it finds no
    instances of a given item, there is no effect.
    """
    
    add_py_modules(varmap)
    add_packages(varmap)
    add_package_data(varmap)
    add_extensions(varmap)
    add_datafiles(varmap)
    add_entry_points(varmap)
    add_scripts(varmap)


def _add_package_data_lines(pdata, lines):
    # Distutils won't automatically include package_data
    # if we have a MANIFEST.in, so we need to include it
    # in MANIFEST.in (actually, there is supposedly a
    # fix for that that's in the head of the Python source
    # tree, but it isn't in all recent versions and
    # distutils will take care of any duplicate file
    # inclusions anyway, so it doesn't hurt to make sure
    # with the "belt and suspenders" approach here)
    for pkgname, items in pdata.items():
        pkgname = pkgname.replace('.', '/')
        for item in items:
            if '/' in item:
                dirname, filespec = item.rsplit('/', 1)
                dirname = "{}/{}".format(pkgname, dirname)
            else:
                dirname = pkgname
                filespec = item
            lines.append(
                "recursive-include {} {}\n".format(dirname, filespec)
            )


def _add_data_dirs_lines(datadirs, lines):
    # Shortcut if data_dirs was specified (in which
    # case we don't need to individually include each
    # file in data_files)
    for datadir in datadirs:
        lines.append(
            "recursive-include {} *.*\n".format(datadir)
        )


def _add_data_files_lines(datafiles, lines):
    # Distutils won't automatically include data_files
    # either if there's a MANIFEST.in (see note above)
    for _, filenames in datafiles:
        for datafile in filenames:
            lines.append(
                "include {}\n".format(datafile)
            )


def _add_scripts_lines(scripts, lines):
    # Same "belt and suspenders" strategy as for package
    # data and data files above; distutils seems to be more
    # consistent about including scripts but...
    for script in scripts:
        lines.append(
            "include {}\n".format(script)
        )


def _add_lines(varmap, key, lines):
    # Factored out for easier use in make_manifest_in
    try:
        data = varmap[key]
    except KeyError:
        return False
    else:
        globals()['_add_{}_lines'.format(key)](data, lines)
        return True


def make_manifest_in(varmap):
    """Automatically generate ``MANIFEST.in`` template.
    
    Most of this can be done automatically based on other
    setup vars, but for any items that are not covered by
    that, you can add a ``MANIFEST.in.in`` template that
    declares those items. That template will occur last in
    the generated ``MANIFEST.in`` file, so it can also be
    used, if necessary, to override any of the automatically
    generated items.
    
    Note that ``setuputils.py`` is automatically included,
    since it is assumed it should be treated the same as
    ``setup.py``.
    
    Also note that files implied by the ``package_data``,
    ``data_files`` (or ``data_dirs`` if ``data_files`` is
    not present), and ``scripts`` setup vars are also included
    in the generated ``MANIFEST.in``. The Python distutils
    are not completely consistent in including these files
    if a ``MANIFEST.in`` template is used, so we make sure
    by including them here (the distutils automatically
    ignore duplicate file specs so there is no harm done
    either way).
    """
    
    lines = ["include setuputils.py\n"]
    
    # Add lines for things that distutils doesn't always
    # add automatically (see comments in subfunctions above)
    for key in ('package_data', ('data_dirs', 'data_files'), 'scripts'):
        if isinstance(key, tuple):
            for k in key:
                if _add_lines(varmap, k, lines):
                    break
        else:
            _add_lines(varmap, key, lines)
    
    # This ensures that pyc files are left out in case the source
    # tree has them from testing
    lines.append("recursive-exclude . *.pyc\n")
    
    # Read from the in.in file last so the user can override
    # any of the above (shouldn't need to but just in case)
    try:
        with open("MANIFEST.in.in", 'rU') as f:
            in_in_lines = f.readlines()
    except IOError:
        pass
    else:
        lines.extend(in_in_lines)
    
    with open("MANIFEST.in", 'w') as f:
        f.writelines(lines)


supported_keywords = dict(
    name=str,
    version=str,
    description=str,
    long_description=str,
    long_description_content_type=str,
    author=str,
    author_email=str,
    maintainer=str,
    maintainer_email=str,
    url=str,
    download_url=str,
    project_urls=(str, list),
    include_package_data=bool,
    packages=(str, list),
    py_modules=(str, list),
    namespace_packages=(str, list),
    scripts=(str, list),
    ext_package=str,
    ext_modules=list,
    dev_status=str,  # setuputils keyword
    classifiers=(str, list),
    distclass=type,
    script_name=str,
    script_args=list,
    options=dict,
    license=str,
    license_file=str,
    license_files=(str, list),
    keywords=(str, list),
    platforms=(str, list),
    cmdclass=dict,
    data_dirs=list,  # setuputils keyword
    data_files=dict,
    package_dir=(str, list),
    package_data=dict,
    exclude_package_data=dict,
    requires=(str, list),
    provides=(str, list),
    obsoletes=(str, list),
    zip_safe=bool,
    setup_requires=(str, list),
    install_requires=(str, list),
    extras_require=dict,
    python_requires=str,
    entry_points_file=str,
    entry_points=dict,
    eager_resources=(str, list),
    dependency_links=(str, list),
    tests_require=(str, list),
    autodiscover=bool,  # setuputils keyword
    sorted_output=bool,  # setuputils keyword
    egg_base=str,
)

list_convert_keywords = tuple(
    k for k, v in supported_keywords.items() if (v is list) or (v == (str, list))
)


def convert_lists(varmap,
                  list_keys=list_convert_keywords):
    """Convert long strings to lists of strings.
    
    Allows variable names in ``list_keys`` to be specified as
    long strings instead of lists, for easier typing.
    """
    
    for key in list_keys:
        var_type = supported_keywords[key]
        var = varmap.get(key)
        if var and isinstance(var, str) and ((var_type is list) or ('\n' in var)):
            varmap[key] = var.strip().splitlines()


def setup_vars(varmap, autodiscover=True, force_manifest_in=False):
    """Return dict of setup variables from dict of input variables.
    
    The ``autodiscover`` argument determines whether arguments
    not explicitly declared in ``varmap`` will be auto-discovered
    using the sub-functions above. For many use cases this will
    be sufficient; however, if you want finer control over what
    is auto-discovered, this argument can be set to ``False``
    and the sub-functions can be used individually (or setup
    arguments can be declared by hand).
    
    The ``force_manifest_in`` argument determines whether a
    ``MANIFEST.in`` template is generated even if you do not
    have a ``MANIFEST.in.in`` template. The chief reason for
    doing this would be to ensure that ``setuputils.py`` is
    included in your distributions. However, in most cases it
    is easier to either have a ``MANIFEST.in.in`` template,
    even an empty one, or to hand-generate your own ``MANIFEST``
    file (which is rarely done since it requires you to include
    *everything* by hand). Note that if you write your own
    ``MANIFEST.in`` file (and leave ``force_manifest_in`` at
    its default), you should be aware of the Python distutils'
    inconsistency about including files implied by the
    ``package_data``, ``data_files``, and ``scripts`` setup
    arguments (see docstrings above), and you must also include
    ``setuputils.py`` yourself.
    """
    
    varmap = dict(varmap)  # so we don't mutate the original
    convert_lists(varmap)
    
    if autodiscover:
        add_vars(varmap)
        add_classifiers(varmap)
        autodiscover_all(varmap)
    
    if force_manifest_in or ((force_manifest_in is not None) and os.path.isfile("MANIFEST.in.in")):
        make_manifest_in(varmap)
    
    return dict(
        (k, v) for k, v in varmap.items()
        if k in supported_keywords
    )


def convert_file_values(varmap,
                        file_marker="file:"):
    
    file_values = {k: v for k, v in varmap.items() if isinstance(v, str) and v.startswith(file_marker)}
    if file_values:
        for key, value in file_values.items():
            filename = value[len(file_marker):].strip()
            with open(filename, 'r') as f:
                data = f.read()
            varmap[key] = data


def setup_py_vars(varmap, autodiscover=True, force_manifest_in=True):
    """Wrapper to return vars for ``setup.py`` legacy mode.
    
    In this mode ``force_manifest_in`` defaults to ``True`` since
    at a minimum we need to make sure ``setuputils.py`` is included
    with the distribution. Also we need to convert any "file:"
    values to the actual file data since that mode only works with
    setup.cfg
    """
    
    varmap = setup_vars(varmap, autodiscover=autodiscover, force_manifest_in=force_manifest_in)
    convert_file_values(varmap)
    return varmap


setup_cfg_sections = (
    ("metadata", (
        "name",
        "version",
        "description",
        "long_description",
        "long_description_content_type",
        "author",
        "author_email",
        "maintainer",
        "maintainer_email",
        "url",
        "download_url",
        "project_urls",
        "license",
        "license_files",
        "keywords",
        "classifiers",
        "platforms",
        "requires",
        "provides",
        "obsoletes",
    )),
    ("options", (
        "zip_safe",
        "setup_requires",
        "install_requires",
        "python_requires",
        "eager_resources",
        "dependency_links",
        "tests_require",
        "include_package_data",
        "packages",
        "package_dir",
        "namespace_packages",
        "py_modules",
        "entry_points",  # for file: entry_points
        "scripts",
    )),
    ("options.extras_require", ()),
    ("options.entry_points", ()),  # for section entry_points
    ("options.package_data", ()),
    ("options.exclude_package_data", ()),
    ("options.data_files", ()),
    ("egg_info", (
        "egg_base",
    )),
)

no_setup_cfg_keys = (
    "ext_package",
    "ext_modules",
    "distclass",
    "options",
    "cmdclass",
)


def read_setup_py():
    import setup
    return {attr: getattr(setup, attr) for attr in dir(setup) if not attr.startswith('_')}


def strtobool(value):
    if value.lower() in ("false", "no", "0"):
        return False
    if value.lower() in ("true", "yes", "1"):
        return True
    raise ValueError("{} is not a valid boolean".format(repr(value)))


def read_in_lines(lines,
                  sep="=", listsep=",", comparison_ops=("==", ">", "<")):
    
    in_vars = {}
    open_key = None
    open_value = None
    
    def close_open_key():
        nonlocal open_key, open_value
        if open_key:
            in_vars[open_key] = open_value
            open_key = open_value = None
    
    for line in lines:
        dangling = line.startswith(' ')
        line = line.strip()
        if not line:
            continue
        if (not dangling) and (sep in line) and all(s not in line for s in comparison_ops):
            close_open_key()
            key, value = (s.strip() for s in line.split(sep))
            if value:
                key_type = supported_keywords.get(key, type(value))
                if key_type in (list, dict):
                    raise RuntimeError("{} cannot be specified on a single line".format(key))
                elif (key_type == (str, list)) and listsep not in value:
                    raise RuntimeError("{} should be comma-separated list".format(key))
                elif key_type is bool:
                    value = strtobool(value)
                in_vars[key] = value
            else:
                open_key = key
                open_type = supported_keywords.get(key, list)
                if open_type is dict:
                    raise RuntimeError("Cannot specify extra section tables in .in file.")
                elif (open_type is not list) and (open_type != (str, list)):
                    raise RuntimeError("String values must be specified on single line in .in file.")
                if open_type == (str, list):
                    open_type = list
                open_value = open_type()
        else:
            open_value.append(line)
    close_open_key()
    return in_vars


def in_filename(section):
    return "{}.in".format(section)


def read_in_files():
    varmap = {}
    for section, _ in setup_cfg_sections:
        filename = in_filename(section)
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                lines = f.readlines()
            section_in = read_in_lines(lines)
            if "." in section:
                key = section.split(".", 1)[-1]
                varmap[key] = section_in
            else:
                varmap.update(section_in)
    return varmap


def write_section_header(lines, section):
    lines.append("[{}]\n".format(section))


def write_item_lines(lines, item, value, sorted_output=True):
    if isinstance(value, list):
        lines.append("{} =\n".format(item))
        if sorted_output:
            value.sort()
        for v in value:
            lines.append("    {}\n".format(v))
    else:
        lines.append("{} = {}\n".format(item, value))


def write_section_items(lines, item_vars, sorted_output=True):
    for item, value in item_vars.items():
        if value and not isinstance(value, dict):
            write_item_lines(lines, item, value, sorted_output=sorted_output)


def write_section_close(lines):
    lines.append("\n")


def write_out_file(cfg_vars, sorted_output=True):
    lines = []
    for section, items in setup_cfg_sections:
        if items:
            item_vars = {item: cfg_vars.get(item) for item in items}
        else:
            key = section.split(".", 1)[-1]
            item_vars = cfg_vars.get(key)
        if item_vars and isinstance(item_vars, dict):
            if sorted_output and not items:
                item_vars = {k: item_vars[k] for k in sorted(item_vars)}
            write_section_header(lines, section)
            write_section_items(lines, item_vars, sorted_output=sorted_output)
            write_section_close(lines)
    with open("setup.cfg", "w") as f:
        f.writelines(lines)


def fix_egg_base(cfg_vars, drive_letter="C"):
    # Special-case this so path separators are correct
    egg_base = cfg_vars.get('egg_base')
    if egg_base and (os.sep != '/'):
        egg_base = egg_base.replace('/', os.sep)
        if egg_base.startswith(os.sep) and (os.name == 'nt'):
            egg_base = "{}:{}".format(drive_letter, egg_base)
        cfg_vars['egg_base'] = egg_base


def write_setup_cfg(autodiscover=True, sorted_output=True):
    if os.path.isfile('setup.py'):
        varmap = read_setup_py()
        #raise RuntimeError("Cannot have setup.py file in setup.cfg mode.")
    else:
        varmap = {}
    varmap.update(read_in_files())
    autodiscover = varmap.get('autodiscover', autodiscover)
    sorted_output = varmap.get('sorted_output', sorted_output)
    cfg_vars = setup_vars(varmap, autodiscover=autodiscover, force_manifest_in=None)
    fix_egg_base(cfg_vars)
    forbidden_keys = [k for k in cfg_vars if k in no_setup_cfg_keys]
    if forbidden_keys:
        raise RuntimeError("Keys {} are not supported in setup.cfg.".format(", ".join(forbidden_keys)))
    write_out_file(cfg_vars, sorted_output=sorted_output)


if __name__ == '__main__':
    write_setup_cfg()

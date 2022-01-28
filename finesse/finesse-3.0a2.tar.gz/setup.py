"""Setup file.

This file only contains the setup inforamtion for building Cython extensions. Everything
else is (and should be) in `setup.cfg`. Eventually it should be possible to get rid of
`setup.py` and make the build system entirely declarative (see #367).
"""

import os
import sys
import platform
from pathlib import Path
from setuptools import setup
from Cython.Build import build_ext, cythonize
from Cython.Distutils import Extension

SYS_NAME = platform.system()
NUM_JOBS = int(os.getenv("CPU_COUNT", os.cpu_count()))


def get_conda_paths():
    try:
        library = sys.prefix
        # library = os.environ["CONDA_PREFIX"]
        if sys.platform == "win32":
            library = os.path.join(library, "Library")
        return os.path.join(library, "include"), os.path.join(library, "lib")
    except KeyError:
        return None, None


class finesse_build_ext(build_ext):
    def initialize_options(self):
        super().initialize_options()
        # default to parallel build
        self.parallel = NUM_JOBS


def make_extension(relpath, **kwargs):
    import numpy as np

    here = Path(__file__).parent.absolute()
    src_dir = Path("src")
    finesse_dir = src_dir / "finesse"

    def construct_ext_name(rp):
        names = []
        leading, trailing = os.path.split(rp)

        while trailing != "":
            names.append(trailing)

            leading, trailing = os.path.split(leading)

        names.reverse()
        if names[-1].endswith(".pyx"):
            names[-1] = names[-1].split(".")[0]

        return ".".join(names)

    # The optional arguments consisting of various directories,
    # macros, compilation args, etc. that will be passed to
    # Extension object constructor
    ext_args = {
        "include_dirs": [],
        "define_macros": [],
        "undef_macros": [],
        "library_dirs": [],
        "libraries": [],
        "runtime_library_dirs": [],
        "extra_objects": [],
        "extra_compile_args": [],
        "extra_link_args": [],
        "export_symbols": [],
        "cython_include_dirs": [],
        "cython_directives": [],
    }
    ### Setting up some global options that need to be passed ###
    ###                   to all extensions                   ###

    include_dirs = ext_args.get("include_dirs")
    # Include the src/finesse and NumPy header file directories
    include_dirs.extend([str(here / finesse_dir), np.get_include()])

    # Now ensure suitesparse headers get included
    USR_SUITESPARSE_PATH = "/usr/include/suitesparse"
    if os.path.exists(USR_SUITESPARSE_PATH):
        include_dirs.append(USR_SUITESPARSE_PATH)

    # Grab the paths to suitesparse from conda if using this
    conda_include, conda_lib = get_conda_paths()
    if conda_include is not None:
        CONDA_SUITESPARSE_PATH = os.path.join(conda_include, "suitesparse")
        if os.path.exists(CONDA_SUITESPARSE_PATH):
            include_dirs.append(CONDA_SUITESPARSE_PATH)

        include_dirs.append(conda_include)
        ext_args.get("library_dirs").append(conda_lib)

    # define_macros = ext_args.get("define_macros")
    # define_macros.extend(
    #     [
    #         # Stops numpy version warning, cython uses an older API on purpose
    #         ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
    #     ]
    # )

    extra_compile_args = ext_args.get("extra_compile_args")
    extra_compile_args.extend(
        [
            "-O3",
            # Inlined cpdef functions in finesse.cymath extensions complain
            # about not being used (they are used outside of these extensions)
            # so we suppress these warnings for the moment
            "-Wno-unused-function",
            "-Wno-unused-variable",
            # "-DCYTHON_WITHOUT_ASSERTIONS",
        ]
    )

    ### Now adding the optional extra args needed for this specific extension ###

    for arg_opt, arg_list in ext_args.items():
        extra_args = kwargs.get(arg_opt)
        if extra_args:
            if isinstance(extra_args, str):
                extra_args = [extra_args]

            arg_list += extra_args

    ext_name = "finesse." + construct_ext_name(relpath)
    sources = [str(finesse_dir / relpath)]

    return Extension(
        ext_name,
        sources,
        language="c",
        **ext_args,
    )


def ext_modules():
    # Argument pattern for extensions requiring OpenMP
    if SYS_NAME == "Darwin":
        open_mp_args = {
            "extra_compile_args": ["-Xpreprocessor", "-fopenmp"],
            "extra_link_args": ["-liomp5"],
        }
    else:
        open_mp_args = {"extra_compile_args": "-fopenmp", "extra_link_args": "-fopenmp"}

    # Argument pattern for extensions using KLU
    cmatrix_args = {"libraries": "klu"}

    # The argument patterns that get passed to all extensions
    default_ext_args = {}

    # See https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives
    # for in-depth details on the options for compiler directives
    compiler_directives = {
        # Embeds call signature in docstring of Python visible functions
        "embedsignature": True,
        # No checks are performed on division by zero (for big perfomance boost)
        "cdivision": True,
    }

    if os.environ.get("CYTHON_COVERAGE", False):
        # If we're in coverage report mode, then add the trace
        # macros to all extensions so that proper line tracing
        # is performed
        default_ext_args["define_macros"] = [
            ("CYTHON_TRACE", "1"),
            ("CYTHON_TRACE_NOGIL", "1"),
        ]

        # Ensure line tracing is switched on for all extensions.
        compiler_directives["linetrace"] = True

    # If debug mode is set then ensure profiling
    # is switched on for all extensions
    if os.environ.get("CYTHON_DEBUG", False):
        compiler_directives["profile"] = True

    # NOTE (sjr) Pass any extra arguments that a specific extension needs via a
    #            dict of the arg names: values here. See ext_args in make_extension
    #            function above for the options.
    ext_args = [
        ("enums.pyx", default_ext_args),
        ("cymath/*.pyx", {**default_ext_args, **open_mp_args}),
        ("thermal/*.pyx", default_ext_args),
        ("tree.pyx", default_ext_args),
        ("materials.pyx", default_ext_args),
        ("constants.pyx", default_ext_args),
        ("frequency.pyx", default_ext_args),
        ("symbols.pyx", default_ext_args),
        ("parameter.pyx", default_ext_args),
        ("cyexpr.pyx", default_ext_args),
        ("element.pyx", default_ext_args),
        ("cmatrix.pyx", {**default_ext_args, **cmatrix_args}),
        ("knm/*.pyx", {**default_ext_args, **open_mp_args}),
        ("simulations/base.pyx", default_ext_args),
        ("simulations/basematrix.pyx", default_ext_args),
        ("simulations/KLU.pyx", default_ext_args),
        ("components/workspace.pyx", default_ext_args),
        ("components/mechanical.pyx", default_ext_args),
        ("components/modal/*.pyx", default_ext_args),
        ("detectors/workspace.pyx", default_ext_args),
        ("detectors/compute/amplitude.pyx", default_ext_args),
        ("detectors/compute/camera.pyx", {**default_ext_args, **open_mp_args}),
        ("detectors/compute/power.pyx", {**default_ext_args, **open_mp_args}),
        ("detectors/compute/quantum.pyx", default_ext_args),
        ("detectors/compute/gaussian.pyx", default_ext_args),
        ("tracing/*.pyx", default_ext_args),
        ("analysis/runners.pyx", default_ext_args),
        ("solutions/base.pyx", default_ext_args),
        ("solutions/array.pyx", default_ext_args),
        ("utilities/cyomp.pyx", {**default_ext_args, **open_mp_args}),
    ]

    exts = []
    for ext_rel_path, args in ext_args:
        exts.append(make_extension(os.path.normpath(ext_rel_path), **args))

    return cythonize(
        exts,
        # Produces HTML files showing level of CPython interaction
        # per-line of each Cython extension (.pyx) file
        annotate=True,
        language_level=3,
        nthreads=NUM_JOBS,
        compiler_directives=compiler_directives,
        gdb_debug=True,
    )


if __name__ == "__main__":
    setup(
        ext_modules=ext_modules(),
        cmdclass={"build_ext": finesse_build_ext},
        use_scm_version=True,
        setup_requires=["setuptools_scm"],
    )

import os
from distutils.sysconfig import get_python_inc
from setuptools import setup, Extension


def src_folder():
    candidates = ['cxx/src/', 'clease/', './']
    for c in candidates:
        if os.path.exists(c + 'cluster.cpp'):
            return c
    raise RuntimeError("Cannot find source folder.")


def get_cython_folder():
    candidates = ['cxx/cython/', 'cython/', './']
    for c in candidates:
        if os.path.exists(c + 'clease_cxx.pyx'):
            return c
    raise RuntimeError("Cannot find cython folder")


def include_folder():
    candidates = ['cxx/include/', 'clease/', './']
    for c in candidates:
        if os.path.exists(c + 'cluster.hpp'):
            return c
    raise RuntimeError("Cannot find include folder")


def get_npy_include_folder():
    import numpy as np
    return np.get_include()


def build_ext(ext_module):
    from Cython.Build import cythonize
    return cythonize(ext_module, compiler_directives={"language_level": "3"})


cxx_src_folder = src_folder()
cxx_inc_folder = include_folder()
cython_folder = get_cython_folder()

src_files = [
    'cf_history_tracker.cpp',
    'additional_tools.cpp',
    'cluster.cpp',
    'row_sparse_struct_matrix.cpp',
    'named_array.cpp',
    'symbols_with_numbers.cpp',
    'basis_function.cpp',
    'cluster_list.cpp',
    'atoms.cpp',
]

src_files = [cxx_src_folder + x for x in src_files]
src_files.append(cython_folder + 'clease_cxx.pyx')
extra_comp_args = ['-std=c++11']

clease_cxx = Extension("clease_cxx",
                       sources=src_files,
                       include_dirs=[
                           cxx_inc_folder,
                           get_npy_include_folder(), cxx_src_folder,
                           get_python_inc(), cython_folder
                       ],
                       extra_compile_args=extra_comp_args,
                       language="c++")

# Extra packages required with certain aspects of CLEASE, which are not required
# to run the base CLEASE package.
EXTRAS_REQUIRE = {
    # For building the documentation
    'doc': ('sphinx', 'sphinx_rtd_theme'),
    # For running the CLEASE test suite
    'test': (
        'pytest',
        'pytest-mock',
        'mock',
        # Get the histrogram extras, for making nice histogram plots
        # with pytest-benchmark
        'pytest-benchmark[histogram]>=3.4.1',
        'tox>=3.24.0',
    ),
    # Extra nice-to-haves when developing CLEASE
    'dev': (
        'pip',
        'cython',
        'pre-commit',
        'ipython',
        'twine',
        'yapf',
        'pylint',
        'pyclean>=2.0.0',  # For removing __pycache__ and .pyc files
        'pytest-cov',
        'build',
    ),
    'gui': ('clease-gui',),
}
# Make an entry which installs all of the above in one go
# Separate out "gui" from "all"
EXTRAS_REQUIRE['all'] = tuple(
    {package for key, tup in EXTRAS_REQUIRE.items() for package in tup if key != 'gui'})

setup(
    ext_modules=build_ext(clease_cxx),
    extras_require=EXTRAS_REQUIRE,
)

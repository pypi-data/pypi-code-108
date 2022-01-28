from setuptools import Extension, setup
import numpy

try:
    from Cython.Build import cythonize

    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

if USE_CYTHON:
    ext_modules = cythonize(
        [
            Extension(
                "squish.core",
                ["squish/core.pyx"],
                define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
            ),
            Extension(
                "squish.voronoi",
                ["squish/voronoi.pyx"],
                extra_compile_args=["-fopenmp"],
                extra_link_args=["-fopenmp"],
                define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
            ),
            Extension(
                "squish.energy",
                ["squish/energy.pyx"],
                extra_compile_args=["-fopenmp"],
                extra_link_args=["-fopenmp"],
                define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
            ),
        ],
        annotate=False,
        compiler_directives={
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
        },
    )
else:
    ext_modules = [
        Extension(
            "squish.core",
            ["squish/core.c"],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
        Extension(
            "squish.voronoi",
            ["squish/voronoi.c"],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
        Extension(
            "squish.energy",
            ["squish/energy.c"],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
    ]

setup(ext_modules=ext_modules, include_dirs=[numpy.get_include()])

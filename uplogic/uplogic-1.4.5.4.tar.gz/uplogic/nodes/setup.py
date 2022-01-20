# Commandline: python setup.py build_ext --inplace
# execute this line in the setup.py directory

# from setuptools import setup
# from Cython.Build import cythonize

# setup(
#     ext_modules=cythonize("__init__.py")
# )

from distutils.core import setup
from distutils.extension import Extension

from Cython.Distutils import build_ext
setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=[
        Extension(
            "nodes",
            ["./../nodes.pyx"]
        )
    ]
)

import os
from setuptools import setup, Extension, find_packages

def my_build_ext(pars):
    # import delayed:
    from setuptools.command.build_ext import build_ext as _build_ext
    class build_ext(_build_ext):
        def finalize_options(self):
            # got error `'dict' object has no attribute '__NUMPY_SETUP__'`
            def _set_builtin(name, value):
                if isinstance(__builtins__, dict):
                    __builtins__[name] = value
                else:
                    setattr(__builtins__, name, value)
            _build_ext.finalize_options(self)
            # Prevent numpy from thinking it is still in its setup process:
            _set_builtin('__NUMPY_SETUP__', False)
            import numpy
            self.include_dirs.append(numpy.get_include())
    #object returned:
    return build_ext(pars)

here = os.path.abspath(os.path.dirname(__file__))
# Get the long description from the README file
with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

if os.name == 'nt':
    extra_compile_args = ["-Ox"]
else:
    extra_compile_args = ['-std=c++0x', '-pthread', '-O3']

array_wrappers_ext = Extension('sparse_dot_topn.array_wrappers',
                         sources=[
                                    './sparse_dot_topn/array_wrappers.pyx',
                                ],
                         extra_compile_args=extra_compile_args,
                         language='c++')

original_ext = Extension('sparse_dot_topn.sparse_dot_topn',
                         sources=[
                                    './sparse_dot_topn/sparse_dot_topn.pyx',
                                    './sparse_dot_topn/sparse_dot_topn_source.cpp'
                                ],
                         extra_compile_args=extra_compile_args,
                         language='c++')

threaded_ext = Extension('sparse_dot_topn.sparse_dot_topn_threaded',
                         sources=[
                             './sparse_dot_topn/sparse_dot_topn_threaded.pyx',
                             './sparse_dot_topn/sparse_dot_topn_source.cpp',
                             './sparse_dot_topn/sparse_dot_topn_parallel.cpp'],
                         extra_compile_args=extra_compile_args,
                         language='c++')

VERSION = '0.0.1'
DESCRIPTION = 'compute the cosinus similarity comparison between 2 columns of a sparse matrix very fast and selecting only the top-n best scores with a threshold'

# Setting up
setup(
    name="cosim_comparison_sparse_matrix",
    version="0.0.1",
    author="camillebrl (Camille Barboule)",
    author_email="camille.barboule@gmail.com",
    description="compute the cosinus similarity comparison between 2 columns of a sparse matrix very fast and selecting only the top-n best scores with a threshold",
    long_description_content_type="text/markdown",
    setup_requires=[
        # Setuptools 18.0 properly handles Cython extensions.
        'setuptools>=42',
        'cython>=0.29.15',
        'numpy>=1.16.6', # select this version for Py2/3 compatible
        'scipy>=1.2.3'   # select this version for Py2/3 compatible
    ],
    install_requires=[
        # Setuptools 18.0 properly handles Cython extensions.
        'setuptools>=42',
        'cython>=0.29.15',
        'numpy>=1.16.6', # select this version for Py2/3 compatible
        'scipy>=1.2.3'   # select this version for Py2/3 compatible
    ],
    zip_safe=False,
    packages=find_packages(),
    cmdclass={'build_ext': my_build_ext},
    ext_modules=[array_wrappers_ext, original_ext, threaded_ext],
    package_data = {
        'cosim_comparison_spase_matrix': ['./cosim_comparison_spase_matrix/*.pxd']
    },
    include_package_data=True,
)
from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize
from os import path

extra_compile_args = ['-D CONFIG_CTRL_IFACE', '-D CONFIG_CTRL_IFACE_UNIX']

ext_modules = [
    Extension(
        name="Cpywpa.ccore._cpywpa_core",
        sources=["./Cpywpa/ccore/_cpywpa_core.pyx"],
        extra_compile_args=extra_compile_args
    )
]

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README_PYPI.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="Cpywpa",
    version='1.0.1',
    description='Cpywpa is another simple tools to control wpa_supplicant. It use Cython to interact with OFFICIAL C '
                'interface',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Syize',
    author_email='syizeliu@gmail.com',
    platforms='Linux',
    packages=find_packages(where='.', exclude=(), include=('*',)),
    install_requires=['Cython', 'setuptools', 'wheel'],
    ext_modules=cythonize(ext_modules),
    include_package_data=True
)

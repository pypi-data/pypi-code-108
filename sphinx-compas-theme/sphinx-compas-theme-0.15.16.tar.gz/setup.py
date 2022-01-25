import io
import os

from setuptools import setup
from setuptools import find_packages

from sphinx_compas_theme import __version__


# Don't copy Mac OS X resource forks on tar/gzip.
os.environ['COPYFILE_DISABLE'] = "true"

MOD_NAME = "sphinx_compas_theme"
PKGS = [x for x in find_packages() if x.split('.')[0] == MOD_NAME]

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*names, **kwargs):
    return io.open(
        os.path.join(HERE, *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


description = read("README.md")
requirements = read('requirements.txt').split('\n')


setup(
    name="sphinx-compas-theme",
    version=__version__,
    description="Sphinx Theme for COMPAS.",
    long_description=description,
    long_description_content_type='text/markdown',
    url="https://github.com/compas-dev/sphinx_compas_theme",
    author='Tom Van Mele',
    author_email='van.mele@arch.ethz.ch',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    install_requires=requirements,
    python_requires='>=3.6',
    entry_points={
        'sphinx.html_themes': [
            'compas = sphinx_compas_theme',
            'compaspkg = sphinx_compas_theme',
        ]
    },
    packages=PKGS,
    include_package_data=True,
)

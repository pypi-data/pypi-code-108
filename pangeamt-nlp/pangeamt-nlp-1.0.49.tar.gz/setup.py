from setuptools import setup
import sys

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name='pangeamt-nlp',
    scripts=[
        'pangeamt_nlp/bin/debug_normalizers.py'
    ],
    setup_requires="setupmeta",
    author='Pangeamt',
    include_package_data=True
)

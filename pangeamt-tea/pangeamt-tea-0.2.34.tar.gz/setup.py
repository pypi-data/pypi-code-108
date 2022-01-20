from setuptools import setup
import sys

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name='pangeamt-tea',
    setup_requires="setupmeta",
    python_requires='>=3.7',
    author='Pangeamt',
    entry_points={"console_scripts": [
        "tea=pangeamt_tea.console_scripts.tea:main",
        "tea_test=pangeamt_tea.console_scripts.tea_test:main"
    ]},
    scripts=["bin/seeded_shuffle.sh"],
    test_suite="tests",
)

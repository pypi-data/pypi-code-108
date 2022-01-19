import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

    def find_packages(where='.'):
        # os.walk -> list[(dirname, list[subdirs], list[files])]
        return [folder.replace("/", ".").lstrip(".")
                for (folder, _, fils) in os.walk(where)
                if "__init__.py" in fils]

import builtins

builtins.__SETUP__ = True

import dstk

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [
    "joblib",
    "numpy",
    "scikit-learn",
    "pandas",
    "intel-openmp!=2019.5",
    "tqdm"
]

setup(
    name="dstk_x250",
    version=dstk.__version__,
    platforms=["any"],
    packages=["dstk"]+[f"dstk.{ii}" for ii in find_packages("dstk")],
    url="https://gitlab.com/Kirire/x250",
    python_requires=">=3.5",
    include_package_data = True,
    license="Apache Software License 2.0",
    author="Cyrile Delestre",
    author_email="cyrile.ufr.orsay@gmail.com",
    description="Package d'utilitaires pour les projets de data science.",
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    test_suite="tests",
    tests_require=["pytest"],
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    zip_safe=False
)


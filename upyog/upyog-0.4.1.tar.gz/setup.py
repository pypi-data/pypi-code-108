from setuptools import setup

if __name__ == "__main__":
    setup()

"""
How to upload to PyPI

python setup.py sdist bdist_wheel
twine check dist/*
twine upload --repository pypi dist/*
https://packaging.python.org/tutorials/packaging-projects/
"""

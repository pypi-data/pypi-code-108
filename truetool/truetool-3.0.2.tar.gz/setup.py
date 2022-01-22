from setuptools import setup, find_packages
from os.path import abspath, dirname, join

# Fetches the content from README.md
# This will be used for the "long_description" field.
README_MD = open(join(dirname(abspath(__file__)), "README.md")).read()

setup(
    name="truetool",
    version="3.0.2",

    # The packages that constitute your project.
    # For my project, I have only one - "pydash".
    # Either you could write the name of the package, or
    # alternatively use setuptools.findpackages()
    #
    # If you only have one file, instead of a package,
    # you can instead use the py_modules field instead.
    # EITHER py_modules OR packages should be present.
    packages=find_packages(),
    
    entry_points = {
        'console_scripts': ['truetool=truetool.command_line:main'],
    },

    # The description that will be shown on PyPI.
    # Keep it short and concise
    # This field is OPTIONAL
    description="An easy utility to managed frequently used TrueNAS SCALE CLI features",

    # The content that will be shown on your project page.
    # In this case, we're displaying whatever is there in our README.md file
    # This field is OPTIONAL
    long_description=README_MD,

    # Now, we'll tell PyPI what language our README file is in.
    # In my case it is in Markdown, so I'll write "text/markdown"
    # Some people use reStructuredText instead, so you should write "text/x-rst"
    # If your README is just a text file, you have to write "text/plain"
    # This field is OPTIONAL
    long_description_content_type="text/markdown",

    # The url field should contain a link to a git repository, the project's website
    # or the project's documentation. I'll leave a link to this project's Github repository.
    # This field is OPTIONAL
    url="https://github.com/truecharts/truetool",

    # The author name and email fields are self explanatory.
    # These fields are OPTIONAL
    author_name="truecharts",
    author_email="into@truecharts.org",

    # For additional fields, check:
    # https://github.com/pypa/sampleproject/blob/master/setup.py
)

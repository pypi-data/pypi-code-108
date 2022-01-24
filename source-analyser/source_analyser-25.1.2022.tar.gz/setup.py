from setuptools import setup, find_packages
import sys, os, source_analyser


if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

sys.path.append(os.path.realpath(os.path.dirname(__file__)))



DESCRIPTION = 'Use to Analyse some oppies... for a specific use only!'
LONG_DESCRIPTION = 'can be used to create scripts for pipelines and analyse entire sources in an oppy'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="source_analyser", 
        version=source_analyser.__VERSION__,
        author="Abdul Salam",
        author_email="abdulsalamone@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            "json_minify==0.3.0",
            "boto3==1.15.0",
            "sql_metadata==0.4.1"
        ],
        keywords=['python', "expedia", "source analyser"],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Operating System :: OS Independent",
        ]
)
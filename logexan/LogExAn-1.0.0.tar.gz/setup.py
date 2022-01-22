from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="LogExAn",
    version="1.0.0",
    description="Logical Expression Analysis",
    py_modules=["LogExAn/LogicalAnalyser"],
    package_dir={"": "SRCS"},
    packages=['LogExAn','LogExAn/Grammer'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/Palani-SN/LogExAn",
    author="Palani-SN",
    author_email="psn396@gmail.com",

    install_requires = [
        "blessings ~= 1.7",
        "lark >= 1.0.0",
        "pandas>=1.3.3",
        "tabulate>=0.8.9",
    ],

    extras_require = {
        "dev": [
            "pytest >= 3.7",
            "check-manifest",
            "twine",
        ],
    },
)

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="clipboard_monitor",
    version="1.0.1",
    description="Monitor Clipboard changes and trigger related actions",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cylin2000/clipboard_monitor/",
    author="Calvin Cai",
    author_email="cylin2000@163.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["src"],
    include_package_data=True,
    install_requires=["pillow"],
    entry_points={
    },
)
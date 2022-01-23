"""
signal-cli-dbus-rest-api
"""

from pathlib import Path
from setuptools import setup, find_packages

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="signal-cli-dbus-rest-api",
    author="Stefan Heitmüller",
    author_email="stefan.heitmueller@gmx.com",
    license="MIT",
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='~=3.7',
    packages=find_packages(),
    version="22.1.23.1",
    install_requires=[
        "sanic==21.12.1",
        "sanic-ext==22.1.2",
        "python-magic==0.4.24",
        "pydbus==0.6.0",
    ],
    entry_points={
        "console_scripts": ["signal-cli-dbus-rest-api=signal_cli_dbus_rest_api:run"],
    }
)

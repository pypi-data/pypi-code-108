"""Package up cidc_api/models.py for use in other services."""

from setuptools import setup

with open("requirements.modules.txt") as f:
    requirements = f.read().splitlines()

from cidc_api import __version__

setup(
    name="cidc_api_modules",
    description="SQLAlchemy data models and configuration tools used in the CIDC API",
    python_requires=">=3.6",
    install_requires=requirements,
    license="MIT license",
    packages=[
        "cidc_api.config",
        "cidc_api.csms",
        "cidc_api.models",
        "cidc_api.shared",
        "cidc_api.models.files",
        "cidc_api.models.templates",
    ],
    url="https://github.com/CIMAC-CIDC/cidc_api-gae",
    version=__version__,
    zip_safe=False,
)

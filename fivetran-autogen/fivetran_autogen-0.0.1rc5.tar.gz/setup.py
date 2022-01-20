from pathlib import Path
from setuptools import setup
from autogen import __version__

here = Path(__file__).parent.resolve()

with (here / "README.md").open(encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="fivetran_autogen",
    version=__version__,
    py_modules=["fivetran_autogen"],
    packages=["autogen", "autogen.packages"],
    include_package_data=True,
    entry_points={"console_scripts": ["fivetran_autogen = autogen.cli:main"]},
    author="Fivetran",
    author_email="hello@fivetran.com",
    url="https://github.com/fivetran/dbt_autogen",
    install_requires=[
        "click",
        "ruamel.yaml",
        "PyYAML",
        "google-cloud-bigquery",
        "requests",
        "snowflake-sqlalchemy",
        "sqlalchemy-bigquery",
        "sqlalchemy",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)

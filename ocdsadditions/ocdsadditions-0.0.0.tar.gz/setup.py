from setuptools import find_packages, setup

setup(
    name="ocdsadditions",
    version="0.0.0",
    author="Open Data Services",
    author_email="code@opendataservices.coop",
    url="https://github.com/OpenDataServices/ocds-additions",
    project_urls={
        "Documentation": "https://ocds-additions.readthedocs.io/en/latest/",
        "Issues": "https://github.com/OpenDataServices/ocds-additions/issues",
        "Source": "https://github.com/OpenDataServices/ocds-additions",
    },
    description="",
    license="TODO",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "ocdsadditions": [
            "templates/*.html",
            "templates/*/*.html",
            "templates/*/*/*.html",
        ]
    },
    include_package_data=True,
    install_requires=[
        "ocdskit>1.0,<=1.1",
        "click>8,<9",
        "requests",
        "python-dateutil",
        "Jinja2",
    ],
    extras_require={
        "dev": ["pytest", "black", "isort", "flake8", "mypy"],
    },
    classifiers=[],
    entry_points={
        "console_scripts": [
            "ocdsadditions = ocdsadditions.cli.main:cli",
            "ocdsadditionsinit = ocdsadditions.cli.init:cli",
        ],
    },
)

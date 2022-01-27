from setuptools import find_packages, setup

setup(
    name="ocdsmetricsanalysis",
    version="0.0.0",
    author="Open Data Services",
    author_email="code@opendataservices.coop",
    url="https://github.com/OpenDataServices/ocds-metrics-analysis",
    project_urls={
        "Documentation": "https://ocds-metrics-analysis.readthedocs.io/en/latest/",
        "Issues": "https://github.com/OpenDataServices/ocds-metrics-analysis/issues",
        "Source": "https://github.com/OpenDataServices/ocds-metrics-analysis",
    },
    description="",
    license="TODO",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[],
    extras_require={
        "dev": ["pytest", "black", "isort", "flake8", "mypy"],
    },
    classifiers=[],
)

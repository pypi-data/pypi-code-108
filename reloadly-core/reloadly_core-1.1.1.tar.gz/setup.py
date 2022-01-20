from setuptools import setup, find_namespace_packages

setup(
    name="reloadly_core",
    version="1.1.1",
    author="Reloadly Inc.",
    author_email="developers@reloadly.com",
    description="The Core for all Reloadly Python libraries",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/Reloadly/reloadly-sdk-python",
    license="MIT",
    packages=find_namespace_packages(include=['reloadly_core.*']),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires = [
        'email-validator',
        'requests',
        'jwt',
        'opentelemetry-launcher',
        'requests',
        'certifi',
    ],
    zip_safe=False
)
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="objectextensions",
    packages=[
        "objectextensions"
    ],
    version="1.1.0",
    license="MIT",
    description="A basic framework for implementing an extension pattern",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="immijimmi",
    author_email="imranhamid99@msn.com",
    url="https://github.com/immijimmi/objectextensions",
    download_url="https://github.com/immijimmi/objectextensions/archive/refs/tags/v1.1.0.tar.gz",
    keywords=["extensions", "plugins"],
    install_requires=[
        "wrapt~=1.11.2"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
)

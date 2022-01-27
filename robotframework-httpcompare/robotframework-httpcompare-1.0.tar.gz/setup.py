import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="robotframework-httpcompare",
    version="1.0",
    author="Deepak Chourasia",
    author_email="deepak.chourasia@gmail.com",
    description="A generic library to compare two HTTP Requests using Robot Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dchourasia/httpCompare",
    project_urls={
        "Bug Tracker": "https://github.com/dchourasia/httpCompare",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Software Development :: Testing",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Robot Framework",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prototools",
    version="0.1.20",
    url="https://proto-tools.github.io/docs/",
    project_urls={
        "Bug Tracker": "https://github.com/proto-tools/docs/issues",
    },
    license="MIT",
    author="Miguel Kanashiro",
    author_email="leugimkm@systrien.com",
    description="console toolbox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requieres=">=3.7",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        'Intended Audience :: Developers',
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
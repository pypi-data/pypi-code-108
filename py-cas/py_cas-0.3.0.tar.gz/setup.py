import setuptools
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

# setuptools.setup(
#     name="py_cas",
#     version="0.0.1",
#     author="includeamin",
#     author_email="includeamin@gmail.com",
#     description="python client of c.a.s",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/includeamin/c.a.s",
#     packages=setuptools.find_packages(),
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#     ],
#     python_requires='>=3.6'
#
# )
setup_args = dict(
    name="py_cas",
    version="0.3.0",
    author="includeamin",
    author_email="includeamin@gmail.com",
    description="python client of c.a.s",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
install_requires = [
    "requests>=2.24.0",
    "pydantic>=1.6.1",
    "certifi>=2017.4.17",
    "pyjwt>=1.7.1",
]
if __name__ == "__main__":
    setup(**setup_args, install_requires=install_requires)

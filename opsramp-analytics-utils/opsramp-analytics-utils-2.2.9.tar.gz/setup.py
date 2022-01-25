import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


def read_req_file(req_type):
    with open("requires-{}.txt".format(req_type)) as fp:
        requires = (line.strip() for line in fp)
        return [req for req in requires if req and not req.startswith("#")]


setuptools.setup(
    name="opsramp-analytics-utils",
    version="2.2.9",
    author="Donald Lafranchi",
    author_email="it.corridor051@gmail.com",
    description="OpsRamp Analytics SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=read_req_file("install"),
    url="https://github.com/opsramp/analytics-sdk",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

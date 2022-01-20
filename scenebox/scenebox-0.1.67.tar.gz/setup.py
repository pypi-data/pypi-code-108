"""
To create a whl file run python3 setup.py sdist bdist_wheel in scenebox_clients_packaging directory
The whl file (scenebox-0.0.1-py3-none-any.whl) can be used to run the test in helper.py
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as file:
    INSTALL_REQS = file.read().split("\n")

with open('../BASE_VERSION') as version_file:
    version = version_file.readline()

print(INSTALL_REQS)
setuptools.setup(
    name="scenebox",
    version=version,
    author="Caliber Data labs",
    author_email="yaser@caliberdatalabs.ai",
    description="Caliber Data Labs Clients package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    package_data={'': ['BASE_VERSION']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=INSTALL_REQS
)
import setuptools
import os

def get_deps()-> list:
    thelibFolder = os.path.dirname(os.path.realpath(__file__))
    requirementPath = thelibFolder + '/requirements.txt'
    install_requires = [] # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
    if os.path.isfile(requirementPath):
        with open(requirementPath) as f:
            install_requires = f.read().splitlines()

    return install_requires


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DecenTT",
    version="0.0.6",
    author="Amey Mahadik",
    author_email="ameyarm@gmail.com",
    description="Decentralized Telemetry Transport (DecenTT)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saapo-ka-baadshah/DecenTT",
    project_urls={
        "Bug Tracker": "https://github.com/saapo-ka-baadshah/DecenTT/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)

from setuptools import setup

DESCRIPTION = """
minio like python Local File System based Object Storage (FSOS)
""".strip()

DEPENDENCIES = []

TEST_DEPENDENCIES = []

VERSION = "0.0.1"
URL = "https://github.com/davinnovation/fsos"

setup(
    name="fsos",
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    packages=["fsos"],
    install_requires=DEPENDENCIES,
    test_requires=TEST_DEPENDENCIES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)

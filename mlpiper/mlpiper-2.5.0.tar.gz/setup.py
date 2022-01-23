from setuptools import setup, find_packages
import os

from mlpiper import project_name, version, jars_folder

# The directory containing this file
ROOT = os.path.dirname(os.path.abspath(__file__))

# The text of the README file
README = open(ROOT + "/README.md").read()

MLPIPER_JAR_FILE = "mlpiper.jar"
MLPIPER_JAR_FILE_PATH = os.path.join("lib", MLPIPER_JAR_FILE)


def read_requirements(fname):
    requirements = []
    with open(fname, "r") as f:
        for req in f:
            req = req.strip()
            if req and not req.startswith("#"):
                requirements.append(req)
    return requirements


install_requires = read_requirements(os.path.join(ROOT, "requirements.txt"))

extras_require = {
    "sagemaker": [
        'numpy==1.14.6;python_version<"3.4"',
        'scipy==1.1.0;python_version<"3.4"',
        "sagemaker",
        "pytz",
    ],
    # Note: 'pypsi' package will be installed only for Python >=3.4, because
    # of compatibilities issues with Python 2
    "wizard": ['pypsi;python_version>="3.4"'],
    "pyspark": ['pyspark'],
    "uwsgi": ['uwsgi']
}

setup(
    name=project_name,
    version=version,
    description="An engine for running component based ML pipelines",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/datarobot/mlpiper",
    author="DataRobot",
    author_email="info@datarobot.com",
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Unix",
    ],
    zip_safe=False,
    include_package_data=True,
    package_data={"": ["*.json", "*.jar", "*.egg", jars_folder + "/*.jar"]},
    packages=find_packages(".", exclude=["tests"]),
    scripts=[
        "bin/mlpiper",
        "bin/mcenter_components_setup.py",
        "bin/create-egg.sh",
        "bin/cleanup.sh",
    ],
    extras_require=extras_require,
    install_requires=install_requires,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    entry_points={"setuptools.installation": ["eggsecutable = mlpiper.cli.main:main"]},
)

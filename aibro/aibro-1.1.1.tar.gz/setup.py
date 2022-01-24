import fnmatch
import os

from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py as build_py_orig


excluded = [
    "aibro/data_operation.py",
    "aibro/model.py",
    "aibro/offline_pickup.py",
    "aibro/training_data.py",
    "tests/*",
]


class build_py(build_py_orig):
    """
    Used to exclude specific files
    Reference: https://stackoverflow.com/questions/35115892/how-to-ex\
        clude-a-single-file-from-package-with-setuptools-and-setup-py
    """

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return [
            (pkg, mod, file)
            for (pkg, mod, file) in modules
            if not any(fnmatch.fnmatchcase(file, pat=pattern) for pattern in excluded)
        ]


with open("PyPiReadMe.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_requirement_txt():
    thelibFolder = os.path.dirname(os.path.realpath(__file__))
    requirementPath = thelibFolder + "/requirements_deploy.txt"
    if os.path.isfile(requirementPath):
        with open(requirementPath) as f:
            install_requires = f.read().splitlines()
    return install_requires


setup(
    name="aibro",
    version="1.1.1",
    author="AIpaca.ai",
    author_email="hello@aipaca.ai",
    description="Serverless model training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AIpaca-Inc/AIbro_lib",
    project_urls={
        "Bug Tracker": "https://github.com/AIpaca-Inc/AIbro_lib/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=("tests")),
    package_data={"": ["*.sh"]},
    cmdclass={"build_py": build_py},
    install_requires=get_requirement_txt(),
    scripts=["aibro/scripts/call_predict.sh", "aibro/scripts/infer_command.sh"],
    python_requires=">=3.6",
)

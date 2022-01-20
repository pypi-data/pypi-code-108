import os
from setuptools import setup, find_packages
import versioneer


def get_path(fname):
    return os.path.join(os.path.dirname(__file__), fname)


readme_path = get_path("README.md")
requirements_path = get_path("requirements.txt")

with open(readme_path, "r", encoding="utf-8") as fh:
    readme = fh.read()

with open(requirements_path, "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh]

setup(
    name="daybook",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Miguel Amezola",
    author_email="mail@imiguel.net",
    description="daybook is a reading log cli app",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/miguelamezola/daybook",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={"console_scripts": ["daybook = daybook.__main__:main"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
    ],
)

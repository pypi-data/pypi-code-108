# type: ignore

import setuptools
import subprocess

with open("README.md", "r") as fh:
    long_description = fh.read().replace('](', '][https://raw.githubusercontent.com/FarisHijazi/htmltable-cli/master/')
with open("requirements.txt", "r") as fh:
    rqeuirements = fh.readlines()

version = subprocess.Popen("git describe --abbrev=0 --tags", shell=True, stdout=subprocess.PIPE).stdout.read().decode().strip().lstrip('v')

setuptools.setup(
    name="htmltable-cli",
    version=version,    
    description="A command line tool to generate html tables with embedded images, videos and audio",
    long_description=long_description,
    url='https://github.com/FarisHijazi/htmltable-cli',
    author='Faris Hijazi',
    author_email='theefaris@gmail.com',
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=rqeuirements,
    keywords='html table htmltable html-table base64 report',
    entry_points={
        'console_scripts': [
            'htmltable=htmltable.htmltable:main',
        ]
    }
    )

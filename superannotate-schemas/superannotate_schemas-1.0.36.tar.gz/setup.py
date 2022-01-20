import os
import re
from pathlib import Path
from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

def get_version():
    init = open(os.path.join(this_directory, 'src', 'superannotate_schemas', '__init__.py')).read()
    match = re.search(r'^__version__ = [\'"]([^\'"]+)[\'"]', init, re.M)
    if not match:
        raise RuntimeError('Unable to find version string.')
    return match.group(1)

setup(
    name='superannotate_schemas',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=get_version(),
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    description='SuperAnnotate JSON Schemas',
    author='Vaghinak Basentsyan',
    author_email='vaghinak@superannotate.con',
    url='https://www.superannotate.com/',
    license='MIT',
    description_file="README.md",
    entry_points={
            'console_scripts': ['superannotate_schemas = superannotate_schemas.bin.app:main']
        },
      )

"""
Some helpful tools
"""
import os
import re


class Setup:
    def __init__(self, path: list):
        self.path = path[0]

    def setup(self):
        if os.path.exists(self.path + '/setup.py'):
            pass
        else:
            with open(self.path + '/setup.py', 'w') as setup:
                setup.write("""
from setuptools import setup, find_packages


setup(
    name='<NAME>',
    version='<VERSION>',
    author='<YOUR NAME>',
    author_email='<EMAIL>',
    packages=find_packages(),
    zip_safe='<BOOL>',
    platforms=['<OS>'],
    install_requires=['<REQUIRES>'],
    python_requires='>=<PYTHON VISION>',
    description='<DESCRIPTION>',
    long_description='<LONG DESCRIPTION>',
    license='<LICENSE>',
    url='<URL>',
    classifiers=[],
    scripts=['<SCRIPTS>']
)
            """)

    def pack(self):
        if os.path.isfile(os.path.abspath(self.path)):
            os.system('python' + self.path)
        else:
            with open(self.path + 'pack.py', 'w') as pack:
                pack.write("""
import os
import re

from UNKnownDB.DB import LocalDB

with open('./setup.py', 'r+') as setup:
    setup.seek(0, 0)
    read = setup.read()
    find = re.findall('version=(.+?),', read)
    v_id = float(eval(find[0].replace('.', '')))
    setup.seek(0, 0)
    num = str(v_id + 1)
    writing = read.replace(find[0], "'" + num[0] + '.' + num[1] + '.' + num[2] + "'")
    setup.write(writing[:-1])
os.system('python3 setup.py sdist bdist_wheel')
os.system('twine upload dist/*')
db = LocalDB('')
db.delete_all('./dist')

                """)

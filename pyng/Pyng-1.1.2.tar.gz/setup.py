from setuptools import setup, find_packages
import os
import re

# set the version number from the most recent CHANGES entry
# Careful: '(.*),' splits on the LAST comma on the line, not the first!
# Use      '(.*?),' to make the match as small as possible.
vxxx = re.compile(r'^v(.*?),')
for line in open(os.path.join(os.path.dirname(__file__), "CHANGES.txt")):
    match = vxxx.search(line)
    if match:
        version = match.group(1)
    # but keep looping: last assignment wins

setup(
    name='Pyng',
    version=version,
    author='Nat Goodspeed',
    author_email='nat.cognitoy@gmail.com',
    packages=find_packages(exclude=['*.test']),
    entry_points=dict(console_scripts=[
        'popup=pyng.tk.popup:script',
    ]),
    scripts=[],
    url='https://pypi.org/project/Pyng/',
    license='LICENSE.txt',
    description='Yet another collection of Python utility functions',
    long_description=open('README.txt').read(),
)

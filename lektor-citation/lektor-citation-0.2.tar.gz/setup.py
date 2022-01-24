import ast
import io
import re

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

_description_re = re.compile(r'description\s+=\s+(?P<description>.*)')

with open('lektor_citation.py', 'rb') as f:
    description = str(ast.literal_eval(_description_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    author='Homer S',
    author_email='homer77@ismus.net',
    description=description,
    keywords='Lektor plugin',
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',
    name='lektor-citation',
    packages=find_packages(),
    py_modules=['lektor_citation'],
    url='https://git.ismus.net/homer77/lektor-citation',
    version='0.2',
    classifiers=[
        'Framework :: Lektor',
        'Environment :: Plugins',
    ],
    entry_points={
        'lektor.plugins': [
            'citation = lektor_citation:CitationPlugin',
        ]
    },
    install_requires=['pybtex','pylatexenc','lektor-jinja-content']
)

import os
import datetime


class NameNotSpecificationError(Exception):
    def __init__(self, name):
        super()
        self.name = name
        self.__str__()

    def __str__(self):
        return 'The name {} does not meet the specification'.format(self.name)


class PathNotFoundError(Exception):
    def __init__(self):
        super()
        # self.name = name
        self.__str__()

    def __str__(self):
        return 'path is not found'


class PathNotFoundError(Exception):
    def __init__(self, name):
        super()
        self.name = name
        self.__str__()

    def __str__(self):
        return '{} is not found'.format(self.name)


class create(object):
    def __init__(self, **kw):
        super(create)
        try:
            kw['path']
        except KeyError:
            raise PathNotFoundError()
        try:
            self.createDir(kw['path']+kw['dirName'])
        except KeyError:
            try:
                self.createDir(kw['path']+kw['name'])
            except KeyError:
                raise NameNotFoundError('name')
        try:
            n = kw['pkgName']
        except KeyError:
            raise NameNotFoundError('pkgName')
        try:
            author = kw['author']
        except KeyError:
            raise NameNotFoundError('author')
        try:
            author_email = kw['author_email']
        except KeyError:
            raise NameNotFoundError('author_email')
        try:
            description = kw['description']
        except KeyError:
            raise NameNotFoundError('description')
        try:
            url = kw['url']
        except KeyError:
            raise NameNotFoundError('url')
        try:
            project_urls = kw['project_urls']
        except KeyError:
            raise NameNotFoundError('project_urls')
        try:
            classifiers = kw['classifiers']
        except KeyError:
            raise NameNotFoundError('classifiers')
        try:
            python_requires = kw['python_requires']
        except KeyError:
            raise NameNotFoundError('python_requires')
        try:
            install_requires = kw['install_requires']
        except KeyError:
            raise NameNotFoundError('install_requires')
        self.createFile('./'+n+'/', 'LICENSE', '''
MIT License

Copyright (c) [{}] [{}]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
        '''.format(datetime.datetime.now().year, n))
        print('INFO[000] create the LICENSE file')
        self.createFile('./'+n+'/', 'pyproject.toml', '''
[build-system]
requires = [
    "setuptools>=42",
    "wheel"
]
build-backend = "setuptools.build_meta"        
        ''')
        print('INFO[001] create the README.md file')
        self.createFile('./'+n+'/', 'README.md', '''#your project readme''')
        print('INFO[002] create the setup.py file')
        self.createFile('./'+n+'/', 'setup.py', '''
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="{}",
    version="0.0.1",
    author="{}",
    author_email="{}",
    description="{}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="{}",
    project_urls={},
    classifiers={},
    packages=["{}/"],
    python_requires=">={}",
    install_requires = {},
)    
        '''.format(n, author, author_email, description, url, project_urls, classifiers, n, python_requires, install_requires))
        self.createDir('./'+n+'/'+n+'/')
        print('INFO[004] create the {} dir'.format(n))
        self.createFile('./'+n+'/'+n+'/', '__init__.py', '# your python file')
        print('INFO[005] create the __init__.py file')
        print(f'{n} is success')

    def createDir(self, dirName):
        name = dirName
        if name[len(name)-1] != '/':
            raise NameNotSpecificationError(dirName)
        os.makedirs(name)

    def createFile(self, path, name, value):
        with open(path+name, 'w')as f:
            f.write(value)

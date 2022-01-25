from setuptools import setup
from setuptools import find_packages
from setuptools import Command
import shutil
import os
from clslq import version
from distutils.sysconfig import get_python_lib

version = version.CLSLQ_Version


def match(list, s):
    if s in list:
        return True
    return False


def rmdir(path):
    removelist = [
        '.pytest_cache', 'clslq.egg-info', '.eggs',
        'dist', 
    ]
    for root, dirs, files in os.walk(path):
        for d in dirs:
            t = os.path.join(root, d)
            father = os.path.basename(root)
            if father == '.git':
                continue
            if os.path.exists(t) and match(removelist, d):
                try:
                    print("delete {}".format(t))
                    shutil.rmtree(t, ignore_errors=True)
                except Exception as e:
                    print(e)

        for f in files:
            t = os.path.join(root, f)
            if os.path.exists(path) and match(removelist, f):
                try:
                    print("delete {}".format(t))
                    os.remove(t)
                except:
                    pass


class CleanCommand(Command):
    description = "[*]distclean project root directory"
    user_options = []

    # This method must be implemented
    def initialize_options(self):
        pass

    # This method must be implemented
    def finalize_options(self):
        pass

    def run(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        print("distclean work root:{}".format(workdir))
        rmdir(workdir)


class DocRunCommand(Command):
    description = "[*]Use sphinx-autobuild host fot document test."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass
        
    def run(self):
        os.system(
            "sphinx-autobuild --host 0.0.0.0 --port 8000 --re-ignore .rst docs build/html")

class PublishCommand(Command):

    description = "[*]Publish a new version to pypi, you may use -r to publish to https://pypi.org"

    user_options = [
        # The format is (long option, short option, description).
        # python setup.py publish --help
        # python setup.py publish -r/-l
        ("release", 'r', "Publish to pypi.org"),
    ]

    def initialize_options(self):
        """Set default values for options."""
        self.release = False
        self.lovelacelee = True

    def finalize_options(self):
        """Post-process options."""

        if self.release:
            print("V%s will publish to the https://upload.pypi.org/legacy/" %
                  version)

    def run(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        print("distclean work root:{}".format(workdir))
        rmdir(workdir)
        """Run command."""
        os.system("python -m pip install -U setuptools twine wheel")
        os.system("python setup.py sdist bdist_wheel")

        try:
            if self.release:
                os.system("twine upload dist/*")
        except Exception as e:
            print(e)


        print("Here is git command tips:")
        print("$ git add .")

        print("$ git commit -m 'publish on version %s'" % version)
        print("$ git tag -a v{} -m 'add tag on {}'".format(version, version))

        print("$ git push")
        print("$ git push origin --tags")


with open('ChangeLog.md', mode='r', encoding='utf-8') as f:
    history = f.read()

setup(
    name="clslq",
    version=version,
    author="Connard.Lee",
    author_email="lovelacelee@gmail.com",
    description="Connard's python library.",
    long_description=history,
    long_description_content_type='text/markdown',
    # Project home
    url="http://git.lovelacelee.com",
    install_requires=[
        'clspy',
        'loguru',
        'Click',
        'clspy',
        'sqlalchemy',
        'notion-client',
        'openpyxl',
        'requests',
        'pandas'
    ],
    platforms=["all"],
    keywords=['clslq', 'clslqutils'],
    # setup.py needs
    setup_requires=['setuptools', 'Click', 'twine', 'sphinx', 'sqlalchemy', 'clspy'],
    requires=['loguru'],
    # python3 setup.py test
    tests_require=[
        'pytest>=3.3.1',
        'pytest-cov>=2.5.1',
        'sqlalchemy',
        'pytest-html',
    ],
    python_requires='>=3',
    # setup_requires or tests_require packages
    # will be written into metadata of *.egg
    dependency_links=[
        #"clslq-1.1.0.tar.gz",
    ],
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Target users
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        #'Natural Language :: Chinese (Simplified)',

        # Project type
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        # Target Python version
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    # setuptools.find_packages
    packages=find_packages(exclude=["pytest"]),
    package_dir={'clslq': 'clslq'},
    # Static files: config/service/pictures
    data_files=[
        # root directory such as: c:\python39\
        # Use MANIFEST.in for egg/tar.gz.
        # data_files is required for bdist_wheel

        #('', ['clslq-template.json'])
        #('', ['conf/*.conf']),
        #('/usr/lib/systemd/system/', ['bin/*.service']),
        #('', ['clslq/pip.conf']),
        #('clslq', ['Pipfile']),
    ],
    # Will be packed
    package_data={
        'clslq': ['*.conf', '*.txt', '*.md', '*.html'],
    },
    # Will not be packed
    exclude_package_data={'useless': ['*.in']},
    entry_points={'console_scripts': ["clslq = clslq.cli:main"]},
    cmdclass={
        "distclean": CleanCommand,
        "publish": PublishCommand,
        "docrun": DocRunCommand,
    })

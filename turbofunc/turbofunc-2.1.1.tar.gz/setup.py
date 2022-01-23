version = "2.1.1"

from setuptools import setup

with open("README.md", "r") as file:
    long_desc = file.read()

import sys

# **Python version check**
# Source: https://github.com/ipython/ipython/blob/6a3e2db0c299dc05e636653c4a43d0aa756fb1c8/setup.py#L23-L58
if sys.version_info < (3, 4):
    pip_message = 'This may be due to an out of date pip. Make sure you have pip >= 9.0.1.'
    try:
        import pip
        pip_version = tuple([int(x) for x in pip.__version__.split('.')[:3]])
        if pip_version < (9, 0, 1):
            pip_message = 'Your pip version is out of date, please install pip >= 9.0.1, which won\'t download an incompatible version like this in the first place. '\
            'pip {} detected.'.format(pip.__version__)
        else:
            # pip is new enough - it must be something else
            pip_message = ''
    except Exception:
        pass

    error = """
turbofunc supports Python 3.4 and above.
You don't seem to have that. We suggest updating your Python as soon as possible - these old versions have not been maintained for a while by now.
Python {py} detected.
{pip}
""".format(py=sys.version_info, pip=pip_message )

    print(error, file=sys.stderr)
    sys.exit(1)

setup(
    name='turbofunc',
    version=version,
    description='simple functions for annoying-to-write tasks',
    long_description=long_desc,
    license='Apache 2.0',
    packages=['turbofunc'],
    author='TheTechRobo',
    author_email='thetechrobo@pm.me',
    keywords=['turbofunc', 'functions', 'press any key', 'getch', 'clear screen', 'easy', 'thetechrobo'],
    url='https://github.com/TheTechRobo/python-text-calculator',
    python_requires='>=3.4',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ],
    project_urls={
        'Source': 'https://github.com/thetechrobo/python-text-calculator',
        'Tracker': 'https://github.com/thetechrobo/python-text-calculator/issues',
    },

    long_description_content_type='text/markdown',
)

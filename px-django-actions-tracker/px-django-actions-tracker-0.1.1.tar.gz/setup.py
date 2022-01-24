import os
import re
import setuptools


with open('README.md', 'r') as rf:
    with open('CHANGELOG.md', 'r') as cf:
        long_description = rf.read() + cf.read()


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()

    return re.search('__version__ = [\'"]([^\'"]+)[\'"]', init_py).group(1)


version = get_version('pxd_actions_tracker')


setuptools.setup(
    name='px-django-actions-tracker',
    version=version,
    author='Alex Tkachenko',
    author_email='preusx.dev@gmail.com',
    license='MIT License',
    description='Simple in-app actions tracker.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(exclude=(
        'tests', 'tests.*',
        'experiments', 'pilot',
    )),
    install_requires=(
        'Django',
        'px-settings',
        'px-domains',
        'django-json-widget==1.1.1',
    ),
    extras_require={
        'dev': (
            'pytest>=6.0,<7.0',
            'pytest-watch>=4.2,<5.0',
            'pytest-django>=4.3,<5.0',
            'django-environ==0.4.5',
            'django-stubs',
            'django>=2.2,<4',
            'twine',
        ),
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Programming Language :: Python :: 3',
        'Framework :: Django',

        'Intended Audience :: Developers',
        'Topic :: Utilities',

        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

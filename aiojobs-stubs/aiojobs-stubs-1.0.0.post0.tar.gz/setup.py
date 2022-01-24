from pathlib import Path

from setuptools import setup

DIR = Path(__file__).parent

setup(
    name='aiojobs-stubs',
    author='Gleb Chipiga',
    version='1.0.0.post0',
    description='External type annotations for the aiojobs library',
    long_description=(DIR / 'README.rst').read_text('utf-8').strip(),
    long_description_content_type='text/x-rst',
    url='https://github.com/gleb-chipiga/aiojobs-stubs',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: AsyncIO'
    ],
    license='Apache 2',
    keywords=['asyncio', 'aiohttp', 'jobs', 'tasks', 'stubs', 'mypy'],
    packages=['aiojobs-stubs', 'aiojobs_protocols'],
    package_data={'aiojobs-stubs': ['__init__.pyi'],
                  'aiojobs_protocols': ['py.typed']},
    python_requires='>=3.8',
    tests_require=['types-setuptools'],
)

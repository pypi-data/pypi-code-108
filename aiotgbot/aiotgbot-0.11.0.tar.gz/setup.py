import re
from pathlib import Path

from setuptools import setup  # type: ignore

path = Path(__file__).parent
txt = (path / 'aiotgbot' / '__init__.py').read_text('utf-8')
version = re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]
readme = (path / 'README.rst').read_text('utf-8')

setup(
    name='aiotgbot',
    version=version,
    description='Asynchronous library for Telegram bot API',
    long_description=readme,
    long_description_content_type="text/x-rst",
    url='https://github.com/gleb-chipiga/aiotgbot',
    license='MIT',
    author='Gleb Chipiga',
    # author_email='',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet',
        'Topic :: Communications :: Chat',
        'Framework :: AsyncIO',
    ],
    packages=['aiotgbot'],
    package_data={'aiotgbot': ['py.typed']},
    python_requires='>=3.8,<3.11',
    install_requires=['aiohttp', 'aiojobs', 'aiojobs-stubs>=1.0.0.post0',
                      'attrs', 'backoff', 'frozenlist', 'aiofreqlimit>=0.0.7',
                      'yarl'],
    tests_require=['pytest', 'pytest-asyncio>=0.17.1', 'hypothesis'],
    extras_require={'sqlite': ['aiosqlite'], 'passport': ['cryptography']}
)

from setuptools import setup

setup(
    name='papyru',
    version='1.9.5',
    description=(
        'minimal REST library with OpenAPI-based validation for django'),
    author='puzzle & play GmbH',
    author_email='papyru@puzzleandplay.de',
    url='https://www.fotopuzzle.de/',
    license='AGPLv3',
    platforms=['any'],
    packages=['papyru', 'papyru.static', 'papyru.varspool'],
    package_data={},
    install_requires=[
        'Cerberus',
        'Django',
        'jsonschema',
        'pyyaml',
        'requests',
        'lxml',
        'python-dateutil',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    scripts=[
        'bin/generate_jsonschema.py'
    ]
)

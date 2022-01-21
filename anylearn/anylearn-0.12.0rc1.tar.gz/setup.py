import io

import setuptools


CLIENT_VERSION = "0.12.0rc1"
PACKAGE_NAME = "anylearn"

try:
    with io.open("README.md", encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = ""

REQUIRES = []
with open('requirements.txt') as f:
    for line in f:
        line, _, _ = line.partition('#')
        line = line.strip()
        REQUIRES.append(line)

setuptools.setup(
    name=PACKAGE_NAME,
    version=CLIENT_VERSION,
    license="Proprietary",
    description="Anylearn Python SDK",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author_email="anylearn@nelbds.org.cn",
    author="Dmagine",
    install_requires=REQUIRES,
    python_requires='>=3.7',
    packages=setuptools.find_packages(),
    package_data={
        'anylearn': [
            "storage/db/migrations/alembic.ini",
        ],
    },
    include_package_data=True,
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points = '''
        [console_scripts]
        anyctl = anylearn.cli.cli:cli
    ''',
)

from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'Testing repo'
LONG_DESCRIPTION = 'Testing repo blabla.'

# Setting up
setup(
    name="michalidesi-repo",
    version=VERSION,
    author="michalidesi",
    author_email="michalides.resetka@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'test'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
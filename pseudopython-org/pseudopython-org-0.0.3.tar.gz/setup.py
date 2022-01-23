from setuptools import setup, find_packages


VERSION = '0.0.3'
DESCRIPTION = 'Converting Python code snippets to Pseudocode effectively.'
LONG_DESCRIPTION = 'Converting Python code snippets to Pseudocode effectively.'

# Setting up
setup(
    name="pseudopython-org",
    version=VERSION,
    author="anonymouscoolguy",
    author_email="<anonymouscoolguy05@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['pseudocode', 'python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

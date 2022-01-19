# type: ignore

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    rqeuirements = fh.readlines()

setuptools.setup(
    name="htmltable-cli",
    version='0.1.5',    
    description="A command line tool to generate html tables with embedded images, videos and audio",
    long_description=long_description,
    url='https://github.com/FarisHijazi/htmltable-cli',
    author='Faris Hijazi',
    author_email='theefaris@gmail.com',
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=rqeuirements,
    keywords='html table htmltable html-table base64 report',
    entry_points={
        'console_scripts': [
            'htmltable=htmltable.htmltable:main',
        ]
    }
    )

import setuptools

setuptools.setup(
    name='xenget',
    packages=setuptools.find_packages(include=["xenget"]),
    version='0.0.2',
    description='A library for Python to get information from a XenForo forum.',
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    author='Cinar Yilmaz',
    author_email="<youremail@email.com>",
    license='GPLv3',
    install_requires=["beautifulsoup4"],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ]
)
from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Convert pixel coordinates to world coordinates from multiple cameras'
LONG_DESCRIPTION = 'Convert pixel coordinates to world coordinates from multiple cameras'

# Setting up
setup(
    name="pixel2world",
    version=VERSION,
    author="Casey Wiens",
    author_email="<cwiens32@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license='MIT',
    packages=['pixel2world'],
    url="https://github.com/cwiens32/pixel2world_base",
    install_requires=['pandas', 'numpy', 'xml-python', 'opencv-python'],
    keywords=['python', 'theia'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research"
    ]
)
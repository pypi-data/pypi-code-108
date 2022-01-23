from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.2'
DESCRIPTION = 'Basic color package'
LONG_DESCRIPTION = 'A package that allows to put color everywhere'

# Setting up
setup(
    name="colorfullytextuel",
    version=VERSION,
    author="NeuralNine (Florian Dedov)",
    author_email="<mail@neuralnine.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description="long_description",
    packages=find_packages(),
    install_requires=['opencv-python'],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

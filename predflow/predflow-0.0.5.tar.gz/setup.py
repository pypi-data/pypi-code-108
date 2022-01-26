from setuptools import setup, find_packages

VERSION = '0.0.5'
DESCRIPTION = 'Predictive coding with tensorflow'
LONG_DESCRIPTION = 'A python library for predictive coding simulations based on tensorflow.'

# Setting up
setup(
    name="predflow",
    version=VERSION,
    author="Arno Granier",
    author_email="<arno.granier@unibe.ch>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['tensorflow_datasets'],
    extras_require = {
    'gpu':  ['tensorflow-gpu'],
    'cpu': ['tensorflow']
    },
    keywords=['python', 'tensorflow', 'predictive coding'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Environment :: GPU :: NVIDIA CUDA :: 11.2"
    ]
)

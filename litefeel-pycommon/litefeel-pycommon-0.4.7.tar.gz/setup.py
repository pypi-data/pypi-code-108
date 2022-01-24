from setuptools import setup, find_packages


setup(
    name="litefeel-pycommon",
    version="0.4.7",
    description="my python common lib",
    author="litefeel",
    author_email="litefeel@gmail.com",
    url="http://github.com/litefeel/pycommon",
    license="MIT",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(exclude=["test"]),
    python_requires=">=3.9",
)

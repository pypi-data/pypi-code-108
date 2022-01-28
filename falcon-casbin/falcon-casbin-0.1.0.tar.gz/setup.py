from setuptools import setup

setup(
    name="falcon-casbin",
    version="0.1.0",
    description="Falcon Casbin middleware",
    url="http://github.com/alexferl/falcon-casbin",
    author="Alexandre Ferland",
    author_email="me@alexferl.com",
    license="MIT",
    packages=["falcon_casbin"],
    zip_safe=False,
    install_requires=["casbin>=1.15.0", "falcon>=2.0.0"],
    setup_requires=["pytest-runner>=5.3.1"],
    tests_require=["pretend>=1.0.9", "pytest>=6.2.5"],
    platforms="any",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

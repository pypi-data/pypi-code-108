# pylint: skip-file
import os
from setuptools import setup, find_packages, Extension

exec(open('src/traceableai/version.py').read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="traceable-agent",
    version=__version__,
    author="Traceable.ai",
    description="Traceable.ai Python Agent",
    url="https://traceable.ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.6",
    ext_modules=[ # this option will let wheel builder know to package c extensions when ran from CI. No effect for source tar installs
        Extension(
            name='traceableai.filter._blocking',
            sources=[],
            optional=os.environ.get('CIBUILDWHEEL', '0') != '1'
        )
    ],
    install_requires=[
        "hypertrace-agent==0.9.4",
        "psutil",
        "distro==1.6.0",
        "cffi",
    ],
    entry_points = {
        'console_scripts': [
            'traceableai-instrument = traceableai.autoinstrumentation.wrapper:run',
        ],
    }
)

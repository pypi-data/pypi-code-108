from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="imecilabt-gpulab-common",
    version="4.0.0",

    description="GPULab Common",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://gpulab.ilabt.imec.be",

    author="Thijs Walcarius <Thijs.Walcarius@ugent.be>, Wim Van de Meerssche <wim.vandemeerssche@ugent.be>",
    author_email="gpulab@ilabt.imec.be",

    project_urls={
        "Bug Tracker": "https://gitlab.ilabt.imec.be/ilabt/gpulab/gpulab-common/-/issues",
        "Documentation":  "https://doc.ilabt.imec.be/ilabt/gpulab/",
        "Source": "https://gitlab.ilabt.imec.be/ilabt/gpulab/gpulab-common",
    },
    license="GPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Operating System :: OS Independent",
    ],

    packages=["imecilabt.gpulab.model", "imecilabt.gpulab.util"],

    install_requires=[
        "snakecase", "python-dateutil", "pyyaml",
        "dataclass-dict-convert >=1.6.1, <2",
        "imecilabt-utils >=1.5.0, <2",
    ],
    python_requires='>=3.7',  # required because of dataclasses

    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'python-dateutil'],

    # Zipped eggs don't play nicely with namespace packaging, and may be implicitly installed by commands like
    # python setup.py install. To prevent this, it is recommended that you set zip_safe=False in setup.py
    zip_safe=False,
)

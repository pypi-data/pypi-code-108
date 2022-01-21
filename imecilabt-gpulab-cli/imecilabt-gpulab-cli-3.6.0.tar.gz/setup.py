from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="imecilabt-gpulab-cli",
    version="3.6.0",
    # Make sure to also update version number in imecilabt/gpulab/cli/__main__.py  (three times!)

    description="GPULab CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://gpulab.ilabt.imec.be",

    project_urls={
        "Bug Tracker": "https://gitlab.ilabt.imec.be/ilabt/gpulab/gpulab-cli/-/issues",
        "Documentation": "https://doc.ilabt.imec.be/ilabt/gpulab/",
        "Website": "https://gpulab.ilabt.imec.be",
        "Source": "https://gitlab.ilabt.imec.be/ilabt/gpulab/gpulab-cli",
    },
    license="GPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        # "Operating System :: OS Independent",  # Uses "pwd.getpwuid(os.getuid()).pw_name" which doesn't work on windows
        "Operating System :: POSIX :: Linux",
    ],

    author="Thijs Walcarius <Thijs.Walcarius@ugent.be>, Wim Van de Meerssche <wim.vandemeerssche@ugent.be>",
    author_email="gpulab@ilabt.imec.be",

    packages=["imecilabt.gpulab.cli"],

#requests 2.18.0 is required for "with session.get() as r:"  ("Response is now a context manager")
#         2.18.4 is known to  work
#click 6.7 is what is known to work

# Python version requirement:
#     At least python 3.4 was required previously (not sure for which feature, but < 3.4 will certainly fail)
#     but now, gpulab-common uses dataclasses, so at least python 3.7 is required
#        (python 3.7.0 was released June 27, 2018)
#        (python 3.7 is available from ubuntu 19.04 Disco Dingo, released April 18, 2019)
#            (the deadsnakes ppa can be used for earlier ubuntu's)
#        (python 3.7 is available from debian 10.0 buster, released July 6th, 2019)
#        (+ there's always https://github.com/pyenv/pyenv)

    install_requires=["requests>=2.18.4",
                      "click>=6.7",
                      # "sentry-sdk==0.14.4"  # not yet
                      "cryptography==3.4.8",
                      "imecilabt-gpulab-common>=4.0.0, <5"],
    python_requires='>=3.7',

    entry_points={
        'console_scripts': [
            'gpulab-cli=imecilabt.gpulab.cli.__main__:main',
        ],
    },

    # Zipped eggs don't play nicely with namespace packaging, and may be implicitly installed by commands like
    # python setup.py install. To prevent this, it is recommended that you set zip_safe=False in setup.py
    zip_safe=False,
)

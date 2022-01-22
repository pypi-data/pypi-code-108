# -*- coding: utf-8 -*-
# setup script for glue

import os
import time
from pathlib import Path

from setuptools import (
    find_packages,
    setup,
)
from setuptools.command import (
    build_py,
    sdist,
)
from setuptools.extension import Extension

from misc import generate_vcs_info as gvcsi

VERSION = "3.0.1"

HERE = Path(__file__).parent
SOURCE_PATH = HERE / "glue"
GIT_VERSION_PY = SOURCE_PATH / "git_version.py"


# -- build commands to support git_version.py ---

def write_build_info():
    """Get VCS info from misc/generate_vcs_info.py and add build information

    Substitute these into misc/git_version.py.in to produce glue/git_version.py
    """
    vcs_info = gvcsi.generate_git_version_info()

    # determine current time and treat it as the build time
    vcs_info.build_date = time.strftime(
        '%Y-%m-%d %H:%M:%S +0000',
        time.gmtime(),
    )

    # determine builder
    retcode, builder_name = gvcsi.call_out(('git', 'config', 'user.name'))
    if retcode:
        builder_name = "Unknown User"
    retcode, builder_email = gvcsi.call_out(('git', 'config', 'user.email'))
    if retcode:
        builder_email = ""
    vcs_info.builder = "%s <%s>" % (builder_name, builder_email)

    template = (HERE / "misc" / "git_version.py.in").read_text()
    GIT_VERSION_PY.write_text(template.format(vcs_info, version=VERSION))


class glue_build_py(build_py.build_py):
    def run(self):
        # create the git_version module
        self.announce("generating glue/git_version.py", level=2)
        try:
            write_build_info()
        except gvcsi.GitInvocationError:
            if not os.path.exists("glue/git_version.py"):
                raise
            # probably being built from a release tarball; don't overwrite
            self.announce(
                "not in git checkout or cannot find git executable; "
                "using existing glue/git_version.py",
                level=3,
            )

        # resume normal build procedure
        super().run()


class glue_sdist(sdist.sdist):
    def run(self):
        # create the git_version module
        self.announce("generating glue/git_version.py", level=2)
        write_build_info()

        # now run sdist
        super().run()


# -- contents

packages = find_packages(include=("glue*",))
scripts = list(map(str, Path("bin").glob("*")))
ext_modules = [
    Extension(
        "glue.ligolw.tokenizer",
        [
            "glue/ligolw/tokenizer.c",
            "glue/ligolw/tokenizer.Tokenizer.c",
            "glue/ligolw/tokenizer.RowBuilder.c",
            "glue/ligolw/tokenizer.RowDumper.c"
        ],
        include_dirs=["src", "glue/ligolw"]
    ),
    Extension(
        "glue.ligolw._ilwd",
        [
            "glue/ligolw/ilwd.c"
        ],
        include_dirs=["src", "glue/ligolw"]
    ),
]
data_files = [
    (os.path.join("share", "lscsoft-glue"), [
        os.path.join('etc', 'ligolw.xsl'),
        os.path.join('etc', 'ligolw.js'),
        os.path.join('etc', 'ligolw_dtd.txt'),
    ]),
]

# -- requirements

install_requires = [
    'ligo-segments',
    'numpy',
    'pyOpenSSL',
    'pyRXP',
    'six',
]

# -- setup


setup(
    # metadata
    name="lscsoft-glue",
    version=VERSION,
    author="Duncan Brown",
    author_email="dbrown@ligo.org",
    description="Grid LSC User Engine",
    long_description=(HERE / "README.md").read_text().strip(),
    long_description_content_type='text/markdown',
    url="https://docs.ligo.org/lscsoft/glue/",
    license='GPLv2+',
    # build instructions
    cmdclass={
        'build_py': glue_build_py,
        'sdist': glue_sdist
    },
    # contents
    packages=packages,
    scripts=scripts,
    ext_modules=ext_modules,
    data_files=data_files,
    # requirements
    install_requires=install_requires,
    # classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: '
        'GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics'
    ]
)

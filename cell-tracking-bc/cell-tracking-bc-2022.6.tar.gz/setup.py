# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from pathlib import Path

from setuptools import setup


AUTHOR = "Eric Debreuve"
E_MAIL = "eric.debreuve@univ-cotedazur.fr"

PYPI_NAME = "cell-tracking-bc"
DESCRIPTION = "Base Classes for Cell Tracking in Microscopy"
VERSION = (2022, 6)  # /!\ str(2021.10) -> "2021.1"
PY_VERSION = "3.8"

REPOSITORY_NAME = "cell-tracking-bc"
REPOSITORY_USER = "edebreuv"
REPOSITORY_SITE = "gitlab.inria.fr"
DOCUMENTATION_SITE = f"{REPOSITORY_USER}.gitlabpages.inria.fr"

IMPORT_NAME = "cell_tracking_BC"
PACKAGES = [
    IMPORT_NAME,
    f"{IMPORT_NAME}.in_out",
    f"{IMPORT_NAME}.in_out.file",
    f"{IMPORT_NAME}.in_out.graphics",
    f"{IMPORT_NAME}.in_out.graphics.dbe",
    f"{IMPORT_NAME}.in_out.graphics.dbe.matplotlib",
    f"{IMPORT_NAME}.in_out.graphics.dbe.mayavi",
    f"{IMPORT_NAME}.in_out.graphics.dbe.vedo",
    f"{IMPORT_NAME}.in_out.graphics.generic",
    f"{IMPORT_NAME}.in_out.text",
    f"{IMPORT_NAME}.standard",
    f"{IMPORT_NAME}.task",
    f"{IMPORT_NAME}.task.tracking",
    f"{IMPORT_NAME}.test",
    f"{IMPORT_NAME}.type",
]

HERE = Path(__file__).parent.resolve()


long_description = (HERE / "README.rst").read_text(encoding="utf-8")
repository_url = f"https://{REPOSITORY_SITE}/{REPOSITORY_USER}/{REPOSITORY_NAME}"
documentation_url = repository_url
version = f"{VERSION[0]}.{VERSION[1]}"

folders = [IMPORT_NAME]
for node in (HERE / IMPORT_NAME).rglob("*"):
    if node.is_dir():
        node = node.relative_to(HERE)
        node = str(node).replace("/", ".")
        folders.append(node)
folders = sorted(folders)
if PACKAGES != folders:
    raise ValueError(
        f"Missing packages in setup:\n"
        f"    - Declared={PACKAGES}\n"
        f"    - Actual={folders}"
    )


if __name__ == "__main__":
    #
    setup(
        # --- OLD BUILD PROCEDURE
        # Remove: {IMPORT_NAME.lower()}.egg-info/ build/ dist/
        # python setup.py bdist_wheel
        # --- NEW BUILD PROCEDURE
        # Remove: {IMPORT_NAME.lower()}.egg-info/ dist/
        # python -m build
        # --- UPLOAD
        # twine upload dist/*
        # https://pypi.org/project/{PYPI_NAME}
        author=AUTHOR,
        author_email=E_MAIL,
        #
        name=PYPI_NAME,
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type="text/x-rst",
        version=version,
        license="CeCILL-2.1",
        #
        classifiers=[
            "Topic :: Scientific/Engineering :: Image Recognition",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)",
            f"Programming Language :: Python :: {PY_VERSION}",
            "Development Status :: 4 - Beta",
        ],
        keywords="cell, tracking, microscopy, classes",
        #
        url=repository_url,
        project_urls={
            "Documentation": documentation_url,
            "Source": repository_url,
        },
        #
        packages=PACKAGES,
        python_requires=f">={PY_VERSION}",
        install_requires=[
            "imageio",
            "itk",
            "matplotlib",
            # "mayavi",  # Temporarily removed since mayavi does not compile
            "mrc",
            "networkx",
            "numpy",
            "pca-b-stream",
            "Pillow",
            "plotext",
            "rich",
            "scikit-image",
            "scipy",
            "tensorflow",
            "tifffile",
            "vedo",
            "xlsxwriter",
        ],
    )

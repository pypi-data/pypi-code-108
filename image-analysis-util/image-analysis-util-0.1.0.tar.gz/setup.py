# ----------------------------------------------------------------------------------

from pathlib import Path
from setuptools import setup, find_packages

# ----------------------------------------------------------------------------------

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text()

# ----------------------------------------------------------------------------------

setup( 
    name="image-analysis-util",
    version="0.1.0",
    description="Scientific image exploration software for multidimensional datasets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Henry Smith",
    author_email="smithh@anl.gov",
    url="https://github.com/henryjsmith12/image-analysis-util/iautil",
    install_requires=[
        "h5py",
        "numpy",
        "PyQt5",
        "pyqtgraph",
        "scipy",
        "vtk",
        "xarray",
    ],
    packages=find_packages(),
    license="See LICENSE file",
    platforms="any",
)


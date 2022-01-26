# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyechelle']

package_data = \
{'': ['*'], 'pyechelle': ['models/*']}

install_requires = \
['astropy>=5.0,<6.0',
 'astroquery>=0.4.4,<0.5.0',
 'h5py>=3.1.0,<4.0.0',
 'joblib>=1.1.0,<2.0.0',
 'matplotlib>=3.3.2,<4.0.0',
 'numba>=0.55.0,<0.56.0',
 'pandas>=1.3.4,<2.0.0',
 'parmap>=1.5.2,<2.0.0',
 'plotly>=5.4.0,<6.0.0',
 'scipy>=1.5.2,<2.0.0',
 'skycalc-ipy>=0.1.3,<0.2.0']

entry_points = \
{'console_scripts': ['pyechelle = pyechelle.simulator:main']}

setup_kwargs = {
    'name': 'pyechelle',
    'version': '0.2.1',
    'description': 'A fast generic spectrum simulator',
    'long_description': '# PyEchelle\n\nPyEchelle is a simulation tool, to generate realistic 2D spectra, in particular cross-dispersed echelle spectra.\nHowever, it is not limited to echelle spectrographs, but allows simulating arbitrary spectra for any fiber-fed or slit\nspectrograph, where a model file is available. Optical aberrations are treated accurately, the simulated spectra include\nphoton and read-out noise.\n\nPyEchelle uses numba for implementing fast Python-based simulation code. It also comes with **CUDA support** for major\nspeed improvements.\n\n### Example usage\n\n```bash\npyechelle --spectrograph MaroonX --fiber 2-4 --sources Phoenix --phoenix_t_eff 3500 -t 10 --rv 100 -o mdwarf.fit\n```\n\nsimulates a PHOENIX M-dwarf spectrum with the given stellar parameters, and a RV shift of 100m/s for the MAROON-X\nspectrograph.\n\nThe output is a 2D raw frame (.fits) and will look similar to:\n\n![](https://gitlab.com/Stuermer/pyechelle/-/raw/master/docs/source/_static/plots/mdwarf.jpg "")\n\nCheck out the [Documentation](https://stuermer.gitlab.io/pyechelle/usage.html) for more examples.\n\nPyechelle is the successor of [Echelle++](https://github.com/Stuermer/EchelleSimulator) which has a similar\nfunctionality but was written in C++. This package was rewritten in python for better maintainability, easier package\ndistribution and for smoother cross-platform development.\n\n# Installation\n\nAs simple as\n\n```bash\npip install pyechelle\n```\n\nCheck out the [Documentation](https://stuermer.gitlab.io/pyechelle/installation.html) for alternative installation instruction.\n\n# Usage\n\nSee\n\n```bash\npyechelle -h\n```\n\nfor all available command line options.\n\nSee [Documentation](https://stuermer.gitlab.io/pyechelle/usage.html) for more examples.\n\n# Concept:\n\nThe basic idea is that any spectrograph can be modelled with a set of wavelength-dependent transformation matrices and\npoint spread functions which describe the spectrographs\' optics:\n\nFirst, wavelength-dependent **affine transformation matrices** are extracted from the ZEMAX model of the spectrograph.\nAs the underlying geometric transformations (scaling, rotation, shearing, translation) vary smoothly across an echelle\norder, these matrices can be interpolated for any intermediate wavelength.\n\nSecond, a wavelength-dependent **point spread functions (PSFs)** is applied on the transformed slit images to properly\naccount for optical aberrations. Again, the PSF is only slowly varying across an echelle order, allowing for\ninterpolation at intermediate wavelength.\n\n![Echelle simulation](https://gitlab.com/Stuermer/pyechelle/-/raw/master/docs/source/_static/plots/intro.png "Echelle simulation")\n\n**Both, the matrices and the PSFs have to be extracted from ZEMAX only once. It is therefore possible to simulate\nspectra without access to ZEMAX**\n\n# Citation\n\nPlease cite this [paper](http://dx.doi.org/10.1088/1538-3873/aaec2e) if you find this work useful in your research.\n',
    'author': 'Julian Stuermer',
    'author_email': 'julian@stuermer.science',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/Stuermer/pyechelle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)

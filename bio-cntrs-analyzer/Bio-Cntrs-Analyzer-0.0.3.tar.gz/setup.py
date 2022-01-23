# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bcanalyzer',
 'bcanalyzer.common',
 'bcanalyzer.gui.controllers',
 'bcanalyzer.gui.models',
 'bcanalyzer.gui.views',
 'bcanalyzer.gui.widgets',
 'bcanalyzer.image_processing']

package_data = \
{'': ['*'], 'bcanalyzer': ['gui/resources/*']}

install_requires = \
['PyQt5',
 'appdirs',
 'filetype',
 'numpy>=1.19.0,<2.0.0',
 'opencv-python==4.3.0.36',
 'pandas',
 'scipy']

entry_points = \
{'console_scripts': ['bcanalyzer = bcanalyzer.app:main']}

setup_kwargs = {
    'name': 'bio-cntrs-analyzer',
    'version': '0.0.3',
    'description': 'The semi-automatic segmentation and quantification of patchy areas in various biomedical images based on the assessment of their local edge densities.',
    'long_description': '# BCAnalyzer: Segmentation of patchy areas in biomedical images based on local edge density estimation\n\n## Installation from binaries\n\n```bash\npip install -U bio-cntrs-analyzer\n```\n## Build exe from source\n\n```bash\npip install cx_Freeze\npython setup.py build\n```\n## User manual\n\nFor starting appliation evualate in command line (terminal) the next command:\n\n```bash\nbcanalyzer\n```\n\n![UserManualFigure](images/UserManualFigure.PNG) \n\nSoftware user interface outline: (A) list of images submitted for the analysis; (B) segmentation algorithm options; (C) color channel import options; (D) selected image with on-the-fly with marked-up visualization of the segmentation results; (E) segmentation algorithm controls for online adjustment of sensitivity and resolution; (F) file export menu.\n\nThe typical algorithm of user interaction with the software is as follows:\n\n* Selected images are imported by their drag-and-drop onto the program window. The image list appears in **A**.\n* Global algorithm options can be adjusted in **B** and color channels for the analysis selected in **C**.\n* The image selected in the list **A** is displayed in **D** with immediate effect of the segmentation algorithm visualized (using default parameters during the first run).\n* Next the algorithm parameters (sensitivity and resolution) can be adjusted manually in **E**. Segmentation results are visualized on-the-fly for direct user control. Of note, global options and color channel selection can be readjusted at this stage as well. Following adjustment, the chosen algorithm parameters can be applied either to the entire imported image set, or solely to the currently analyzed image, with corresponding controls available in **E**.\n* Once the algorithm parameters are adjusted for either a single or a few representative image(s), further processing and export can be performed as a fully automated procedure for the entire image set using file export options in **F**. Export options include visualizations of segmentation results, either as binary masks or as marked-up images similar to those appearing on the screen during analysis, as well as a *.csv table with summary statistics.\n\n# Dataset\n\nLink to downloading dataset:\n\nhttps://drive.digiratory.ru/d/s/mrbRyk4HyFbOIEANc6DhQGxhCFNgq3xI/Jqbcbsq_eE5Cf8-bnJaM3dXL6RI1v7d7-d74AOY4RLgk\n\nIf something goes wrong, please, write to amsinitca[at]etu.ru\n\n# Citation\n\nIf you find this project useful, please cite:\n\n```bib\n```\n\n',
    'author': 'Aleksandr Sinitca',
    'author_email': 'amsinitca@etu.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/digiratory/biomedimaging/bcanalyzer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

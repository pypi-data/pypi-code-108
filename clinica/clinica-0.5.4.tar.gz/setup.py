# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clinica',
 'clinica.engine',
 'clinica.iotools',
 'clinica.iotools.converters',
 'clinica.iotools.converters.adni_to_bids',
 'clinica.iotools.converters.adni_to_bids.adni_modalities',
 'clinica.iotools.converters.aibl_to_bids',
 'clinica.iotools.converters.habs_to_bids',
 'clinica.iotools.converters.nifd_to_bids',
 'clinica.iotools.converters.oasis3_to_bids',
 'clinica.iotools.converters.oasis_to_bids',
 'clinica.iotools.utils',
 'clinica.lib',
 'clinica.lib.nipype.interfaces.mrtrix3',
 'clinica.pipelines',
 'clinica.pipelines.cli_param',
 'clinica.pipelines.deeplearning_prepare_data',
 'clinica.pipelines.dwi_connectome',
 'clinica.pipelines.dwi_dti',
 'clinica.pipelines.dwi_preprocessing_using_fmap',
 'clinica.pipelines.dwi_preprocessing_using_t1',
 'clinica.pipelines.machine_learning',
 'clinica.pipelines.machine_learning_spatial_svm',
 'clinica.pipelines.pet_linear',
 'clinica.pipelines.pet_surface',
 'clinica.pipelines.pet_volume',
 'clinica.pipelines.statistics_surface',
 'clinica.pipelines.statistics_volume',
 'clinica.pipelines.statistics_volume_correction',
 'clinica.pipelines.t1_freesurfer',
 'clinica.pipelines.t1_freesurfer_atlas',
 'clinica.pipelines.t1_freesurfer_longitudinal',
 'clinica.pipelines.t1_linear',
 'clinica.pipelines.t1_volume',
 'clinica.pipelines.t1_volume_create_dartel',
 'clinica.pipelines.t1_volume_dartel2mni',
 'clinica.pipelines.t1_volume_existing_template',
 'clinica.pipelines.t1_volume_parcellation',
 'clinica.pipelines.t1_volume_register_dartel',
 'clinica.pipelines.t1_volume_tissue_segmentation',
 'clinica.utils']

package_data = \
{'': ['*'],
 'clinica': ['resources/*',
             'resources/atlases/*',
             'resources/masks/*',
             'resources/templates/pipeline_template/*'],
 'clinica.iotools': ['data/*'],
 'clinica.iotools.converters': ['clinical_data_bids_correspondence/*'],
 'clinica.lib': ['clinicasurfstat/*',
                 'clinicasurfstat/SurfStat/*',
                 'clinicasurfstat/SurfStat/@random/*',
                 'clinicasurfstat/SurfStat/@term/*']}

install_requires = \
['argcomplete>=1.9.4,<2.0.0',
 'attrs>=20.1.0',
 'cattrs>=1.9.0,<2.0.0',
 'click-option-group>=0.5,<0.6',
 'click>=8,<9',
 'colorlog>=5,<6',
 'fsspec',
 'jinja2>=2.10.1,<3.0.0',
 'matplotlib',
 'networkx',
 'nibabel>=2.3.3,<3.0.0',
 'niflow-nipype1-workflows',
 'nilearn>=0.7.0,<0.8.0',
 'nipype>=1.7.0,<2.0.0',
 'numpy>=1.17,<2.0',
 'openpyxl',
 'pandas>=1.2,<2.0',
 'pydicom',
 'scikit-image>=0.19,<0.20',
 'scikit-learn>=1.0,<2.0',
 'scipy>=1.2.3,<2.0.0',
 'xgboost',
 'xlrd',
 'xvfbwrapper']

extras_require = \
{'docs': ['mkdocs>=1.1,<2.0', 'mkdocs-material>=7.1.8', 'pymdown-extensions']}

entry_points = \
{'console_scripts': ['clinica = clinica.cmdline:main']}

setup_kwargs = {
    'name': 'clinica',
    'version': '0.5.4',
    'description': 'Software platform for clinical neuroimaging studies',
    'long_description': '<!--(http://www.clinica.run/img/clinica_brainweb.png)-->\n<!-- markdownlint-disable MD033 -->\n\n<h1 align="center">\n  <a href="http://www.clinica.run">\n    <img src="http://www.clinica.run/assets/images/clinica-icon-257x257.png" alt="Logo" width="120" height="120">\n  </a>\n  <br/>\n  Clinica\n</h1>\n\n<p align="center"><strong>Software platform for clinical neuroimaging studies</strong></p>\n\n<p align="center">\n  <a href="https://ci.inria.fr/clinica-aramis/job/clinica/job/dev/">\n    <img src="https://ci.inria.fr/clinica-aramis/buildStatus/icon?job=clinica%2Fdev" alt="Build Status">\n  </a>\n  <a href="https://badge.fury.io/py/clinica">\n    <img src="https://badge.fury.io/py/clinica.svg" alt="PyPI version">\n  </a>\n  <a href="https://aramislab.paris.inria.fr/clinica/docs/public/latest/Installation/">\n  </a>\n  <a href="https://aramislab.paris.inria.fr/clinica/docs/public/latest/Installation/">\n    <img src="https://anaconda.org/aramislab/clinica/badges/platforms.svg" alt="platform">\n  </a>\n  <a href="https://github.com/psf/black">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">\n  </a>\n</p>\n\n<p align="center">\n  <a href="http://www.clinica.run">Homepage</a> |\n  <a href="https://aramislab.paris.inria.fr/clinica/docs/public/latest/">Documentation</a> |\n  <a href="https://doi.org/10.3389/fninf.2021.689675">Paper</a> |\n  <a href="https://github.com/aramis-lab/clinica/discussions">Forum</a> |\n  See also:\n  <a href="#related-repositories">AD-ML</a>,\n  <a href="#related-repositories">AD-DL</a>\n  <a href="#related-repositories">ClinicaDL</a>\n</p>\n\n## About The Project\n\nClinica is a software platform for clinical research studies involving patients\nwith neurological and psychiatric diseases and the acquisition of multimodal\ndata (neuroimaging, clinical and cognitive evaluations, genetics...),\nmost often with longitudinal follow-up.\n\nClinica is command-line driven and written in Python.\nIt uses the [Nipype](https://nipype.readthedocs.io/) system for pipelining and combines\nwidely-used software packages for neuroimaging data analysis\n([ANTs](http://stnava.github.io/ANTs/),\n[FreeSurfer](https://surfer.nmr.mgh.harvard.edu/),\n[FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki),\n[MRtrix](https://www.mrtrix.org/),\n[PETPVC](https://github.com/UCL/PETPVC),\n[SPM](https://www.fil.ion.ucl.ac.uk/spm/)), machine learning\n([Scikit-learn](https://scikit-learn.org/stable/)) and the [BIDS\nstandard](http://bids-specification.readthedocs.io/) for data organization.\n\nClinica provides tools to convert publicly available neuroimaging datasets into\nBIDS, namely:\n\n- [ADNI: Alzheimer’s Disease Neuroimaging Initiative](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Converters/ADNI2BIDS/)\n- [AIBL: Australian Imaging, Biomarker & Lifestyle Flagship Study of Ageing](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Converters/AIBL2BIDS/)\n- [NIFD: Neuroimaging in Frontotemporal Dementia](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Converters/NIFD2BIDS/)\n- [OASIS: Open Access Series of Imaging Studies](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Converters/OASIS2BIDS/)\n- [OASIS-3: Longitudinal Neuroimaging, Clinical, and Cognitive Dataset for Normal Aging and Alzheimer’s Disease](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Converters/OASIS3TOBIDS/)\n\nClinica can process any BIDS-compliant dataset with a set of complex processing\npipelines involving different software packages for the analysis of\nneuroimaging data (T1-weighted MRI, diffusion MRI and PET data).\nIt also provides integration between feature extraction and statistics, machine\nlearning or deep learning.\n\n![ClinicaPipelines](http://www.clinica.run/img/Clinica_Pipelines_A4_2021-04-02_75dpi.jpg)\n\nClinica is also showcased as a framework for the reproducible classification of\nAlzheimer\'s disease using\n[machine learning](https://github.com/aramis-lab/AD-ML) and\n[deep learning](https://github.com/aramis-lab/clinicadl).\n\n## Getting Started\n\n> Full instructions for installation and additional information can be found in\nthe [user documentation](https://aramislab.paris.inria.fr/clinica/docs/public/latest/).\n\nClinica currently supports macOS and Linux.\nIt can be installed by typing the following command:\n\n```sh\npip install clinica\n```\n\nTo avoid conflicts with other versions of the dependency packages installed by pip, it is strongly recommended to create a virtual environment before the installation.\nFor example, use [Conda](https://docs.conda.io/en/latest/miniconda.html), to create a virtual\nenvironment and activate it before installing clinica (you can also use\n`virtualenv`):\n\n```sh\nconda create --name clinicaEnv python=3.7\nconda activate clinicaEnv\n```\n\nDepending on the pipeline that you want to use, you need to install pipeline-specific interfaces.\nNot all the dependencies are necessary to run Clinica.\nPlease refer to this [page](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Third-party/)\nto determine which third-party libraries you need to install.\n\n## Example\n\nDiagram illustrating the Clinica pipelines involved when performing a group\ncomparison of FDG PET data projected on the cortical surface between patients\nwith Alzheimer\'s disease and healthy controls from the ADNI database:\n\n![ClinicaExample](http://www.clinica.run/img/Clinica_Example_2021-04-02_75dpi.jpg)\n\n1. Clinical and neuroimaging data are downloaded from the ADNI website and data\n   are converted into BIDS with the [`adni-to-bids`\n   converter](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Converters/ADNI2BIDS/).\n2. Estimation of the cortical and white surface is then produced by the\n   [`t1-freesurfer`\n   pipeline](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Pipelines/T1_FreeSurfer/).\n3. FDG PET data can be projected on the subject’s cortical surface and\n   normalized to the FsAverage template from FreeSurfer using the\n   [`pet-surface` pipeline](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Pipelines/PET_Surface/).\n4. TSV file with demographic information of the population studied is given to\n   the [`statistics-surface`\n   pipeline](https://aramislab.paris.inria.fr/clinica/docs/public/latest/Pipelines/Stats_Surface/) to generate\n   the results of the group comparison.\n\n> For more examples and details, please refer to the\n> [Documentation](https://aramislab.paris.inria.fr/clinica/docs/public/latest/).\n\n## Support\n\n- Check for [past answers](https://groups.google.com/forum/#!forum/clinica-user) in the old Clinica Google Group\n- Start a [discussion](https://github.com/aramis-lab/clinica/discussions) on Github\n- Report an [issue](https://github.com/aramis-lab/clinica/issues) on GitHub\n\n## Contributing\n\nWe encourage you to contribute to Clinica!\nPlease check out the [Contributing to Clinica guide](CONTRIBUTING.md) for guidelines about how to proceed.\nDo not hesitate to ask questions if something is not clear for you, report an issue, etc.\n\n## License\n\nThis software is distributed under the MIT License.\nSee [license file](https://github.com/aramis-lab/clinica/blob/dev/LICENSE.txt)\nfor more information.\n\n## Citing us\n\n- Routier, A., Burgos, N., Díaz, M., Bacci, M., Bottani, S., El-Rifai O., Fontanella, S., Gori, P., Guillon, J., Guyot, A., Hassanaly, R., Jacquemont, T.,  Lu, P., Marcoux, A.,  Moreau, T., Samper-González, J., Teichmann, M., Thibeau-Sutre, E., Vaillant G., Wen, J., Wild, A., Habert, M.-O., Durrleman, S., and Colliot, O.:\n*Clinica: An Open Source Software Platform for Reproducible Clinical Neuroscience Studies* Frontiers in Neuroinformatics, 2021\n[doi:10.3389/fninf.2021.689675](https://doi.org/10.3389/fninf.2021.689675)\n\n## Related Repositories\n\n- [AD-DL: Classification of Alzheimer\'s disease status with convolutional neural networks](https://github.com/aramis-lab/AD-DL)\n- [AD-ML: Framework for the reproducible classification of Alzheimer\'s disease using\nmachine learning](https://github.com/aramis-lab/AD-ML)\n- [ClinicaDL: Framework for the reproducible processing of neuroimaging data with deep learning methods](https://github.com/aramis-lab/clinicadl)\n',
    'author': 'ARAMIS Lab',
    'author_email': None,
    'maintainer': 'Clinica developers',
    'maintainer_email': 'clinica-user@inria.fr',
    'url': 'https://www.clinica.run',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)

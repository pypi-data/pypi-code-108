# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rwrap']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.8.0,<2.0.0',
 'geopandas>=0.10.2,<0.11.0',
 'loguru>=0.5.3,<0.6.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.4.0,<2.0.0',
 'rpy2>=3.4.5,<4.0.0']

setup_kwargs = {
    'name': 'rwrap',
    'version': '0.1.2',
    'description': 'A thin wrapper around rpy2 with strong opinions on how data types should be converted.',
    'long_description': '# rwrap\n\n[![PyPI](https://img.shields.io/pypi/v/rwrap.svg?style=flat)](https://pypi.python.org/pypi/rwrap)\n[![Tests](https://github.com/kpj/rwrap/actions/workflows/main.yml/badge.svg)](https://github.com/kpj/rwrap/actions/workflows/main.yml)\n\nA thin wrapper around [rpy2](https://rpy2.github.io/doc/latest/html/index.html) with strong opinions on how data types should be converted. This enables easy usage of R packages from Python with no boilerplate code.\n\n> Warning: still work-in-progress, issues and PRs welcome\n\n\n## Installation\n\n```bash\npip install rwrap\n```\n\n\n## Usage\n\nFor example, accessing Bioconductor\'s [biomaRt](https://bioconductor.org/packages/release/bioc/html/biomaRt.html) package can be as simple as follows:\n```python\nfrom rwrap import biomaRt\n\nbiomaRt\n## <module \'biomaRt\' from \'/Library/Frameworks/R.framework/Versions/4.1/Resources/library/biomaRt\'>\n\nsnp_list = ["rs7329174", "rs4948523", "rs479445"]\nensembl = biomaRt.useMart("ENSEMBL_MART_SNP", dataset="hsapiens_snp")\n\ndf = biomaRt.getBM(\n    attributes=["refsnp_id", "chr_name", "chrom_start", "consequence_type_tv"],\n    filters="snp_filter", values=snp_list, mart=ensembl\n)\n\nprint(df)  # pandas.DataFrame\n##    refsnp_id  chr_name  chrom_start     consequence_type_tv\n## 1   rs479445         1     60875960          intron_variant\n## 2   rs479445         1     60875960  NMD_transcript_variant\n## 3  rs4948523        10     58579338          intron_variant\n## 4  rs7329174        13     40983974          intron_variant\n```\n\nCheck the `tests/` directory for more examples showing how to rewrite R scripts in Python.\n\n\n## Tests\n\nA comprehensive test suite aims at providing stability and avoiding regressions.\nThe examples in `tests/` are validated using `pytest`.\n\nRun tests as follows:\n\n```bash\n$ pytest tests/\n```\n',
    'author': 'kpj',
    'author_email': 'kim.philipp.jablonski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kpj/rwrap',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)

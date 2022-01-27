# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biopipen',
 'biopipen.core',
 'biopipen.namespaces',
 'biopipen.scripts.bam',
 'biopipen.scripts.bcftools',
 'biopipen.scripts.gene',
 'biopipen.scripts.misc',
 'biopipen.scripts.vcf',
 'biopipen.scripts.web',
 'biopipen.utils']

package_data = \
{'': ['*'],
 'biopipen': ['reports/bam/*',
              'reports/gsea/*',
              'reports/scrna/*',
              'reports/scrna_metabolic/*',
              'reports/tcr/*',
              'reports/utils/*',
              'scripts/bed/*',
              'scripts/gsea/*',
              'scripts/plot/*',
              'scripts/rnaseq/*',
              'scripts/scrna/*',
              'scripts/scrna_metabolic/*',
              'scripts/tcr/*']}

install_requires = \
['cmdy>=0.4.3,<0.5.0', 'datar>=0.5,<0.6', 'pipen>=0.2.14,<0.3.0']

entry_points = \
{'pipen_cli_run': ['bam = biopipen.namespaces.bam',
                   'bcftools = biopipen.namespaces.bcftools',
                   'bed = biopipen.namespaces.bed',
                   'csv = biopipen.namespaces.csv',
                   'gene = biopipen.namespaces.gene',
                   'gsea = biopipen.namespaces.gsea',
                   'misc = biopipen.namespaces.misc',
                   'plot = biopipen.namespaces.plot',
                   'rnaseq = biopipen.namespaces.rnaseq',
                   'scrna = biopipen.namespaces.scrna',
                   'scrna_metabolic = biopipen.namespaces.scrna_metabolic',
                   'tcr = biopipen.namespaces.tcr',
                   'vcf = biopipen.namespaces.vcf',
                   'web = biopipen.namespaces.web']}

setup_kwargs = {
    'name': 'biopipen',
    'version': '0.1.7',
    'description': 'Bioinformatics processes/pipelines that can be run from `pipen run`',
    'long_description': None,
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)

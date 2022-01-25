# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycashier']

package_data = \
{'': ['*']}

install_requires = \
['rich>=10.12.0,<11.0.0']

entry_points = \
{'console_scripts': ['pycashier = pycashier.pycashier:main']}

setup_kwargs = {
    'name': 'pycashier',
    'version': '0.2.8',
    'description': 'cash in on expressed barcode tags',
    'long_description': "# Cash in on Expressed Barcode Tags (EBTs) from NGS Sequencing Data *with Python*\n\nTool for extracting and processing DNA barcode tags from Illumina sequencing.\n\nDefault parameters are designed for use by the Brock Lab to process data generated from\nClonMapper lineage tracing experiments, but is extensible to other similarly designed tools.\n\n\n### Bioconda Dependencies\n- cutadapt (sequence extraction)\n- starcode (sequence clustering)\n- fastp (merging/quality filtering)\n- pysam (sam file convertion to fastq)\n\n## Installation\nIt's recommended to use [conda](https://docs.conda.io/en/latest/)/[mamba](https://github.com/mamba-org/mamba) to install and manage the dependencies for this package\n\n```bash\nconda install -c conda-forge -c bioconda cutadapt fastp pysam starcode pycashier\n```\n\nYou can also use the included `environment.yml` to create your environment and install everything you need.\n\n```bash\nconda env create -f https://raw.githubusercontent.com/brocklab/pycashier/main/environment.yml\nconda activate cashierenv\n```\n\nAdditionally you may install with pip. Though it will be up to you to ensure all the\ndependencies you would install from bioconda are on your path and installed correctly.\n`Pycashier` will check for them before running.\n\n```bash\npip install pycashier\n```\n\n## Usage\n\nPycashier has one required argument which is the directory containing the fastq or sam files you wish to process.\n\n```bash\nconda activate cashierenv\npycashier ./fastqs\n```\nFor additional parameters see `pycashier -h`.\n\nAs the files are processed two additional directories will be created `pipeline` and `outs`.\n\n**Note**: these can be specified with `-pd/--pipelinedir` and  `-o/--outdir`.\n\nCurrently all intermediary files generated as a result of the program will be found in `pipeline`.\n\nWhile the final processed files will be found within the `outs` directory.\n\n## Merging Files\n\nPycashier can now take paired end reads and perform a merging of the reads to produce a fastq which can then be used with pycashier's default feature.\n```bash\npycashier ./fastqs -m\n```\n\n## Processing Barcodes from 10X bam files\n\nPycashier can also extract gRNA barcodes along with 10X cell and umi barcodes.\n\nFirstly we are only interested in the unmapped reads. From the cellranger bam output you would obtain these reads using samtools.\n\n```\nsamtools view -f 4 possorted_genome_bam.bam > unmapped.sam\n```\n\nThen similar to normal barcode extraction you can pass a directory of these unmapped sam files to pycashier and extract barcodes. You can also still specify extraction parameters that will be passed to cutadapt as usual.\n\n*Note*: The default parameters passed to cutadapt are unlinked adapters and minimum barcode length of 10 bp.\n\n```\npycashier ./unmapped_sams -sc\n```\nWhen finished the `outs` directory will have a `.tsv` containing the following columns: Illumina Read Info, UMI Barcode, Cell Barcode, gRNA Barcode\n\n\n## Usage notes\nPycashier will **NOT** overwrite intermediary files. If there is an issue in the process, please delete either the pipeline directory or the requisite intermediary files for the sample you wish to reprocess. This will allow the user to place new fastqs within the source directory or a project folder without reprocessing all samples each time.\n- Currently, pycashier expects to find `.fastq.gz` files when merging and `.fastq` files when extracting barcodes. This behavior may change in the future.\n- If there are reads from multiple lanes they should first be concatenated with `cat sample*R1*.fastq.gz > sample.R1.fastq.gz`\n- Naming conventions:\n    - Sample names are extracted from files using the first string delimited with a period. Please take this into account when naming sam or fastq files.\n    - Each processing step will append information to the input file name to indicate changes, again delimited with periods.\n\n\n## Acknowledgments\n\n[Cashier](https://github.com/russelldurrett/cashier) is a tool developed by Russell Durrett for the analysis and extraction of expressed barcode tags.\nThis version like it's predecessor wraps around several command line bioinformatic tools to pull out expressed barcode tags.\n",
    'author': 'Daylin Morgan',
    'author_email': 'daylinmorgan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/brocklab/pycashier/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)

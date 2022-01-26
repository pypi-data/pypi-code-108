# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ncbitax2lin']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.3.1,<0.4.0',
 'pandas>=1.0.3,<2.0.0',
 'typing-extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['ncbitax2lin = ncbitax2lin.ncbitax2lin:main']}

setup_kwargs = {
    'name': 'ncbitax2lin',
    'version': '2.1.0',
    'description': 'A tool that converts NCBI taxonomy dump into lineages',
    'long_description': "# NCBItax2lin\n\n[![Downloads](https://pepy.tech/badge/ncbitax2lin/week)](https://pepy.tech/project/ncbitax2lin)\n\nConvert NCBI taxonomy dump into lineages. An example for [human\n(tax_id=9606)](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=9606)\nis like\n\n| tax_id | superkingdom | phylum   | class    | order    | family    | genus | species      | family1 | forma | genus1 | infraclass | infraorder  | kingdom | no rank            | no rank1     | no rank10            | no rank11 | no rank12 | no rank13 | no rank14 | no rank15     | no rank16 | no rank17 | no rank18 | no rank19 | no rank2  | no rank20 | no rank21 | no rank22 | no rank3  | no rank4      | no rank5   | no rank6      | no rank7   | no rank8     | no rank9      | parvorder  | species group | species subgroup | species1 | subclass | subfamily | subgenus | subkingdom | suborder    | subphylum | subspecies | subtribe | superclass | superfamily | superorder       | superorder1 | superphylum | tribe | varietas |\n|--------|--------------|----------|----------|----------|-----------|-------|--------------|---------|-------|--------|------------|-------------|---------|--------------------|--------------|----------------------|-----------|-----------|-----------|-----------|---------------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|---------------|------------|---------------|------------|--------------|---------------|------------|---------------|------------------|----------|----------|-----------|----------|------------|-------------|-----------|------------|----------|------------|-------------|------------------|-------------|-------------|-------|----------|\n| 9606   | Eukaryota    | Chordata | Mammalia | Primates | Hominidae | Homo  | Homo sapiens |         |       |        |            | Simiiformes | Metazoa | cellular organisms | Opisthokonta | Dipnotetrapodomorpha | Tetrapoda | Amniota   | Theria    | Eutheria  | Boreoeutheria |           |           |           |           | Eumetazoa |           |           |           | Bilateria | Deuterostomia | Vertebrata | Gnathostomata | Teleostomi | Euteleostomi | Sarcopterygii | Catarrhini |               |                  |          |          | Homininae |          |            | Haplorrhini | Craniata  |            |          |            | Hominoidea  | Euarchontoglires |             |             |       |          |\n\n### Install\n\nncbitax2lin requires python-3.7\n\n```\npip install -U ncbitax2lin\n```\n\n### Generate lineages\n\nFirst download taxonomy dump from NCBI:\n\n```bash\nwget -N ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz\nmkdir -p taxdump && tar zxf taxdump.tar.gz -C ./taxdump\n```\n\nThen, run ncbitax2lin\n\n```bash\nncbitax2lin --nodes-file taxdump/nodes.dmp --names-file taxdump/names.dmp\n```\n\nBy default, the generated lineages will be saved to\n`ncbi_lineages_[date_of_utcnow].csv.gz`. The output file can be overwritten with\n`--output` option.\n\n\n## FAQ\n\n**Q**: I have a large number of sequences with their corresponding accession\nnumbers from NCBI, how to get their lineages?\n\n**A**: First, you need to map accession numbers (GI is deprecated) to tax IDs\nbased on `nucl_*accession2taxid.gz` files from\nftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/. Secondly, you can trace a\nsequence's whole lineage based on its tax ID. The tax-id-to-lineage mapping is\nwhat NCBItax2lin can generate for you.\n\nIf you have any question about this project, please feel free to create a new\n[issue](https://github.com/zyxue/ncbitax2lin/issues/new).\n\n## Note on `taxdump.tar.gz.md5`\n\nIt appears that NCBI periodically regenerates `taxdump.tar.gz` and\n`taxdump.tar.gz.md5` even when its content is still the same. I am not sure how\ntheir regeneration works, but `taxdump.tar.gz.md5` will differ simply because\nof a different timestamp.\n\n## Used in\n\n* Mahmoudabadi, G., & Phillips, R. (2018). A comprehensive and quantitative exploration of thousands of viral genomes. ELife, 7. https://doi.org/10.7554/eLife.31955\n* Dombrowski, N. et al. (2020) Undinarchaeota illuminate DPANN phylogeny and the impact of gene transfer on archaeal evolution, Nature Communications. Springer US, 11(1). doi: 10.1038/s41467-020-17408-w. https://www.nature.com/articles/s41467-020-17408-w\n* Schenberger Santos, A. R. et al. (2020) NAD+ biosynthesis in bacteria is controlled by global carbon/ nitrogen levels via PII signaling, Journal of Biological Chemistry, 295(18), pp. 6165–6176. doi: 10.1074/jbc.RA120.012793. https://www.sciencedirect.com/science/article/pii/S0021925817482433\n* Villada, J. C., Duran, M. F. and Lee, P. K. H. (2020) Interplay between Position-Dependent Codon Usage Bias and Hydrogen Bonding at the 5' End of ORFeomes, mSystems, 5(4), pp. 1–18. doi: 10.1128/msystems.00613-20. https://msystems.asm.org/content/5/4/e00613-20\n* Byadgi, O. et al. (2020) Transcriptome analysis of amyloodinium ocellatum tomonts revealed basic information on the major potential virulence factors, Genes, 11(11), pp. 1–12. doi: 10.3390/genes11111252. https://www.mdpi.com/2073-4425/11/11/1252\n",
    'author': 'Zhuyi Xue',
    'author_email': 'zhuyi.xue2013@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zyxue/ncbitax2lin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

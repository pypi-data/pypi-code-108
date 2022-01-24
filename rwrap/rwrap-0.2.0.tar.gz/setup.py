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
    'version': '0.2.0',
    'description': 'A thin wrapper around rpy2 with strong opinions on how data types should be converted.',
    'long_description': '# rwrap\n\n[![PyPI](https://img.shields.io/pypi/v/rwrap.svg?style=flat)](https://pypi.python.org/pypi/rwrap)\n[![Tests](https://github.com/kpj/rwrap/actions/workflows/main.yml/badge.svg)](https://github.com/kpj/rwrap/actions/workflows/main.yml)\n\nA thin wrapper around [rpy2](https://rpy2.github.io/doc/latest/html/index.html) with strong opinions on how data types should be converted. This enables easy usage of R packages from Python with no boilerplate code.\n\n> Warning: still work-in-progress, issues and PRs welcome\n\n\n## Installation\n\n```bash\npip install rwrap\n```\n\n\n## Usage\n\n### Genomic Annotations\n\nAccessing Bioconductor\'s [biomaRt](https://bioconductor.org/packages/release/bioc/html/biomaRt.html) package can be as simple as follows:\n```python\nfrom rwrap import biomaRt\n\nbiomaRt\n## <module \'biomaRt\' from \'/Library/Frameworks/R.framework/Versions/4.1/Resources/library/biomaRt\'>\n\nsnp_list = ["rs7329174", "rs4948523", "rs479445"]\nensembl = biomaRt.useMart("ENSEMBL_MART_SNP", dataset="hsapiens_snp")\n\ndf = biomaRt.getBM(\n    attributes=["refsnp_id", "chr_name", "chrom_start", "consequence_type_tv"],\n    filters="snp_filter", values=snp_list, mart=ensembl\n)\n\nprint(df)  # pandas.DataFrame\n##    refsnp_id  chr_name  chrom_start     consequence_type_tv\n## 1   rs479445         1     60875960          intron_variant\n## 2   rs479445         1     60875960  NMD_transcript_variant\n## 3  rs4948523        10     58579338          intron_variant\n## 4  rs7329174        13     40983974          intron_variant\n```\n\n### Differential Gene Expression analysis workflow\n\nDifferentially expressed genes between conditions can be determined using [DESeq2](https://bioconductor.org/packages/release/bioc/html/DESeq2.html) and annotated with [biomaRt](https://bioconductor.org/packages/release/bioc/html/biomaRt.html):\n\n```python\nimport pandas as pd\nfrom rwrap import DESeq2, biomaRt, base, stats\n\n\nDESeq2\n## <module \'DESeq2\' from \'/Library/Frameworks/R.framework/Versions/4.1/Resources/library/DESeq2\'>\nbiomaRt\n## <module \'biomaRt\' from \'/Library/Frameworks/R.framework/Versions/4.1/Resources/library/biomaRt\'>\n\n\n# retrieve count data (https://trace.ncbi.nlm.nih.gov/Traces/sra/?study=SRP009615)\ndf_counts = pd.read_csv(\n    "http://duffel.rail.bio/recount/v2/SRP009615/counts_gene.tsv.gz", sep="\\t"\n).set_index("gene_id")\ndf_design = pd.DataFrame(\n    {"condition": ["1", "2", "1", "2", "3", "4", "3", "4", "5", "6", "5", "6"]}\n)\n\n# run differential gene expression analysis\ndds = DESeq2.DESeqDataSetFromMatrix(\n    countData=df_counts, colData=df_design, design=stats.as_formula("~ condition")\n)\ndds = DESeq2.DESeq(dds)\n\nres = DESeq2.results(dds, contrast=("condition", "1", "2"))\ndf_res = base.as_data_frame(res)\n\n# annotate result\nensembl = biomaRt.useEnsembl(biomart="genes", dataset="hsapiens_gene_ensembl")\ndf_anno = biomaRt.getBM(\n    attributes=["ensembl_gene_id_version", "gene_biotype"],\n    filters="ensembl_gene_id_version",\n    values=df_res.index,\n    mart=ensembl,\n).set_index("ensembl_gene_id_version")\n\ndf_res = df_res.merge(df_anno, left_index=True, right_index=True).sort_values("padj")\nprint(df_res.head())  # pd.DataFrame\n##                      baseMean  log2FoldChange     lfcSE      stat        pvalue          padj          gene_biotype\n## ENSG00000222806.1  158.010377       22.137400  2.745822  8.062214  7.492501e-16  2.853744e-11       rRNA_pseudogene\n## ENSG00000255099.1   65.879611       21.835651  2.915452  7.489627  6.906949e-14  1.315359e-09  processed_pseudogene\n## ENSG00000261065.1   92.351998       22.273400  3.144991  7.082182  1.419019e-12  1.351190e-08                lncRNA\n## ENSG00000249923.1  154.037908       18.364027  2.636083  6.966407  3.251381e-12  2.476772e-08                lncRNA\n## ENSG00000267658.1   64.371181      -19.545702  3.041247 -6.426871  1.302573e-10  8.268736e-07                lncRNA\n```\n\n### More examples\n\nCheck the `tests/` directory for more examples showing how to rewrite R scripts in Python.\n\n\n## Tests\n\nA comprehensive test suite aims at providing stability and avoiding regressions.\nThe examples in `tests/` are validated using `pytest`.\n\nRun tests as follows:\n\n```bash\n$ pytest tests/\n```\n',
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

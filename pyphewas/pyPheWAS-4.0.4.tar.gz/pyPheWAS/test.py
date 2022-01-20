from pyPhewasCorev2 import *
from pathlib import Path

path = Path('/Users/caileykerley/Documents/MASI/pyPheWAS/pyPheWAS_github/test_data/ICD')
phenotype = 'icds.csv'

phenotypes = get_icd_codes(path, phenotype, 0)
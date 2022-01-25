
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.gene_api import GeneApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from ncbi.datasets.openapi.api.gene_api import GeneApi
from ncbi.datasets.openapi.api.genome_api import GenomeApi
from ncbi.datasets.openapi.api.prokaryote_api import ProkaryoteApi
from ncbi.datasets.openapi.api.taxonomy_api import TaxonomyApi
from ncbi.datasets.openapi.api.version_api import VersionApi
from ncbi.datasets.openapi.api.virus_api import VirusApi

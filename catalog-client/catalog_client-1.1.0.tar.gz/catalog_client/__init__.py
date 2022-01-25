from .Selections import Selections
from .Catalog import Catalog, FatalError
from .Selections import ALL_TAGS as ALL_TAGS

import catalog_cli
def main():
    """Entry point for the application script"""
    catalog_cli.main()

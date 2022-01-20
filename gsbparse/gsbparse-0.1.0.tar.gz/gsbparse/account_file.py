"""Define the representation of a .gsb account file."""

import logging
from functools import cached_property
from typing import TextIO, Union

import defusedxml.ElementTree as ET
import pandas as pd

from gsbparse.account_section import (
    GsbSectionAccount,
    GsbSectionBudgetary,
    GsbSectionCategory,
    GsbSectionCurrency,
    GsbSectionFinancial_year,
    GsbSectionParty,
    GsbSectionReconcile,
    GsbSectionSubBudgetary,
    GsbSectionSubCategory,
    GsbSectionTransaction,
)

logger = logging.getLogger(__name__)


class AccountFile:
    """Representation of a parsed `.gsb` file."""

    def __init__(self, source: Union[str, TextIO]) -> None:
        """Initialize an AccountFile object, given its source (file object or path)."""
        self.source = source

    def __repr__(self) -> str:
        """Return a representation of an AccountFile object."""
        return f"AccountFile({self.source})"

    @cached_property
    def sections(self) -> list[dict]:
        """Parse a Grisbi file to extract its records into Python-friendly objects.

        `self.sections` is populated as a hash table mapping the various types
        (sections) of the XML tags with the records of that type (as a list of dicts).

        For users convenience, records of most useful sections (Account, Currency, etc.)
        are then assigned as attributes of the AccountFile as pandas.DataFrames.
        """
        # Initialize the collection of GsbSections
        sections = {}

        # Read the .gsb XML content
        tree = ET.parse(self.source)
        root = tree.getroot()

        # Instantiate each GsbSection with tags of the relevant type
        sections["Account"] = GsbSectionAccount(
            [child.attrib for child in root if child.tag == "Account"]
        )
        sections["Currency"] = GsbSectionCurrency(
            [child.attrib for child in root if child.tag == "Currency"]
        )
        sections["Party"] = GsbSectionParty(
            [child.attrib for child in root if child.tag == "Party"]
        )
        sections["Category"] = GsbSectionCategory(
            [child.attrib for child in root if child.tag == "Category"]
        )
        sections["Sub_category"] = GsbSectionSubCategory(
            [child.attrib for child in root if child.tag == "Sub_category"]
        )
        sections["Budgetary"] = GsbSectionBudgetary(
            [child.attrib for child in root if child.tag == "Budgetary"]
        )
        sections["Sub_budgetary"] = GsbSectionSubBudgetary(
            [child.attrib for child in root if child.tag == "Sub_budgetary"]
        )
        sections["Transaction"] = GsbSectionTransaction(
            [child.attrib for child in root if child.tag == "Transaction"]
        )
        sections["Financial_year"] = GsbSectionFinancial_year(
            [child.attrib for child in root if child.tag == "Financial_year"]
        )
        sections["Reconcile"] = GsbSectionReconcile(
            [child.attrib for child in root if child.tag == "Reconcile"]
        )

        return sections

    @cached_property
    def account(self) -> pd.DataFrame:
        """Return records of the Account section as a pd.DataFrame."""
        return self.sections["Account"].df

    @cached_property
    def currency(self) -> pd.DataFrame:
        """Return records of the Currency section as a pd.DataFrame."""
        return self.sections["Currency"].df

    @cached_property
    def party(self) -> pd.DataFrame:
        """Return records of the Party section as a pd.DataFrame."""
        return self.sections["Party"].df

    @cached_property
    def category(self) -> pd.DataFrame:
        """Return records of the Category section as a pd.DataFrame."""
        return self.sections["Category"].df

    @cached_property
    def subcategory(self) -> pd.DataFrame:
        """Return records of the Subcategory section as a pd.DataFrame."""
        return self.sections["Sub_category"].df

    @cached_property
    def budgetary(self) -> pd.DataFrame:
        """Return records of the Budgetary section as a pd.DataFrame."""
        return self.sections["Budgetary"].df

    @cached_property
    def subbudgetary(self) -> pd.DataFrame:
        """Return records of the Subbudgetary section as a pd.DataFrame."""
        return self.sections["Sub_budgetary"].df

    @cached_property
    def transaction(self) -> pd.DataFrame:
        """Return records of the Transaction section as a pd.DataFrame."""
        return self.sections["Transaction"].df

    @cached_property
    def financialyear(self) -> pd.DataFrame:
        """Return records of the Financialyear section as a pd.DataFrame."""
        return self.sections["Financial_year"].df

    @cached_property
    def reconcile(self) -> pd.DataFrame:
        """Return records of the Reconcile section as a pd.DataFrame."""
        return self.sections["Reconcile"].df

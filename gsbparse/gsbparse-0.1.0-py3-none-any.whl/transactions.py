"""Define a representation of transactions."""

from functools import cached_property
from typing import TextIO, Union

import pandas as pd

from gsbparse import AccountFile


class Transactions:
    """Represents transactions of a Grisbi file.

    The difference with an AccountFile["Transaction"] is that we here merge the
    different sections of the AccountFile together to replace "foreign keys" in
    the AccountFile["Transaction"].df records with their names, using the other
    sections of the .gsb file as lookup tables.

    Attributes:
        df (pd.DataFrame): Transactions of the Grisbi file
    """

    def __init__(self, source: Union[str, TextIO]) -> None:
        """Create the user-friendly Transactions df from an AccountFile instance."""
        self.source = source

    def __repr__(self) -> str:
        """Return a representation of an Transaction object."""
        return f"Transactions({self.source})"

    @cached_property
    def account_file(self) -> AccountFile:
        """Return the instantiated account file containing the transactions."""
        return AccountFile(self.source)

    @cached_property
    def _df(self) -> pd.DataFrame:
        """Return the transactions as a pd.DataFrame, with foreign keys merged."""
        return (
            self.account_file.transaction.pipe(self._add_account_details)
            .pipe(self._add_party_details)
            .pipe(self._add_currency_details)
            .pipe(self._add_subcategory_details)
            .pipe(self._add_category_details)
            .pipe(self._add_subbudgetary_details)
            .pipe(self._add_budgetary_details)
            .pipe(self._add_financialyear_details)
            .pipe(self._add_reconcile_details)
            .pipe(self._format_transactions_columns)
        )

    def get_transactions(
        self,
        columns: Union[list, dict, None] = None,
        ignore_mother_transactions: bool = False,
    ):
        """Return all or a subset of the transactions."""
        if ignore_mother_transactions:
            df = self._df[self._df["transaction_Br"] == "0"]
        else:
            df = self._df

        if columns is None:
            return df
        elif type(columns) == list:
            return df[columns]
        elif type(columns) == dict:
            return df[columns.keys()].rename(columns=columns)

    @staticmethod
    def prefix_column_names(
        df: pd.DataFrame, prefix: str, separator: str = "_"
    ) -> pd.DataFrame:
        """Add a leading prefix to all columns of a dataframe."""
        df.columns = [f"{prefix}{separator}{col}" for col in df.columns]

        return df

    def _add_account_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(
                df=self.account_file.account, prefix="account"
            ),
            how="left",
            left_on=["Ac"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Ac"])

    def _add_currency_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(
                df=self.account_file.currency, prefix="currency"
            ),
            how="left",
            left_on=["Cu"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Cu"])

    def _add_party_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(df=self.account_file.party, prefix="party"),
            how="left",
            left_on=["Pa"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Pa"])

    def _add_subcategory_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(
                df=self.account_file.subcategory, prefix="subcategory"
            ),
            how="left",
            left_on=["Ca", "Sca"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Sca"])

    def _add_category_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(
                df=self.account_file.category, prefix="category"
            ),
            how="left",
            left_on=["Ca"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Ca"])

    def _add_subbudgetary_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(
                df=self.account_file.subbudgetary, prefix="subbudgetary"
            ),
            how="left",
            left_on=["Bu", "Sbu"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Sbu"])

    def _add_budgetary_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(
                df=self.account_file.budgetary, prefix="budgetary"
            ),
            how="left",
            left_on=["Bu"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Bu"])

    def _add_financialyear_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(
                df=self.account_file.financialyear, prefix="financialyear"
            ),
            how="left",
            left_on=["Fi"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Fi"])

    def _add_reconcile_details(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.merge(
            type(self).prefix_column_names(
                df=self.account_file.reconcile, prefix="reconcile"
            ),
            how="left",
            left_on=["Re"],
            right_index=True,
            validate="m:1",
        ).drop(columns=["Re"])

    def _format_transactions_columns(self, transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions.rename(
            columns={
                col: f"transaction_{col}"
                for col in [
                    "Id",
                    "Dt",
                    "Dv",
                    "Am",
                    "Exb",
                    "Exr",
                    "Exf",
                    "Br",
                    "No",
                    "Pn",
                    "Pc",
                    "Ma",
                    "Ar",
                    "Au",
                    "Vo",
                    "Ba",
                    "Trt",
                    "Mo",
                ]
            }
        )

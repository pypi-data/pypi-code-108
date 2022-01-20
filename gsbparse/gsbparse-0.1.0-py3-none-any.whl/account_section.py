"""Define the representation of the sections of an account file."""

from abc import ABCMeta, abstractmethod
from functools import cached_property

import pandas as pd


class AccountSection(metaclass=ABCMeta):
    """Represent tags of a given type from a .gsb file.

    Grisbi files (.gsb) are XML files. They are constituted of tags of
    different types: e.g. "Account", "Currency", or "Transaction".

    This class represents, then, for example, all "Currency" tags in:
    - a list of a records, where each record is represented as a dict which keys are the
      attributes of the tag,
    - a pd.DataFrame, where columns represent the attributes of the tag, and rows
      represent the respective values of these attributes for a given tag.

    Example:
        <Currency Nb="1" Na="Euro" Co="€" Ico="EUR" Fl="2" />
        <Currency Nb="2" Na="United States Dollar" Co="$" Ico="USD" Fl="2" />
    will be represented as following pd.DataFrame:

           Nb                    Na Co  Ico  Fl
        0   1                  Euro  €  EUR   2
        1   2  United States Dollar  $  USD   2

    Attributes:
        records (list(dict)): Collection of records.
        df (pd.DataFrame): Attributes' values of a set of tags of a given type.
    """

    @property
    @abstractmethod
    def _idx_col(self):
        pass

    @property
    @abstractmethod
    def _name_col(self):
        pass

    @property
    @abstractmethod
    def _int_cols(self):
        pass

    @property
    @abstractmethod
    def _currency_cols(self):
        pass

    @property
    @abstractmethod
    def _date_cols(self):
        pass

    def __init__(self, records: list[dict]):
        """Build self.df from the list of XML tags attributes values.

        Args:
            records (list(dict)): Attributes values of XML tags of a given
            type.
        """
        self.records = records

    @cached_property
    def df(self):
        """Represent the list of records as a pd.DataFrame."""
        # Create df
        df = pd.DataFrame.from_records(self.records)

        # "Improve" df by casting correct columns dtype
        if self._idx_col is not None:
            df.set_index(self._idx_col, inplace=True)

        if self._int_cols:
            df[self._int_cols] = df[self._int_cols].apply(
                pd.to_numeric, downcast="integer"
            )

        if self._currency_cols:
            df[self._currency_cols] = df[self._currency_cols].apply(pd.to_numeric)

        if self._date_cols:
            df[self._date_cols] = df[self._date_cols].apply(
                pd.to_datetime, format="%m/%d/%Y", errors="coerce"
            )

        return df


class GsbSectionAccount(AccountSection):
    """Represent the <Account …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Account" tags.
    """

    @property
    def _idx_col(self):
        return ["Number"]

    @property
    def _name_col(self):
        return ["Name"]

    @property
    def _int_cols(self):
        return []

    @property
    def _currency_cols(self):
        return [
            "Initial_balance",
            "Minimum_wanted_balance",
            "Minimum_authorised_balance",
        ]

    @property
    def _date_cols(self):
        return []

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Account" tags
                attributes.
        """
        super(GsbSectionAccount, self).__init__(XML_tags_attributes_values)


class GsbSectionCurrency(AccountSection):
    """Represent the <Currency …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Currency" tags.
    """

    @property
    def _idx_col(self):
        return ["Nb"]

    @property
    def _name_col(self):
        return ["Na"]

    @property
    def _int_cols(self):
        return ["Fl"]

    @property
    def _currency_cols(self):
        return []

    @property
    def _date_cols(self):
        return []

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Currency" tags
                attributes.
        """
        super(GsbSectionCurrency, self).__init__(XML_tags_attributes_values)


class GsbSectionParty(AccountSection):
    """Represent the <Party …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Party" tags.
    """

    @property
    def _idx_col(self):
        return ["Nb"]

    @property
    def _name_col(self):
        return ["Na"]

    @property
    def _int_cols(self):
        return []

    @property
    def _currency_cols(self):
        return []

    @property
    def _date_cols(self):
        return []

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Party" tags
                attributes.
        """
        super(GsbSectionParty, self).__init__(XML_tags_attributes_values)


class GsbSectionCategory(AccountSection):
    """Represent the <Category …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Category" tags.
    """

    @property
    def _idx_col(self):
        return ["Nb"]

    @property
    def _name_col(self):
        return ["Na"]

    @property
    def _int_cols(self):
        return []

    @property
    def _currency_cols(self):
        return []

    @property
    def _date_cols(self):
        return []

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Category" tags
                attributes.
        """
        super(GsbSectionCategory, self).__init__(XML_tags_attributes_values)


class GsbSectionSubCategory(AccountSection):
    """Represent the <SubCategory …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "SubCategory" tags.
    """

    @property
    def _idx_col(self):
        return ["Nbc", "Nb"]

    @property
    def _name_col(self):
        return ["Na"]

    @property
    def _int_cols(self):
        return []

    @property
    def _currency_cols(self):
        return []

    @property
    def _date_cols(self):
        return []

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "SubCategory"
                tags attributes.
        """
        super(GsbSectionSubCategory, self).__init__(XML_tags_attributes_values)


class GsbSectionBudgetary(AccountSection):
    """Represent the <Budgetary …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Budgetary" tags.
    """

    @property
    def _idx_col(self):
        return ["Nb"]

    @property
    def _name_col(self):
        return ["Na"]

    @property
    def _int_cols(self):
        return []

    @property
    def _currency_cols(self):
        return []

    @property
    def _date_cols(self):
        return []

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Budgetary" tags
                attributes.
        """
        super(GsbSectionBudgetary, self).__init__(XML_tags_attributes_values)


class GsbSectionSubBudgetary(AccountSection):
    """Represent the <SubBudgetary …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "SubBudgetary" tags.
    """

    @property
    def _idx_col(self):
        return ["Nbb", "Nb"]

    @property
    def _name_col(self):
        return ["Na"]

    @property
    def _int_cols(self):
        return []

    @property
    def _currency_cols(self):
        return []

    @property
    def _date_cols(self):
        return []

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "SubBudgetary"
                tags attributes.
        """
        super(GsbSectionSubBudgetary, self).__init__(XML_tags_attributes_values)


class GsbSectionTransaction(AccountSection):
    """Represent the <Transaction …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Transaction" tags.
    """

    @property
    def _idx_col(self):
        return ["Nb"]

    @property
    def _name_col(self):
        return ["No"]

    @property
    def _int_cols(self):
        return []

    @property
    def _currency_cols(self):
        return ["Am", "Exr", "Exf"]

    @property
    def _date_cols(self):
        return ["Dt", "Dv"]

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Transaction"
                tags attributes.
        """
        super(GsbSectionTransaction, self).__init__(XML_tags_attributes_values)


class GsbSectionPayment(AccountSection):
    """Represent the <Payment …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Payment" tags.
    """

    @property
    def _idx_col(self):
        return ["Number"]

    @property
    def _name_col(self):
        return ["Name"]

    @property
    def _int_cols(self):
        return ["Sign", "Show_entry", "Automatic_number", "Current_number", "Account"]

    @property
    def _currency_cols(self):
        return []

    @property
    def _date_cols(self):
        return []

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Transaction"
                tags attributes.
        """
        super(GsbSectionTransaction, self).__init__(XML_tags_attributes_values)


class GsbSectionFinancial_year(AccountSection):
    """Represent the <Financial_year …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Financial_year" tags.
    """

    @property
    def _idx_col(self):
        return ["Nb"]

    @property
    def _name_col(self):
        return ["Na"]

    @property
    def _int_cols(self):
        return ["Sho"]

    @property
    def _currency_cols(self):
        return []

    @property
    def _date_cols(self):
        return ["Bdte", "Edte"]

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Transaction"
                tags attributes.
        """
        super(GsbSectionFinancial_year, self).__init__(XML_tags_attributes_values)


class GsbSectionReconcile(AccountSection):
    """Represent the <Reconcile …/> tags of a Grisbi file.

    Attributes:
        df (pd.DataFrame): Attributes' values of "Reconcile" tags.
    """

    @property
    def _idx_col(self):
        return ["Nb"]

    @property
    def _name_col(self):
        return ["Na"]

    @property
    def _int_cols(self):
        return ["Acc"]

    @property
    def _currency_cols(self):
        return ["Ibal", "Fbal"]

    @property
    def _date_cols(self):
        return ["Idate", "Fdate"]

    def __init__(self, XML_tags_attributes_values):
        """Build self.df from the list of XML tags attributes values.

        Args:
            XML_tags_attributes_values (list(dict)): Values of "Transaction"
                tags attributes.
        """
        super(GsbSectionReconcile, self).__init__(XML_tags_attributes_values)

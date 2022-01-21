"""
.. code:: python

    from ocdsextensionregistry import Codelist

Create a new codelist:

.. code:: python

    codelist = Codelist('+partyRole.csv')

Add codes to the codelist (you can provide any iterable, including a :code:`csv.DictReader`):

.. code:: python

    codelist.extend([
        {'Code': 'publicAuthority', 'Title': 'Public authority', 'Description': ''},
        {'Code': 'bidder', 'Title': 'Bidder', 'Description': ''}
    ])

Iterate over the codes in the codelist:

.. code:: python

    [code['Title'] for code in codelist]  # ['Public authority', 'Bidder']

Read the codelists' codes and fieldnames:

.. code:: python

    codelist.codes  # ['publicAuthority', 'bidder']
    codelist.fieldnames  # ['Code', 'Title', 'Description']

Determine whether the codelist adds or removes codes from another codelist:

.. code:: python

    codelist.patch  # True
    codelist.addend  # True
    codelist.subtrahend  # False

Get the name of the codelist it modifies:

.. code:: python

    codelist.basename  # 'partyRole.csv'
"""
import csv
from io import StringIO

from .codelist_code import CodelistCode


class Codelist:
    def __init__(self, name):
        self.name = name
        self.rows = []

    def __getitem__(self, index):
        return self.rows[index]

    def __iter__(self):
        for row in self.rows:
            yield row

    def __len__(self):
        return len(self.rows)

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return f'Codelist(name={self.name!r}, rows={self.rows!r})'

    def extend(self, rows, extension_name=None):
        """
        Adds rows to the codelist.
        """
        for row in rows:
            self.rows.append(CodelistCode(row, extension_name))

    def add_extension_column(self, field_name):
        """
        Adds a column for the name of the extension from which codes originate.
        """
        for row in self.rows:
            row[field_name] = row.extension_name

    def remove_deprecated_codes(self):
        """
        Removes deprecated codes and the Deprecated column.
        """
        self.rows = [row for row in self.rows if not row.pop('Deprecated', None)]

    def to_csv(self):
        """
        Returns the codelist as CSV content.
        """
        io = StringIO()

        writer = csv.DictWriter(io, fieldnames=self.fieldnames, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(self)

        return io.getvalue()

    @property
    def codes(self):
        """
        Returns the codes in the codelist.
        """
        return [row['Code'] for row in self.rows]

    @property
    def fieldnames(self):
        """
        Returns all fieldnames used in any rows.
        """
        fieldnames = {}
        for row in self.rows:
            for field in row:
                fieldnames[field] = True
        return list(fieldnames.keys())

    @property
    def basename(self):
        """
        If the codelist modifies another codelist, returns the latter's name. Otherwise, returns its own name.
        """
        if self.patch:
            return self.name[1:]
        return self.name

    @property
    def patch(self):
        """
        Returns whether the codelist modifies another codelist.
        """
        return self.name.startswith(('+', '-'))

    @property
    def addend(self):
        """
        Returns whether the codelist adds codes to another codelist.
        """
        return self.name.startswith('+')

    @property
    def subtrahend(self):
        """
        Returns whether the codelist removes codes from another codelist.
        """
        return self.name.startswith('-')

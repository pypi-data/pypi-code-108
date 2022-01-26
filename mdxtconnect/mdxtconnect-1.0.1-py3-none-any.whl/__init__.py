"""
MDXTConnect
===========

This package provides Jupyter Notebook and Lab users a convenenient way to retrieve data from the MDXT Connect platform
and Data Marketplace.

Configuration
-------------

Having installed the mdxtconnect package in your environment you will need to establish a configuration before accessing
the service.

From a temporary Notebook simply import the mdxtconnect package and use the `configure` call to set your configuration and
store it to a JSON file in your home directory for later use.

>>> import mdxtconnect
>>> mdxtconnect.configure(username='jrandall@example.com', passkey='MIGfMA0GCSqGSIb3DQEBAQUAA4GNA', url='https://data.mdxtechnology.com')

For more information look at the help for the mdxtconnect.configure function.

Once configuration has been set this way there is no need to perform this step again while the JSON file in your home directory
remains intact.


Retrieving Data
---------------

To retrieve data from the service you simply need to know the provider name and the name of the record (i.e. the instrument or symbol).

Armed with that information you can use the `get` call to retrieve data into a Pandas DataFrame ready for use in
your Notebook or Lab.

>>> import mdxtconnect
>>> mdxtconnect.get('NewChangeFX', 'EUR/JPY')

The example above retrieves Euro / Yen spot rate from NewChangeFX.

Refer to the help for the `get` function for further details. A similar `history` function is provided for retrieving historic data.

"""

from ._api import configure
from ._api import get
from ._api import history
from ._api import get_list

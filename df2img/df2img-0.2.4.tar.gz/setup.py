# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['df2img']

package_data = \
{'': ['*']}

install_requires = \
['kaleido==0.2.1', 'pandas>=1.0.0,<2.0.0', 'plotly>=5.3.1,<6.0.0']

extras_require = \
{'docs': ['ipykernel>=6.6.0,<7.0.0',
          'nbformat>=5.1.3,<6.0.0',
          'nbsphinx>=0.8.7,<0.9.0',
          'numpydoc>=1.1.0,<2.0.0',
          'pandoc>=1.1.0,<2.0.0',
          'sphinx>=4.3.0,<5.0.0',
          'sphinx-copybutton>=0.4.0,<0.5.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0']}

setup_kwargs = {
    'name': 'df2img',
    'version': '0.2.4',
    'description': 'Save a Pandas DataFrame as image',
    'long_description': '########################################\ndf2img: Save a Pandas DataFrame as image\n########################################\n\nWhat is it all about?\n*********************\n| Have you ever tried to save a ``pd.DataFrame`` into an image file? This is not a straightforward process at all. Unfortunately, ``pandas`` itself doesn\'t provide this functionality out of the box.\n\n| **df2img** tries to fill the gap. It is a Python library that greatly simplifies the process of saving a ``pd.DataFrame`` into an image file (e.g. ``png`` or ``jpg``).\n\nIt is a wrapper/convenience function in order to create a ``plotly`` Table. That is, one can use ``plotly``\'s styling function to format the table.\n\nDependencies\n************\n**df2img** has a limited number of dependencies, namely\n\n- ``pandas``\n- ``plotly``\n- ``kaleido``\n\nDocumentation\n*************\nAn extensive documentation is available at https://df2img.readthedocs.io/.\n\nQuickstart\n**********\n\nYou can install the package via ``pip``.\n\n.. code-block:: python\n\n    pip install df2img\n\nUsing ``poetry``?\n\n.. code-block:: python\n\n    poetry add df2img\n\nLet\'s create a simple ``pd.DataFrame`` with some dummy data:\n\n.. code-block:: python\n\n    import pandas as pd\n\n    import df2img\n\n    df = pd.DataFrame(\n        data=dict(\n            float_col=[1.4, float("NaN"), 250, 24.65],\n            str_col=("string1", "string2", float("NaN"), "string4"),\n        ),\n        index=["row1", "row2", "row3", "row4"],\n    )\n\n.. code-block:: python\n\n          float_col  str_col\n    row1       1.40  string1\n    row2        NaN  string2\n    row3     250.00      NaN\n    row4      24.65  string4\n\nBasics\n------\n\nSaving ``df`` into a png-file now takes just two lines of code including some styling out of the box.\n\n* First, we create a ``plotly`` figure.\n* Second, we save the figure to disk.\n\n.. code-block:: python\n\n    fig = df2img.plot_dataframe(df, fig_size=(500, 140))\n\n    df2img.save_dataframe(fig=fig, filename="plot1.png")\n\n\n.. image:: ./docs/source/images/plot1.png\n    :alt: plot1.png\n\nFormatting\n----------\n\nYou can control the settings for the header row via the ``tbl_header`` input argument. This accepts a regular ``dict``.\nThis ``dict`` can comprise various key/value pairs that are also accepted by ``plotly``. All available key/value pairs\ncan be seen at ``plotly``\'s website at https://plotly.com/python/reference/table/#table-header.\n\nLet\'s set the header row in a different color and size. Also, let\'s set the alignment to "left".\n\n.. code-block:: python\n\n    fig = df2img.plot_dataframe(\n        df,\n        tbl_header=dict(\n            align="left",\n            fill_color="blue",\n            font_color="white",\n            font_size=14,\n        ),\n        fig_size=(500, 140),\n    )\n\n.. image:: ./docs/source/images/plot2.png\n    :alt: plot2.png\n\n\nControlling the table body (cells) is basically the same. Just use the ``tbl_cells`` input argument, which happens to be\na ``dict``, too. See https://plotly.com/python/reference/table/#table-cells for all the possible key/value pairs.\n\nLet\'s print the table cell values in yellow on a green background and align them "right".\n\n.. code-block:: python\n\n    fig = df2img.plot_dataframe(\n        df,\n        tbl_cells=dict(\n            align="right",\n            fill_color="green",\n            font_color="yellow",\n        ),\n        fig_size=(500, 140),\n    )\n\n.. image:: ./docs/source/images/plot3.png\n    :alt: plot3.png\n\n\nYou can alternate row colors for better readability by using the ``row_fill_color`` input argument. Using HEX colors is also possible:\n\n.. code-block:: python\n\n    fig = df2img.plot_dataframe(\n        df,\n        row_fill_color=("#ffffff", "#d7d8d6"),\n        fig_size=(500, 140),\n    )\n\n.. image:: ./docs/source/images/plot4.png\n    :alt: plot4.png\n\n\nSetting the title will be controlled via the ``title`` input argument. You can find the relevant key/value pairs here:\nhttps://plotly.com/python/reference/layout/#layout-title.\n\nLet\'s put the title in a different font and size. In addition, we can control the alignment via the ``x`` key/value pair.\nIt sets the x (horizontal) position in normalized coordinates from "0" (left) to "1" (right).\n\n.. code-block:: python\n\n    fig = df2img.plot_dataframe(\n        df,\n        title=dict(\n            font_color="darkred",\n            font_family="Times New Roman",\n            font_size=24,\n            text="This is a title starting at the x-value x=0.1",\n            x=0.1,\n            xanchor="left",\n        ),\n        fig_size=(500, 140),\n    )\n\n.. image:: ./docs/source/images/plot5.png\n    :alt: plot5.png\n\n\nYou can also control relative column width via the ``col_width`` argument. Let\'s set the first column\'s width triple\nthe width of the third column and the second column\'s width double the width of the third column.\n\n.. code-block:: python\n\n    fig = df2img.plot_dataframe(\n        df,\n        col_width=[3, 2, 1],\n        fig_size=(500, 140),\n    )\n\n.. image:: ./docs/source/images/plot6.png\n    :alt: plot6.png\n\nContributing to df2img\n**********************\nAll bug reports and bug fixes, improvements to the documentation, or general ideas are welcome. Simply open an\n`issue <https://github.com/andreas-vester/df2img/issues>`_.\n',
    'author': 'Andreas Vester',
    'author_email': 'andreas@vester-online.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andreas-vester/df2img',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

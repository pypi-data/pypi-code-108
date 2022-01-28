# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['peatland_time_series']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0', 'numpy>=1.21.4,<2.0.0', 'pandas>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'peatland-time-series',
    'version': '0.1.2',
    'description': 'Analyze water retention in peatland from time series of precipitation and water table depth',
    'long_description': '# Peatland Time Series\n\nThis Python library contains functions which make it possible to analyze the water retention in a peatland from time series of precipitation and water table depth.\n\n## Installation\n```bash\npip install peatland-time-series\n```\n\n\n## Usage\n\n### Calculating the Specific Yield (Sy)\nThe `calculate_sy` function allows you to calculate the specific yield (Sy)\nfrom a time series of precipitation and the water table depth.\n\nLets take the example of a CSV file `./data/time-series.csv`, a time-series of precipitation and water table depth. The table must have at least the columns "date", "data_prec" and "data_wtd". There is an example of CSV file:\n```\ndate,data_prec,data_wtd\n2011-06-16 12:00:00,-0.098,0\n2011-06-16 13:00:00,-0.103,0\n2011-06-16 14:00:00,-0.109,10.3\n2011-06-16 15:00:00,-0.089,0\n2011-06-16 16:00:00,-0.084,0\n```\n\nTo calculate the Sy with other pertinent information:\n```python\nimport pandas\nfrom peatland_time_series import calculate_sy, read_time_series, visualization\n\ntime_series = read_time_series(\'./data/time-series.csv\')\n\nresult = calculate_sy(time_series)\nprint(results.head())\n```\nOutput:\n```\n       date_beginning         date_ending  precision_sum  max_wtd  min_wtd  durations  intensities  delta_h   depth        sy             idx_max             idx_min  accuracy_mean  accuracy_std\n0 2011-06-16 14:00:00 2011-06-16 14:00:00           10.3   -0.084   -0.109        0.5         20.6    0.025 -0.0965  0.412000 2011-06-16 16:00:00 2011-06-16 14:00:00       0.001333      0.003317\n1 2011-06-16 20:00:00 2011-06-16 21:00:00            3.7   -0.072   -0.100        1.0          3.7    0.028 -0.0860  0.132143 2011-06-16 23:00:00 2011-06-16 20:00:00       0.000000      0.000000\n2 2011-06-18 04:00:00 2011-06-18 05:00:00            1.2   -0.067   -0.084        1.0          1.2    0.017 -0.0755  0.070588 2011-06-18 04:00:00 2011-06-18 09:00:00       0.000000      0.000000\n3 2011-06-18 12:00:00 2011-06-18 12:00:00            0.4   -0.085   -0.094        0.5          0.8    0.009 -0.0895  0.044444 2011-06-18 12:00:00 2011-06-18 15:00:00       0.001556      0.002603\n4 2011-06-18 17:00:00 2011-06-18 17:00:00            1.6   -0.077   -0.087        0.5          3.2    0.010 -0.0820  0.160000 2011-06-18 18:00:00 2011-06-18 17:00:00       0.000667      0.001000\n```\n\n### Plotting water level in function of the time\n```python\ntime_series = read_time_series(\'path/to/time-series.csv\')\nsy = calculate_sy(time_series)\n\nvisualization.show_water_level(\n    time_series,\n    sy,\n    event_index=30,\n    time_before=pandas.Timedelta(hours=10),\n    time_after=pandas.Timedelta(hours=20)\n)\n```\nOutput:\n![water_level_by_time](https://github.com/ulaval-rs/peatland-time-series/blob/main/docs/images/water_level_by_time1.png)\n\nFor more information, see the `visualization.show_water_level` docstring. \n\n### Plot depth(Sy) \nIt is possible to plot the depth in function of Sy.\nNote that the Sy DataFrame can by filtered with the `filter_sy` function.\n```python\ntime_series = read_time_series(\'path/to/time-series.csv\')\nsy = calculate_sy(time_series=time_series)\n\nsy = filter_sy(sy, sy_min=0, delta_h_min=.01, precipitation_sum_min=10, precipitation_sum_max=100)\n\nvisualization.plot_depth(sy, label=\'Depth\', color=\'blue\')\nplt.legend()\n\nplt.show()\n```\nOutput:\n![depth_by_sy](https://github.com/ulaval-rs/peatland-time-series/blob/main/docs/images/depth_by_sy.png)\n\n\n### Interactively select data points.\nThe `visualization.show_selector` plots an interactive selector of the Depth(Sy)\ngraph. You can click on the data points you wish to exclude.\nA set of indexes of the selected data points is returned.\n```python\nselected_indexes = show_selector(sy)\n\n# selected_indexes\n{0, 100, 5, 101, 103, 46, 79, 47, 19, 24}\n```\n\n## Reference / Citation\nWe kindly ask users who produce scientific works to cite the following paper when using this library or algorithms :\nQuantification of peatland water storage capacity using the water table fluctuation method (https://doi.org/10.1002/hyp.11116)\n\n',
    'author': 'Gabriel Couture',
    'author_email': 'gacou54@ulaval.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ulaval-rs/peatland-time-series',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)

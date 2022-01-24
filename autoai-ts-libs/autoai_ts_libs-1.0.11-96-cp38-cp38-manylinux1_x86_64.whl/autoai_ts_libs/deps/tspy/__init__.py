"""
Entry point to time-series data-structure creation functions

Use

* time-series related data builders, e.g.

+-------------------------------+----------------------------------+
| function                      | description                      |
+===============================+==================================+
|:func:`autoai_ts_libs.deps.tspy.observation`       | create one observation           |
+-------------------------------+----------------------------------+
|:func:`autoai_ts_libs.deps.tspy.observations`      | create one observation collection|
+-------------------------------+----------------------------------+
|:func:`autoai_ts_libs.deps.tspy.time_series`       | create one time-series           |
+-------------------------------+----------------------------------+
|:func:`autoai_ts_libs.deps.tspy.multi_time_series` | create one multi-time-series     |
+-------------------------------+----------------------------------+
|:func:`autoai_ts_libs.deps.tspy.builder`           | create a time-series builder     |
+-------------------------------+----------------------------------+

* :py:mod:`autoai_ts_libs.deps.tspy.stream_time_series`  module : APIs for connecting stream data into time-series form

* :py:mod:`autoai_ts_libs.deps.tspy.stream_multi_time_series`  module : APIs for connecting stream data into multi-time-series form

* :py:mod:`autoai_ts_libs.deps.tspy.functions`  module : APIs for performing different time-series related operations, e.g. reduce, transforms, segment

* :py:mod:`autoai_ts_libs.deps.tspy.models`  module : APIs for loading/creating a time-series-based model

* :py:mod:`autoai_ts_libs.deps.tspy.forecasters`  module : APIs for different forecasting models

* :py:mod:`autoai_ts_libs.deps.tspy.exceptions`  module :

* :py:mod:`autoai_ts_libs.deps.tspy.ml`  module : APIs for different machine-learning methods

..

    * :py:mod:`autoai_ts_libs.deps.tspy.data_structures`  module : autoai_ts_libs.deps.tspy-specific data structure (internally used)

"""

__version__ = '2.2.3.0'

__all__ = []
#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

#__all__ = ['data_structures']
__all__ += ['time_series', 'multi_time_series', 'observation', 'record', 'observations', 'builder']
__all__ += ['forecasters', 'functions', 'stream_time_series', 'stream_multi_time_series', 'exceptions', 'ml']

from autoai_ts_libs.deps.tspy import data_structures
from . import forecasters, functions, stream_time_series, stream_multi_time_series, exceptions, ml
from autoai_ts_libs.deps.tspy.time_series import time_series
from autoai_ts_libs.deps.tspy.multi_time_series import multi_time_series
from autoai_ts_libs.deps.tspy.others import builder, observation, record
from autoai_ts_libs.deps.tspy.observations import observations

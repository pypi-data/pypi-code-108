# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nidaqmx',
 'nidaqmx._task_modules',
 'nidaqmx._task_modules.channels',
 'nidaqmx._task_modules.triggering',
 'nidaqmx.system',
 'nidaqmx.system._collections',
 'nidaqmx.system._watchdog_modules',
 'nidaqmx.system.storage']

package_data = \
{'': ['*']}

install_requires = \
['six>=1.16,<2.0']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['numpy==1.21.5',
                                                         'importlib_metadata>=4.10,<5.0'],
 ':python_version >= "3.8" and python_version < "4.0"': ['numpy>=1.22,<2.0']}

setup_kwargs = {
    'name': 'nidaqmx',
    'version': '0.5.8',
    'description': 'NI-DAQmx Python API',
    'long_description': '===========  =================================================================================================================================\nInfo         Contains a Python API for interacting with NI-DAQmx. See `GitHub <https://github.com/ni/nidaqmx-python/>`_ for the latest source.\nAuthor       National Instruments\n===========  =================================================================================================================================\n\nAbout\n=====\n\nThe **nidaqmx** package contains an API (Application Programming Interface)\nfor interacting with the NI-DAQmx driver. The package is implemented in Python.\nThis package was created and is supported by NI. The package is implemented as a \ncomplex, highly object-oriented wrapper around the NI-DAQmx C API using the \n`ctypes <https://docs.python.org/2/library/ctypes.html>`_ Python library.\n\n**nidaqmx** 0.5 supports all versions of the NI-DAQmx driver that ships with the\nC API. The C API is included in any version of the driver that supports it. The \n**nidaqmx** package does not require installation of the C header files.\n\nSome functions in the **nidaqmx** package may be unavailable with earlier \nversions of the NI-DAQmx driver. Visit the \n`ni.com/downloads <http://www.ni.com/downloads/>`_ to upgrade your version of \nNI-DAQmx.\n\n**nidaqmx** supports only the Windows operating system.\n\n**nidaqmx** supports CPython 3.7+ and PyPy3.\n\nInstallation\n============\n\nRunning **nidaqmx** requires NI-DAQmx or NI-DAQmx Runtime. Visit the\n`ni.com/downloads <http://www.ni.com/downloads/>`_ to download the latest version \nof NI-DAQmx.\n\n**nidaqmx** can be installed with `pip <http://pypi.python.org/pypi/pip>`_::\n\n  $ python -m pip install nidaqmx\n\n.. _usage-section:\n\nUsage\n=====\nThe following is a basic example of using an **nidaqmx.task.Task** object. \nThis example illustrates how the single, dynamic **nidaqmx.task.Task.read** \nmethod returns the appropriate data type.\n\n.. code-block:: python\n\n  >>> import nidaqmx\n  >>> with nidaqmx.Task() as task:\n  ...     task.ai_channels.add_ai_voltage_chan("Dev1/ai0")\n  ...     task.read()\n  ...\n  -0.07476920729381246\n  >>> with nidaqmx.Task() as task:\n  ...     task.ai_channels.add_ai_voltage_chan("Dev1/ai0")\n  ...     task.read(number_of_samples_per_channel=2)\n  ...\n  [0.26001373311970705, 0.37796597238117036]\n  >>> from nidaqmx.constants import LineGrouping\n  >>> with nidaqmx.Task() as task:\n  ...     task.di_channels.add_di_chan(\n  ...         "cDAQ2Mod4/port0/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)\n  ...     task.read(number_of_samples_per_channel=2)\n  ...\n  [[False, True], [True, True]]\n\nA single, dynamic **nidaqmx.task.Task.write** method also exists.\n\n.. code-block:: python\n\n  >>> import nidaqmx\n  >>> from nidaqmx.types import CtrTime\n  >>> with nidaqmx.Task() as task:\n  ...     task.co_channels.add_co_pulse_chan_time("Dev1/ctr0")\n  ...     sample = CtrTime(high_time=0.001, low_time=0.001)\n  ...     task.write(sample)\n  ...\n  1\n  >>> with nidaqmx.Task() as task:\n  ...     task.ao_channels.add_ao_voltage_chan("Dev1/ao0")\n  ...     task.write([1.1, 2.2, 3.3, 4.4, 5.5], auto_start=True)\n  ...\n  5\n\nConsider using the **nidaqmx.stream_readers** and **nidaqmx.stream_writers**\nclasses to increase the performance of your application, which accept pre-allocated\nNumPy arrays.\n\nFollowing is an example of using an **nidaqmx.system.System** object.\n\n.. code-block:: python\n\n  >>> import nidaqmx.system\n  >>> system = nidaqmx.system.System.local()\n  >>> system.driver_version\n  DriverVersion(major_version=16L, minor_version=0L, update_version=0L)\n  >>> for device in system.devices:\n  ...     print(device)\n  ...\n  Device(name=Dev1)\n  Device(name=Dev2)\n  Device(name=cDAQ1)\n  >>> import collections\n  >>> isinstance(system.devices, collections.Sequence)\n  True\n  >>> device = system.devices[\'Dev1\']\n  >>> device == nidaqmx.system.Device(\'Dev1\')\n  True\n  >>> isinstance(device.ai_physical_chans, collections.Sequence)\n  True\n  >>> phys_chan = device.ai_physical_chans[\'ai0\']\n  >>> phys_chan\n  PhysicalChannel(name=Dev1/ai0)\n  >>> phys_chan == nidaqmx.system.PhysicalChannel(\'Dev1/ai0\')\n  True\n  >>> phys_chan.ai_term_cfgs\n  [<TerminalConfiguration.RSE: 10083>, <TerminalConfiguration.NRSE: 10078>, <TerminalConfiguration.DIFFERENTIAL: 10106>]\n  >>> from enum import Enum\n  >>> isinstance(phys_chan.ai_term_cfgs[0], Enum)\n  True\n\nSupport / Feedback\n==================\n\nThe **nidaqmx** package is supported by NI. For support for **nidaqmx**, open \na request through the NI support portal at `ni.com <http://www.ni.com>`_.\n\nBugs / Feature Requests\n=======================\n\nTo report a bug or submit a feature request, please use the \n`GitHub issues page <https://github.com/ni/nidaqmx-python/issues>`_.\n\nInformation to Include When Asking for Help\n-------------------------------------------\n\nPlease include **all** of the following information when opening an issue:\n\n- Detailed steps on how to reproduce the problem and full traceback, if \n  applicable.\n- The python version used::\n\n  $ python -c "import sys; print(sys.version)"\n\n- The versions of the **nidaqmx**, numpy, six and enum34 packages used::\n\n  $ python -m pip list\n\n- The version of the NI-DAQmx driver used. Follow \n  `this KB article <http://digital.ni.com/express.nsf/bycode/ex8amn>`_ \n  to determine the version of NI-DAQmx you have installed.\n- The operating system and version, for example Windows 7, CentOS 7.2, ...\n\nDocumentation\n=============\n\nDocumentation is available `here <http://nidaqmx-python.readthedocs.io>`_.\n\nAdditional Documentation\n========================\n\nRefer to the `NI-DAQmx Help <http://digital.ni.com/express.nsf/bycode/exagg4>`_ \nfor API-agnostic information about NI-DAQmx or measurement concepts.\n\nNI-DAQmx Help installs only with the full version of NI-DAQmx.\n\nLicense\n=======\n\n**nidaqmx** is licensed under an MIT-style license (see\n`LICENSE <https://github.com/ni/nidaqmx-python/blob/master/LICENSE>`_).\nOther incorporated projects may be licensed under different licenses. All\nlicenses allow for non-commercial and commercial use.',
    'author': 'NI',
    'author_email': 'opensource@ni.com',
    'maintainer': 'Zach Hindes',
    'maintainer_email': 'zach.hindes@ni.com',
    'url': 'https://github.com/ni/nidaqmx-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

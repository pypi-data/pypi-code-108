#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
This module is a wrapper around LibTiePie SDK devices; see
https://www.tiepie.com/en/libtiepie-sdk .

The device classes adds simplifications for starting of the device (using serial
number) and managing mutable configuration of both the device and oscilloscope's
channels. This includes extra validation and typing hints support.

Extra installation
~~~~~~~~~~~~~~~~~~

LibTiePie SDK library is available only on Windows and on Linux.

To use this LibTiePie SDK devices wrapper:

1. install the :code:`hvl_ccb` package with a :code:`tiepie` extra feature::

        $ pip install "hvl_ccb[tiepie]"

   this will install the Python bindings for the library.

2. install the library

    * on Linux: follow instructions in https://www.tiepie.com/en/libtiepie-sdk/linux ;
    * on Windows: the additional DLL is included in Python bindings package.

Troubleshooting
...............

On a Windows system, if you encounter an :code:`OSError` like this::

    ...
        self._handle = _dlopen(self._name, mode)
    OSError: [WinError 126] The specified module could not be found

most likely the :code:`python-libtiepie` package was installed in your
:code:`site-packages/` directory as a :code:`python-libtiepie-*.egg` file via
:code:`python setup.py install` or :code:`python setup.py develop` command. In such
case uninstall the library and re-install it using :code:`pip`::

    $ pip uninstall python-libtiepie
    $ pip install python-libtiepie

This should create :code:`libtiepie/` folder. Alternatively, manually move the folder
:code:`libtiepie/` from inside of the :code:`.egg` archive file to the containing it
:code:`site-packages/` directory (PyCharm's Project tool window supports reading and
extracting from :code:`.egg` archives).

"""
import sys

if sys.platform == 'darwin':
    import warnings

    warnings.warn("\n\n  LibTiePie SDK is not available for Darwin OSs\n")
else:
    try:
        from .generator import (  # noqa: F401
            TiePieGeneratorConfig,
            TiePieGeneratorSignalType,
            TiePieGeneratorMixin,
        )
        from .i2c import (  # noqa: F401
            TiePieI2CHostConfig,
            TiePieI2CHostMixin,
        )
        from .oscilloscope import (  # noqa: F401
            TiePieOscilloscope,
            TiePieOscilloscopeConfig,
            TiePieOscilloscopeResolution,
            TiePieOscilloscopeAutoResolutionModes,
        )
        from .base import (  # noqa: F401
            TiePieDeviceConfig,
            TiePieDeviceType,
            TiePieError,
            get_device_by_serial_number,
        )
        from .channel import (  # noqa: F401
            TiePieOscilloscopeChannelCoupling,
            TiePieOscilloscopeChannelConfig,
            TiePieOscilloscopeRange,
            TiePieOscilloscopeTriggerKind,
            TiePieOscilloscopeTriggerLevelMode,
        )
        from .device import (  # noqa: F401
            TiePieHS5,
            TiePieHS6,
            TiePieWS5,
        )
    except (ImportError, ModuleNotFoundError):
        import warnings

        warnings.warn(
            "\n\n  "
            "To use TiePie devices controllers or related utilities install LibTiePie"
            "\n  "
            "and install the hvl_ccb library with a 'tiepie' extra feature:"
            "\n\n  "
            "    $ pip install hvl_ccb[tiepie]"
            "\n\n"
        )

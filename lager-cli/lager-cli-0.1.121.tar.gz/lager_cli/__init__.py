"""
Lager CLI
----
A Command Line Interface for Lager Data
"""

__version__ = '0.1.121'

SUPPORTED_DEVICES = (
    'at91samdexx',
    'at91samdgxx',
    'at91samdxx',
    'at91sam4sxx',
    'at91sam4sd32x',
    'atsame70',
    'cc3220s',
    'cc3220sf',
    'cc3235sf',
    'efm32',
    'nrf52',
    'stm32f0x',
    'stm32f1x',
    'stm32f2x',
    'stm32f3x',
    'stm32f4x',
    'stm32f7x',
    'stm32g0x',
    'stm32g4x',
    'stm32h7x',
    'stm32h7x_dual_bank',
    'stm32l0',
    'stm32l0_dual_bank',
    'stm32l1',
    'stm32l1x_dual_bank',
    'stm32l4x',
    'stm32mp15x',
    'stm32w108xx',
    'stm32wbx',
    'stm32wlx',
    'stm32xl',
    'imxrt1050',
    'imxrt1064',
    'MIMXRT1064xxx5A',
    'MIMXRT1064xxx6A',
    'lpc54xx',
    'lpc55xx',
    'pic32mm',
)  # Empty docstring below is to suppress tuple docstring that would otherwise be printed by autodoc
"""
"""

SUPPORTED_INTERFACES = (
    'ftdi',
    'jlink',
    'cmsis-dap',
    'xds110',
    'stlink',
    'stlink-dap',
)

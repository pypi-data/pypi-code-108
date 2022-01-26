#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from pylspci.command import CommandBuilder, IDResolveOption
from pylspci.filters import DeviceFilter, SlotFilter


def get_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='Python wrapper for lspci',
    )
    parser.add_argument(
        '-i', '--pci-ids',
        help='Path to an alternate file to use as the PCI ID list.',
        required=False,
        type=Path,
        dest='pciids',
    )
    parser.add_argument(
        '-p', '--pci-map',
        help='Path to an alternate file to use as the '
             'kernel module mapping file.',
        required=False,
        type=Path,
        dest='pcimap',
    )

    filter_options = parser.add_argument_group(title='Filters')
    filter_options.add_argument(
        '-s',
        help='Filter devices by their slots. '
             'Any value can be omitted or set to * to disable filtering.',
        type=SlotFilter.parse,
        dest='slot_filter',
        metavar='[[domain:]bus:][device][.function]',
    )
    filter_options.add_argument(
        '-d',
        help='Filter devices by their type. '
             'Any value can be omitted or set to * to disable filtering.',
        type=DeviceFilter.parse,
        dest='device_filter',
        metavar='[vendor]:[device][:class]',
    )

    output_options = parser.add_argument_group(title='Output options')
    output_options.add_argument(
        '-v', '--verbose',
        help='Display more details about devices.',
        default=False,
        action='store_true',
        dest='verbose',
    )
    output_options.add_argument(
        '-k', '--kernel-modules',
        help='On Linux kernels above 2.6, include kernel drivers handling '
             'each device and kernel modules able to handle them. Implies -v.',
        default=False,
        action='store_true',
        dest='kernel_drivers',
    )
    output_options.add_argument(
        '-P', '-PP', '--bridge-paths',
        help='Include PCI bridge paths along with device IDs.',
        default=False,
        action='store_true',
        dest='bridge_paths',
    )

    output_modes = output_options.add_mutually_exclusive_group()
    output_modes.add_argument(
        '--json',
        help='Parse the lspci output and return JSON data.',
        action='store_true',
        default=True,
        dest='json',
    )
    output_modes.add_argument(
        '--raw',
        help="Return lspci's output directly, without parsing.",
        action='store_false',
        default=True,
        dest='json',
    )

    id_resolve_option = output_options.add_mutually_exclusive_group()
    id_resolve_option.add_argument(
        '--name-only',
        help='Only include device names. This is the default.',
        action='store_const',
        default=IDResolveOption.NameOnly,
        const=IDResolveOption.NameOnly,
        dest='id_resolve_option',
    )
    id_resolve_option.add_argument(
        '-n', '--id-only',
        help='Only include device IDs, without looking for names '
             'in the PCI ID file.',
        action='store_const',
        const=IDResolveOption.IDOnly,
        default=IDResolveOption.NameOnly,
        dest='id_resolve_option',
    )
    id_resolve_option.add_argument(
        '-nn', '--name-with-id',
        help='Include both device IDs and names.',
        action='store_const',
        const=IDResolveOption.Both,
        default=IDResolveOption.NameOnly,
        dest='id_resolve_option',
    )

    access_options = parser.add_argument_group(title='PCI access options')
    access_options.add_argument(
        '-O', '--option',
        help='Set PCI library access parameters. '
             'Use -O help to get a list of available parameters '
             'with their descriptions and default values.',
        action='append',
        dest='pcilib_params',
        metavar='KEY=VALUE',
    )
    access_exclusive = access_options.add_mutually_exclusive_group()
    access_exclusive.add_argument(
        '-A', '--access-method',
        help='PCI library access method to use. '
             'Use -A help to list available access methods.',
        dest='access_method',
        metavar='METHOD',
    )
    access_exclusive.add_argument(
        '-F', '--file',
        help='Use a hex dump file from a previous run of lspci instead of '
             'accessing real hardware.',
        dest='file',
        metavar='FILE',
    )
    access_exclusive.add_argument(
        '-H1',
        help='Access hardware using Intel configuration mechanism 1. '
             'Alias to -A intel-conf1.',
        action='store_const',
        const='intel-conf1',
        dest='access_method',
    )
    access_exclusive.add_argument(
        '-H2',
        help='Access hardware using Intel configuration mechanism 2. '
             'Alias to -A intel-conf2.',
        action='store_const',
        const='intel-conf2',
        dest='access_method',
    )
    return parser


def main() -> None:
    parser: argparse.ArgumentParser = get_parser()
    args: Dict[str, Any] = vars(parser.parse_args())

    json_output: bool = args.pop('json', True)
    kernel_modules: bool = args.pop('kernel_modules', False)
    access_method: Optional[str] = args.pop('access_method', None)
    pcilib_params = args.pop('pcilib_params', []) or []

    builder: CommandBuilder = CommandBuilder(**args)
    if kernel_modules:
        builder = builder.include_kernel_drivers()

    if access_method:
        if access_method.strip().lower() == 'help':
            builder = builder.list_access_methods()
        else:
            builder = builder.use_access_method(access_method)

    for param in pcilib_params:
        if param.strip().lower() == 'help':
            builder = builder.list_pcilib_params(raw=not json_output)
            break
        if '=' not in param:
            parser.error(
                'Invalid PCI access parameter syntax for {!r}'.format(param))
        key, value = map(str.strip, param.split('=', 2))
        builder = builder.with_pcilib_params(**{key: value})

    if json_output:
        builder = builder.with_default_parser()

    result = list(builder)
    if not json_output:  # Raw mode
        for item in result:
            print(item)
        return

    print(json.dumps([
        item if isinstance(item, str) else item.as_dict()
        for item in result
    ]))


if __name__ == '__main__':
    main()

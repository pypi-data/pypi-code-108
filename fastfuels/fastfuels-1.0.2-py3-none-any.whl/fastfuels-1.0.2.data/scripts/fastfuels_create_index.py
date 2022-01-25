#!python

"""
This script creates an index of FastFuels zarr files based on their extents.
"""

import argparse
import numcodecs
import os
import sys
import zarr


def parse_extent(extent, extent_fmt):
    if extent_fmt == '(x1, y1), (x2, y2)' and len(extent) == 4:
        return extent
    elif extent_fmt == '[[x1, y1], [x2, y2]]':
        return extent[0][0], extent[0][1], extent[1][0], extent[1][1]
    else:
        raise Exception(f'Unknown extent format: {extent_fmt}')


def read_input_fios(fios, relative):

    fio_files = []
    for fio_name in fios:

        if fio_name[0] != '/' and not relative:
            print('WARNING: not absolute path {fio_name},')

        try:
            fio_file = zarr.open(fio_name)

            if relative:
                fio_name = os.path.relpath(
                    fio_name, start=os.path.dirname(output))

            fio_files.append({
                'name': fio_name,
                'fio': fio_file
            })
        except:
            print(f'WARNING: Could not open {fio_name}')
            continue

    return fio_files


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', action='store_true',
                        help='Overwrite index if it exists.')
    parser.add_argument('-f', nargs=1, required=True, help='Name of index.')
    parser.add_argument('-i', nargs='+', help='Names of files to index.')
    parser.add_argument('-r', action='store_true', default=True,
                        help='Use relative paths instead of absolute.')
    parser.add_argument('-t', action='store_true',
                        help='Show contents of index.')
    parser.add_argument('-v', action='store_true', help='Turn on verbosity')

    args = vars(parser.parse_args())

    create = args['c']
    output = args['f'][0]
    fios = args['i']
    relative = args['r']
    contents = args['t']
    verbose = args['v']

    if not fios and not contents:
        print('Must specify either -i or -t')
        sys.exit(1)
    elif fios and contents:
        print('Cannot specify both -i and -t')
        sys.exit(1)

    if contents:
        print(f'contents of {output}:')

        z = zarr.open(output, mode='r')
        index = z['index']

        for i in range(len(index['name'])):
            print(index['name'][i], index['extent'][i])

        sys.exit(0)

    if create or not os.path.exists(output):
        print(f'creating {output}')
        z = zarr.open(output, mode='w')
        index = z.create_group('index')
        creating = True
    else:

        print(f'updating {output}')
        z = zarr.open(output, mode='a')
        index = z['index']
        creating = False

    fio_files = read_input_fios(fios, relative)

    if creating:
        names = index.create_dataset('name', shape=(len(fio_files)), dtype=str)
        extents = index.create_dataset('extent', shape=(len(fio_files)), dtype=object,
                                       object_codec=numcodecs.MsgPack())
        extent_fmts = index.create_dataset(
            'extent_fmt', shape=(len(fio_files)), dtype=str)

        min_x = 999999999
        min_y = 999999999
        max_x = -999999999
        max_y = -999999999

        i = 0
        proj = None

    else:

        names = index['name']
        extents = index['extent']
        extent_fmts = index['extent_fmt']

        i = len(names)

        names.resize(i + len(fio_files))
        extents.resize(i + len(fio_files))
        extent_fmts.resize(i + len(fio_files))

        min_x, min_y, max_x, max_y = parse_extent(
            z.attrs['extent'], z.attrs['extent_fmt'])

        proj = z.attrs['proj']
        res = z.attrs['resolution']
        units = z.attrs['units']

    for fio_entry in fio_files:

        fio_file = fio_entry['fio']

        if verbose:
            print(fio_entry['name'], fio_file.attrs['extent'])

        names[i] = fio_entry['name']
        extents[i] = fio_file.attrs['extent']
        extent_fmts[i] = fio_file.attrs['extent_fmt']

        x1, y1, x2, y2 = parse_extent(extents[i], extent_fmts[i])

        if x1 < min_x:
            min_x = x1
        if y1 < min_y:
            min_y = y1
        if x2 > max_x:
            max_x = x2
        if y2 > max_y:
            max_y = y2

        if not proj:
            proj = fio_file.attrs['proj']
            res = fio_file.attrs['resolution']
            units = fio_file.attrs['units']
        elif proj != fio_file.attrs['proj']:
            raise Exception('Cannot handle different projections.')
        elif res != fio_file.attrs['resolution']:
            raise Exception('Cannot handle different resolutions.')
        elif units != fio_file.attrs['units']:
            Exception('Cannot handle different units.')

        i += 1

    # print(min_x,min_y,max_x,max_y)
    z.attrs['extent'] = [[min_x, min_y], [max_x, max_y]]
    z.attrs['extent_fmt'] = '[[x1, y1], [x2, y2]]'
    z.attrs['proj'] = proj
    z.attrs['resolution'] = res
    z.attrs['units'] = units
    z = None

import numpy

dtype = numpy.dtype([
    ('sample', '<u8'),
    ('type', 'S1'),
    ('sequence', '<u8'),
    ('logical_index', '<u8'),
    ('direction', 'S1'),
    ('count_hint', '<u8'),
    ('flags', '<u8'),
])

def load_binary(f):
    return numpy.fromfile(f, dtype=dtype)
load = load_binary

if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description='print vortex marker log', formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('path', help='path to markers log')
    parser.add_argument('--count', '-c', type=int, help='number of records to show')
    parser.add_argument('--skip', '-s', type=int, help='number of records to skip')
    parser.add_argument('--pretty', '-p', action='store_true', help='show pretty output')

    args = parser.parse_args()

    markers = load(args.path)

    if args.skip is not None:
        markers = markers[args.skip:]
    if args.count is not None:
        markers = markers[:args.count]

    if args.pretty:
        import pandas
        pandas.set_option('display.max_rows', 10)
        markers = pandas.DataFrame(markers)
        print(markers)
    else:
        print(markers)

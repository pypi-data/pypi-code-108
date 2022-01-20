#!/usr/bin/env python3

import argparse
import csv
import re

def _parse_ranges(numbers: str):
    for x in numbers.split(','):
        x = x.strip()
        if x.isdigit():
            yield int(x)
        elif '-' in x:
            xr = x.split('-')
            yield from range(int(xr[0].strip()), int(xr[1].strip())+1)
        else:
            yield x

def main():
    parser = argparse.ArgumentParser(
        description="Tool to remove districts from a block equivalency csv. Either use --remove or --keep to determine which districts are in the output.")
    parser.add_argument(
        'blocks.csv',
        type=argparse.FileType('r'),
        help="Requires BLOCKID and DISTRICT fields.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--remove',
        type=str,
        help="List of districts to remove separated by commas. Can include ranges such as 1-10.")
    group.add_argument(
        '--keep',
        type=str,
        help="List of districts to keep separated by commas. Can include ranges such as 1-10.")
    parser.add_argument(
        'output-blocks.csv',
        type=argparse.FileType('w'),
        help="Output file for the block equivalency file with the districts removed.")

    args = parser.parse_args()

    if args.remove is not None:
        keep = False
        districts = set(map(str,_parse_ranges(args.remove)))
    else:
        keep = True
        districts = set(map(str,_parse_ranges(args.keep)))

    with vars(args)['output-blocks.csv'] as outputFile, vars(args)['blocks.csv'] as inputFile:
        writer = csv.DictWriter(
            outputFile,
            fieldnames=['BLOCKID','DISTRICT'])
        writer.writeheader()
        reader = csv.DictReader(inputFile)
        for row in reader:
            if not keep:
                if row['DISTRICT'] not in districts:
                    writer.writerow({
                        'DISTRICT': row['DISTRICT'],
                        'BLOCKID' : row['BLOCKID']
                        })
            else:
                if row['DISTRICT'] in districts:
                    writer.writerow({
                        'DISTRICT': row['DISTRICT'],
                        'BLOCKID' : row['BLOCKID']
                        })

main()

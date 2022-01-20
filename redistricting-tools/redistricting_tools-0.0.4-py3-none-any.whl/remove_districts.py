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
            raise ValueError(f"Unknown value specified: {x}")

def main():
    parser = argparse.ArgumentParser(
        description="Tool to remove districts from a block equivalency csv.")
    parser.add_argument(
        'blocks.csv',
        type=argparse.FileType('r'),
        help="Requires BLOCKID and DISTRICT fields.")
    parser.add_argument(
        '--districts',
        type=str,
        help="List of districts to remove separated by commas. Can include ranges such as 1-10.")
    parser.add_argument(
        'output-blocks.csv',
        type=argparse.FileType('w'),
        help="Output file for the block equivalency file with the districts removed.")

    args = parser.parse_args()

    districts = _parse_ranges(args.districts)

    with vars(args)['output-blocks.csv'] as outputFile, vars(args)['blocks.csv'] as inputFile:
        writer = csv.DictWriter(
            outputFile,
            fieldnames=['BLOCKID','DISTRICT'])
        writer.writeheader()
        reader = csv.DictReader(inputFile)
        for row in reader:
            if row['DISTRICT'] not in districts:
                writer.writerow({
                    'DISTRICT': row['DISTRICT'],
                    'BLOCKID' : row['BLOCKID']
                    })


# Takes any ranges, expands them, and prepends them
def expand_ranges(s):
    return re.sub(
        r'(\d+)-(\d+)',
        lambda match: ','.join(
            str(i) for i in range(
                int(match.group(1)),
                int(match.group(2)) + 1
            )   
        ),  
        s
    )

main()

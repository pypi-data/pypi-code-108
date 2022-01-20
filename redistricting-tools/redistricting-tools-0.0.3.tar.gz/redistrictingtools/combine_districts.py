#!/usr/bin/env python3

import argparse
import csv
import warnings

def main():
    parser = argparse.ArgumentParser(
        description="Tool to combine districts from two block equivalency csv files. This will ignore district 0 if it exists in either file.")
    parser.add_argument(
        'source-one.csv',
        type=argparse.FileType('r'),
        help="Requires BLOCKID and DISTRICT fields.")
    parser.add_argument(
        'source-two.csv',
        type=argparse.FileType('r'),
        help="Requires BLOCKID and DISTRICT fields.")
    parser.add_argument(
        'output-blocks.csv',
        type=argparse.FileType('w'),
        help="Output file for the block equivalency file with the districts combined.")

    args = parser.parse_args()

    blockIds = set()
    count = 0
    overlappingDistricts = set()


    with vars(args)['output-blocks.csv'] as outputFile, vars(args)['source-one.csv'] as sourceFileOne, vars(args)['source-two.csv'] as sourceFileTwo:
        writer = csv.DictWriter(
            outputFile,
            fieldnames=['BLOCKID','DISTRICT'])
        writer.writeheader()
        readerOne = csv.DictReader(sourceFileOne)
        readerTwo = csv.DictReader(sourceFileTwo)
        for row in readerOne:
            # ignore district 0 rows
            if row['DISTRICT'] == "0":
                continue
            writer.writerow({
                'DISTRICT': row['DISTRICT'],
                'BLOCKID' : row['BLOCKID']
                })
            blockIds.add(row['BLOCKID'])
        for row in readerTwo:
            # ignore district 0 rows
            if row['DISTRICT'] == "0":
                continue
            # check for any blockid dupes between files, only output non-dupes
            elif row['BLOCKID'] in blockIds:
                count += 1
                overlappingDistricts.add(row['DISTRICT'])
            else:
                writer.writerow({
                    'DISTRICT': row['DISTRICT'],
                    'BLOCKID' : row['BLOCKID']
                    })

    if count > 0:
        warnings.warn("Found {} duplicate BLOCKIDs, this means you have districts that overlap between the two files.".format(count))
        warnings.warn("Overlapping districts: {}".format(overlappingDistricts))

main()
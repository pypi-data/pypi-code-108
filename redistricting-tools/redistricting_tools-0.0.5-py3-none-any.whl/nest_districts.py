#!/usr/bin/env python3

import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description="Tool to nest districts from a block equivalency csv.")
    parser.add_argument(
        'blocks.csv',
        type=argparse.FileType('r'),
        help="Requires BLOCKID and DISTRICT fields.")
    parser.add_argument(
        'nestings.csv',
        type=argparse.FileType('r'),
        help="First column is the senate district and each following column is a nested house district.")
    parser.add_argument(
        'output-senate-blocks.csv',
        type=argparse.FileType('w'),
        help="Outputs BLOCKID and DISTRICT fields for nested senate districts")

    args = parser.parse_args()

    with vars(args)['nestings.csv'] as nestingsFile:
        nestingReader = csv.reader(nestingsFile)
        houseToSenateMap = {}
        for row in nestingReader:
            for index, district in enumerate(row):
                if index == 0:
                    senate = district
                else:
                    if district in houseToSenateMap:
                        raise ValueError("House district in nesting file maps to multiple senate districts.")
                    houseToSenateMap[district] = senate

    with vars(args)['output-senate-blocks.csv'] as outputFile, vars(args)['blocks.csv'] as inputFile:
        writer = csv.DictWriter(
            outputFile,
            fieldnames=['BLOCKID','DISTRICT'])
        writer.writeheader()
        reader = csv.DictReader(inputFile)
        for row in reader:
            if row['DISTRICT'] in houseToSenateMap:
                writer.writerow({
                    'DISTRICT': houseToSenateMap[row['DISTRICT']],
                    'BLOCKID' : row['BLOCKID']
                    })
main()

#!/usr/bin/env python3

import csv
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( 'csv_filename' )
    parser.add_argument( '-d', '--dirname' )
    args = parser.parse_args()

    filename = args.csv_filename
    dirname = args.dirname

    csvfile = open( filename, 'r' )
    reader = csv.reader( csvfile, delimiter=',' )

    for alumne, repo in reader :
        # alumne = alumne.split()
        # nom = ".".join([alumne[i] for i in [0,2]])
        nom = alumne

        repo = repo.replace("https://gitlab.com/", "git@gitlab.com:")

        print(nom, " => ", repo)
        if repo:
            subprocess.call(["git", "clone", repo, "{}/{}".format(dirname, nom)])

if __name__ == "__main__":
    main()

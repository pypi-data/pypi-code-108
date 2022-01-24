#!/usr/bin/python

import json
import os

import codacy_client
import codacy_converter
import codecov_client
import codecov_converter
import coveralls_client
import coveralls_converter

banner = """
  ______   .___  ___. .__   __.  __     .______       _______ .______     ______   .______     .___________. _______ .______
 /  __  \  |   \/   | |  \ |  | |  |    |   _  \     |   ____||   _  \   /  __  \  |   _  \    |           ||   ____||   _  \ 
|  |  |  | |  \  /  | |   \|  | |  |    |  |_)  |    |  |__   |  |_)  | |  |  |  | |  |_)  |   `---|  |----`|  |__   |  |_)  |
|  |  |  | |  |\/|  | |  . `  | |  |    |      /     |   __|  |   ___/  |  |  |  | |      /        |  |     |   __|  |      /
|  `--'  | |  |  |  | |  |\   | |  |    |  |\  \----.|  |____ |  |      |  `--'  | |  |\  \----.   |  |     |  |____ |  |\  \----.
 \______/  |__|  |__| |__| \__| |__|    | _| `._____||_______|| _|       \______/  | _| `._____|   |__|     |_______|| _| `._____|

<Experimental Python Version>

by João Esperancinha
"""

if __name__ == '__main__':
    f = open('coverage.json')
    data = json.load(f)
    f.close()

    print(banner)
    codecov_token = os.getenv('CODECOV_TOKEN')
    if codecov_token is not None:
        print("Processing Codecov reports...")
        codecov_report = codecov_converter.convert_coverage(data)
        print(codecov_client.send_report([json.dumps(codecov_report)]))
        print("Codecov reporting complete!")
    else:
        print("* CODECOV_TOKEN not configured.")

    coveralls_token = os.getenv('COVERALLS_REPO_TOKEN')
    if coveralls_token is not None:
        print("Processing Coveralls reports...")
        coveralls_report = coveralls_converter.convert_coverage(data)
        print(coveralls_client.send_report(json.dumps(coveralls_report)))
        print("Coveralls reporting complete!")
    else:
        print ("* COVERALLS_REPO_TOKEN not configured.")

    codacy_token = os.getenv('CODACY_PROJECT_TOKEN')
    if codacy_token is not None:
        print("Processing Codacy reports...")
        codacy_report = codacy_converter.convert_coverage(data)
        print(codacy_client.send_report([json.dumps(codacy_report)], codacy_converter.Language.PYTHON))
        print("Codacy reporting complete!")
    else:
        print ("* CODACY_PROJECT_TOKEN not configured.")

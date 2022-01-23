from sys import argv
from subprocess import run
from spl_covid import covidstats

args = argv[1:]
fp = f"{__file__[:-12]}/covid-data.xlsx"

if "open" in args: run(["open", fp], capture_output=False)
else: covidstats.main()
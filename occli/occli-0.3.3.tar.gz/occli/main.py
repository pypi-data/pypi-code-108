#!/usr/bin/env python3

import logging
import argparse
import requests
from datetime import datetime
from occli import search,colors

def occli():
	parser = argparse.ArgumentParser(description=f"{colors.white}Unofficial Command Line Interface for OpenCorporates{colors.reset}",epilog=f"{colors.white}OpenCorporates.com is a website that shares data on corporations under the copyleft Open Database License. Developed by {colors.green}Richard Mwewa{colors.white} | https://about.me/{colors.green}rly0nheart{colors.reset}")
	parser.add_argument("search",help=f"{colors.white}company name{colors.reset}")
	parser.add_argument("-o","--output",help=f"{colors.white}write output to a file{colors.reset}",metavar=f"{colors.white}path/to/file{colors.reset}")
	parser.add_argument("-v","--verbose",help=f"{colors.white}run occli in verbose mode (recommended){colors.reset}",dest="verbose", action="store_true")
	parser.add_argument("--version",version=f"{colors.white}v0.3.3 Released at 01:57PM CAT 2022-01-22 {colors.reset}",action="version")
	args = parser.parse_args()
	start_time = datetime.now()
	api = f"https://api.opencorporates.com/v0.4.8/"
	if args.verbose:
		logging.basicConfig(format=f"{colors.white}[{colors.green}~{colors.white}] %(message)s{colors.reset}",level=logging.DEBUG)
		
	while True:
		try:
			if args.search:
				search.search(args,api)
				break
			else:
				exit(f"{colors.white}occli: try {colors.green}occli --h{colors.white} or {colors.green}occli --help{colors.white} to view help message{colors.reset}")
				
		except KeyboardInterrupt:
		    if args.verbose:
		    	print(f"\n{colors.white}[{colors.red}x{colors.white}] Process interrupted with {colors.red}Ctrl{colors.white}+{colors.red}C{colors.reset}")
		    break
				
		except IndexError:
		    break
		    
		except Exception as e:
		    if args.verbose:
		    	print(f"{colors.white}[{colors.red}!{colors.white}] An error occured: {colors.red}{e}{colors.reset}")
		    
	if args.verbose:
		exit(f"{colors.white}[{colors.green}-{colors.white}] Finished in {colors.green}{datetime.now()-start_time}{colors.white} seconds.{colors.reset}")
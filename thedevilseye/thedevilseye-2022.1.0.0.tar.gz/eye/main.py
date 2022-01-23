import logging
import requests
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
from eye import search,colors,dump 
                                             
def thedevilseye():
	start_time = datetime.now()
	parser = argparse.ArgumentParser(description=f'{colors.white}Darkweb OSINT tool{colors.reset}',epilog=f'{colors.white}thedevilseye extracts information (.onion links, descriptions) from the {colors.red}darkweb{colors.white} without requiring a Tor network. Developed by Richard Mwewa | https://about.me/{colors.green}rly0nheart{colors.reset}')
	parser.add_argument('query', help=f'{colors.white}search query{colors.reset}')
	parser.add_argument('-i','--i2p', help=f'{colors.white}switch to i2p network search{colors.reset}', action='store_true')
	parser.add_argument('-d','--dump', metavar=f'{colors.white}path/to/filename{colors.reset}', help=f'{colors.white}dump output to a file{colors.reset}')
	parser.add_argument('--version',version=f'{colors.white}2022.1.0.0-hellfire Released on 24th January 2022{colors.reset}',action='version')
	parser.add_argument('-v','--verbose',help=f'{colors.white}enable verbosity{colors.reset}',action='store_true')
	args = parser.parse_args()
	if args.verbose:
		logging.basicConfig(format=f"{colors.white}[{colors.green}~{colors.white}] %(message)s{colors.reset}",level=logging.DEBUG)
	
	if args.i2p:
		uri = f'https://ahmia.fi/search/i2p/?q={args.query}'
	else:
		uri = f'https://ahmia.fi/search/?q={args.query}'
		
	while True:
		try:
			search.search(args,uri)
			break
			
		except KeyboardInterrupt:
		    if args.verbose:
		        print(f'\n{colors.white}[{colors.red}x{colors.white}] Process interrupted with {colors.red}Ctrl{colors.white}+{colors.red}C{colors.reset}')
		        break
		    break
		    
		except Exception as e:
		    if args.verbose:
		        print(f'{colors.white}[{colors.red}!{colors.white}] An error occur: {colors.red}{e}{colors.reset}')
	
	if args.verbose:
	    exit(f'{colors.white}[{colors.green}-{colors.white}] Finished in {colors.green}{datetime.now()-start_time}{colors.white} seconds.{colors.reset}')
	exit()
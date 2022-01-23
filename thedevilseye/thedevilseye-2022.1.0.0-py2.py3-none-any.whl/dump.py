from eye import colors

def dump(args,soup):
    with open(args.dump, 'w') as file:
        file.write(soup.ol.get_text())
        file.close()
    if args.verbose:
    	print(f'{colors.white}[{colors.green}+{colors.white}] Output dumped to {colors.green}{args.dump}{colors.reset}')
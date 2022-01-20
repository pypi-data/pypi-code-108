#!/usr/bin/env python3
"""
$@

Usage:
  $@ URL [-x] DEST

Options:
  URL   the url to download
  DEST  the destination file
  -x    make DEST executable
"""
import urllib.request, docopt, os, sys
opts = docopt.docopt(__doc__.replace('$@', sys.argv[0]),
                     version='1.0.0')
urllib.request.urlretrieve(opts['URL'], opts['DEST'])
if opts['-x']:
    os.system('chmod +x ' + opts['DEST'])

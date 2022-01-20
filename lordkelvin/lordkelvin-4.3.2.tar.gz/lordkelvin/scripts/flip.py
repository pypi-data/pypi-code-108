#!/usr/bin/env python3
"""
$@

flip the addresses, if they're out of order.

Usage:
  $@ CONTRACT1 CONTRACT2

Options:
  CONTRACT1  the 1st contract
  CONTRACT2  the 2nd contract
"""
import docopt, sys
opts = docopt.docopt(__doc__.replace('$@', sys.argv[0]),
                     version='1.0.0')
fn1, fn2 = opts['CONTRACT1'], opts['CONTRACT2']
fc1, fc2 = open(fn1).read(),  open(fn2).read()
if fc1.upper() > fc2.upper():
    with open(fn1,'w') as f: f.write(fc2)
    with open(fn2,'w') as f: f.write(fc1)
    pass

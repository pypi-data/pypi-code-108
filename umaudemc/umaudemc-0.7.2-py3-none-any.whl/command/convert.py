#
# Command-line format conversion subcommand
#

import os.path
import sys
import tempfile

from ..terminal import terminal as tmn
from ..common import maude


def convert(args):
	"""Convert subcommand"""

	maude.init()
	maude.load(args.input_file)

	m = maude.getCurrentModule()

	print(m)

	print('(VAR x y)')

	print('(RULES')

	for rl in m.getRules():
		print(f'\t{rl.getLhs()} -> {rl.getRhs()}')

	print(')')

	return 3

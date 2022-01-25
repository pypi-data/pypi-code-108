

import typing



def allItemsHaveEqualLength(listOfSequences) -> bool:
	it = iter(listOfSequences)
	firstLength = len(next(it))
	if not all( len(item) == firstLength for item in it ):
		return False
	return True
#

def allItemsHaveEqualLengthE(listOfSequences) -> int:
	it = iter(listOfSequences)
	firstLength = len(next(it))
	if not all( len(item) == firstLength for item in it ):
		raise Exception("Sequence contains components of different length!")
	return firstLength
#











import pc 




__all__ = ['pythagores']


def pythagores(p='x',b='x',h='x'):
	if p is not None and b is not None and h is not None:

		if p == 'x':
			return (pc.sqrt(pc.square(h) - pc.square(b)))
		if b == 'x':
			return (pc.sqrt(pc.square(h) - pc.square(p)))
		if h == 'x':
			return (pc.sqrt(pc.square(p) + pc.square(b)))


	else:

		return "Values Are None"










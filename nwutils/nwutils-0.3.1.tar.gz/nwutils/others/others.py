from typing import Callable

def tryFn(fn:Callable, N:int, *args, **kwargs):
	i = 0
	for i in range(N):
		try:
			return fn(*args, **kwargs)
		except Exception as e:
			print("[tryFn] Failed %d/%d. Function: %s. Error: %s" % (i + 1, N, fn, str(e)))
			continue
	assert False

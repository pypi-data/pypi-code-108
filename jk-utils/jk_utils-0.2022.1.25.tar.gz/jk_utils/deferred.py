

import os
import time
import threading





def run(delaySeconds:float, func, *args, **kwargs):
	assert isinstance(delaySeconds, (int,float))
	assert callable(func)

	def _threadFunc():
		time.sleep(delaySeconds)
		func(*args, **kwargs)
	#

	t = threading.Thread(target=_threadFunc)
	t.start()
#





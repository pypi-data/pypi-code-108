import numpy as np
import time
import threading

def split(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class Bar:
	def __init__(self, idx, x, y, z):
		self.idx = idx
		self.a = np.random.rand(x,y)
		self.b = np.random.rand(y,z)
		self.c = np.matmul(self.a,self.b)

class MyThread(threading.Thread):
	def __init__(self, sizes):
		threading.Thread.__init__(self)
		self.bars = []
		self.sizes = sizes
		self.currentNumberOfBars = 0
		self.maxNumberOfBars = len(sizes)

	def run(self):
		for idx, size in enumerate(self.sizes):
			bar = Bar(idx, *size)
			self.bars.append(bar)
			self.currentNumberOfBars += 1

	# @property
	def done(self):
		print(self.maxNumberOfBars, self.currentNumberOfBars)
		return self.maxNumberOfBars == self.currentNumberOfBars

class MAIN:
	def create(self):
		N = 10000	
		sizes = [np.random.randint(2,100,3) for i in range(N)]
		
		self.bars = []
		M = 4
		threads = []
		for size in split(sizes, M):
			threads.append(MyThread(size))
			threads[-1].start()
		for thread in threads:
			thread.join()

if __name__ == '__main__':
	main = MAIN()
	t0 = time.time()
	main.create()
	t1 = time.time()
	print(t1-t0)
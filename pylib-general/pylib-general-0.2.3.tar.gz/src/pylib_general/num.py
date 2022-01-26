def factorial(n):
  if n == 0:
    return 1
  else:
    return n * factorial(n - 1)

def sig(n):
	if n == 0:
		return 0
	else:
		return n + sig(n - 1)

def recpow(n):
	if n == 0:
		return 1
	else:
		return n ** recpow(n - 1)

def incr(n):
	return n + 1

def decr(n):
	return n - 1

def pow(n, p):
	if p == 0:
		return 1
	else:
		return n**p

def mod(n, d):
	return n % d

def _recur_fib(n):  
   if n <= 1:  
       return n  
   else:  
       return(_recur_fib(n-1) + _recur_fib(n-2))

def get_fib(terms):
	if terms <= 0:
		raise ValueError
	else:
		fib = []
		for i in range(terms):
			fib.append(_recur_fibo(i))
		return fib

pi = 22/7

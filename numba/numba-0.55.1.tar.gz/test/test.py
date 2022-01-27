from numba import jit
import foo

@jit(nopython=True)
def baz(x):
    y = 0
    for i in range(x):
        y += foo.bar(i)
    return y

if __name__ == "__main__":
    print (baz(10))

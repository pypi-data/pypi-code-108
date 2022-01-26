BIG = 10

from random import randrange

def find_rep(num):
    assert num%2 == 1 and num != 1
    d = num-1
    r = 0
    while d%2 == 0:
        r += 1
        d = d/2
    return r,d


def has_small_div(num):
    for i in range(2,min(BIG,num)):
        if num%i == 0:
            return True
    return False

def prime_test_Miller_Rabin(num, k = 1000):
    if num == 2:
        return True
    if has_small_div(num):
        return False
    r,d = find_rep(num)
    for i in range(k):
        a = randrange(2,num)
        if  pow(a,num -1,num) != 1:
            return False
        x = pow(a,d,num)
        if x == 1 or x == num-1:
            continue
        for i in range(r):
            x = pow(x,2,num)
            if x == num-1:
                continue
        return False
    
    return True
            

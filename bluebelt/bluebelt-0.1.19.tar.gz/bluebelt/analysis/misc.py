def gcd(*args):
    factor = 10**-min([Decimal(str(x)).as_tuple().exponent for x in args])
    
    result = np.gcd.reduce([int(x*factor) for x in args])
    return result/factor
#!/usr/bin/env python


def gcd(a,b):
    
    # set the variable atemp to the maximum of the two numbers.
    # Note that we take the absolute value of each of the numbers,
    # as this does not change the gcd.
    atemp = max(abs(a),abs(b))
    
    # similar with btemp, but the minimum.
    btemp = min(abs(a),abs(b))
    
    # let a be the maximum of the two, and b be the minimum of the two, 
    # where both are now positive, if they were not before
    a = atemp
    b = btemp
    
    # while b is non zero...
    while b > 0:
        # obtain the quotient of a/b...
        quotient = floor(a/b)
        # as well as the remainder of a/b...
        remainder = a % b
        # then, for the next step in the Euclidean Algorithm, set
        # a to be the current value of b, and set b to be the remainder 
        # obtained from the previous step, continue this process untill
        # the remainder is zero.
        a = b
        b = remainder
        
    # return the quotient, as this will be the greatest common divisor.
    return a



def gcd_full(a: int,b: int):
    # store the original values of a and b into the 
    # variables aOrig and bOrig, to be used at the end
    aOrig = a
    bOrig = b
    
    # let atemp be the maximum of the absolute values of a and b
    # let btemp be the minimum
    atemp = max(abs(a),abs(b))
    btemp = min(abs(a),abs(b))
    
    # reassign the max value to be a and the minimum value to be b
    a = atemp
    b = btemp
    
    # create a list to hold all of the quotients, there is no need to 
    # save all the remainders, as they are not used in the pseudocode 
    # above
    quotients = []
    
    # same as before, go through and perform the steps of the Euclidean
    # algorithm, only this time, save all of the quotients into the list
    # that we just defined.
    while b > 0:
        quotient = floor(a/b)
        remainder = a % b
        a = b
        b = remainder
        quotients.append(quotient)
    
    # let d, be the value of the gcd
    d = a
    
    # throw the very last equation (the one with no remainder)
    # away, since we do not use it in the pseudocode above
    quotients.pop()
    
    # set x and y to their initial values
    x = 1
    y = -quotients.pop()
    
    # set the count equal to one, this will be used to alternate which one of x and y
    # we change in each step
    count = 0
    
    # follow the pseudocode above until there are no longer any quotients left
    while len(quotients)!=0:
        if count % 2 == 0:
            x = x-quotients.pop()*y
        if count % 2 == 1:
            y = y-quotients.pop()*x
        
        count = count + 1
    
    # this part is a little messy (sorry about that), but test to see which linear 
    # combination of the original values of a and b give us the gcd, then
    # return those values
    if x*aOrig+y*bOrig==d:
        return [d,x,y]
    elif (-x)*aOrig+y*bOrig==d:
        return [d,-x,y]
    elif x*aOrig+(-y)*bOrig==d:
        return [d,x,-y]
    elif (-x)*aOrig+(-y)*bOrig==d:
        return [d,-x,-y]
    elif y*aOrig+x*bOrig==d:
        return [d,y,x]
    elif (-y)*aOrig+x*bOrig==d:
        return [d,-y,x]
    elif y*aOrig+(-x)*bOrig==d:
        return [d,y,-x]
    elif (-y)*aOrig+(-x)*bOrig==d:
        return [d,-y,-x]




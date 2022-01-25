# takes an integer and returns a list with all digits staring from ones, tens, hundreds etc
def digits_in_int(a):
    return [int(i) for i in str(a)[::-1]]

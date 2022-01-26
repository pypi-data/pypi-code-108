import string
import random


def get_code(digits_only = False, length = 6):
    # length of the string.
    S = length  
    # call random.choices() string module to find the string in Uppercase + numeric data.  
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))

    if digits_only:  
        ran = ''.join(random.choices(string.digits, k = S))

    return ran
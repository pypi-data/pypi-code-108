import random
import string

class skepeUtilities:

    def return_random(length: int, upper: bool=None, lower: bool=None):
        randomLetter = ""
        for x in range(length):
            if random.randint(1, 2) == 1:
                randomLetter += f"{random.choice(string.ascii_letters)}"
            else:
                randomLetter += f"{random.randint(0, 9)}"

        if upper and lower:
            return randomLetter

        if upper == True and (lower == False or lower == None):
            randomLetter = randomLetter.upper()
        elif (upper == False or upper == None) and lower == True:
            randomLetter = randomLetter.lower()

        return randomLetter

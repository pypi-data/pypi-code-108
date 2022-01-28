import numpy as np

def add_one(number):
    return number + 1

def add_two(n):
    return n + 2

def add_three(n):
    return n + 3

def add_random():
    rng = np.random.default_rng()
    return rng.integers(0, 100)


def main():
    welcome()
    
def welcome():
    print("Welcome!")


if __name__ == '__main__':
    main()

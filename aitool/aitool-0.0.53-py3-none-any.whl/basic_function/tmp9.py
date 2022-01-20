from aitool import get_functions, multi


def toy(x, y=1):
    return x, y


def bauble(x=1, y=2):
    return x+y


toy_functions = list(get_functions(toy, [1, [2, 3], {'x': 4}, {'x': 6, 'y': 7}]))
bauble_functions = list(get_functions(bauble, [None, -2, [-3], [6, -1], {'y': 4}]))
for result in multi(toy_functions+bauble_functions):
    print(result)
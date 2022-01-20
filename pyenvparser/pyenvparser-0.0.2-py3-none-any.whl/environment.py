import os


class EnvParser():

    def __init__(self):
        for k, v in os.environ.items():
            print(f'{k}={v}')
        super().__init__()

    def c2f(self, celcius):
        return (float(celcius) * 9/5) + 32

    def f2c(self, fahrenheit):
        return (float(fahrenheit) - 32) * 5/9
        
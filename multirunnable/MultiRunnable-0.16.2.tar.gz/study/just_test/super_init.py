class A:

    def __init__(self, param1, param2=None):
        self._param1 = param1
        self._param2 = param2


    def fun(self):
        print("This is fun in A.")
        print(f"This A parameter1: {self._param1}.")
        print(f"This A parameter2: {self._param2}.")


class B(A):

    # def __init__(self, param1, param2=None):
    #     super().__init__(param1, param2)
    #     self._param1 = param1
    #     self._param2 = param2

    def fun(self):
        print("This is fun in B.")
        print(f"This B parameter1: {self._param1}.")
        print(f"This B parameter2: {self._param2}.")


class C(A):

    # def __init__(self, param1, param2=None):
    #     # super().__init__(param1, param2)
    #     self._param1 = param1
    #     self._param2 = param2

    def fun(self):
        print("This is fun in C.")
        print(f"This C parameter1 with self: {self._param1}.")
        print(f"This C parameter2 with self: {self._param2}.")
        super(C, self).fun()
        print(f"This C parameter1 with super: {super()._param1}.")
        print(f"This C parameter2 with super: {super()._param2}.")


if __name__ == '__main__':

    b = B(param1="87", param2="777")
    b.fun()

    c = C(param1="87")
    c.fun()

from typing import Final


class SuperCls:

    _Cls_Var: Final[str] = "Not change"

    def print_fun(self):
        print(f"_Cls_Var: {self._Cls_Var}")


class Cls(SuperCls):

    _Cls_Var = "This is Cls not SuperCls."



if __name__ == '__main__':

    __cls = Cls()
    __cls.print_fun()

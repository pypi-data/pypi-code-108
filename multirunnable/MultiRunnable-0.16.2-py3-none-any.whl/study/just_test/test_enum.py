from enum import Enum


class TestObj(Enum):

    A = "a"
    B = "b"
    C = {"1": 1, "2": 2}


if __name__ == '__main__':

    __a = TestObj.A
    print(f"Type of TestObj.A: ", type(__a.value))
    print(f"Type of TestObj.A: ", type(__a.value) is str)

    __c = TestObj.C
    print(f"Type of TestObj.C: ", type(__c.value))
    print(f"Type of TestObj.C: ", type(__c.value) is dict)
    print("keys: ", tuple(__c.value.keys()))

    __b = TestObj.B
    print(f"Type of TestObj.B: ", type(__b))

    specific_enum = "A"
    selected_val: TestObj = getattr(TestObj, specific_enum)
    print("object: ", selected_val)
    print("object name: ", selected_val.name)
    print("object value: ", selected_val.value)

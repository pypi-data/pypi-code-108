class Calculate:
    """
    Class having all the arithmetic functions.
    """

    def add(self, num1, num2):
        return num1 + num2

    def sub(self, num1, num2):
        return num1 - num2

    def mul(self, num1, num2):
        return num1 * num2

    def div(self, num1, num2):
        return num1 / num2


def main():
    calculate = Calculate()

    num1 = input("Enter 1st number: ")
    num2 = input("Enter 2nd number: ")

    num1 = float(num1)
    num2 = float(num2)

    add_ans = calculate.add(num1, num2)
    sub_ans = calculate.sub(num1, num2)
    mul_ans = calculate.mul(num1, num2)
    div_ans = calculate.div(num1, num2)

    print("ADDITION IS: {}".format(add_ans))
    print("SUBTRACTION IS: {}".format(sub_ans))
    print("MULTIPLICATION IS: {}".format(mul_ans))
    print("DIVISION IS: {}".format(div_ans))


if __name__ == "__main__":
    main()

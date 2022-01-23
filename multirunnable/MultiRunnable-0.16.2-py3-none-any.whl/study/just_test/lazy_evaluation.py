import random


def chk_non_zero(i: int) -> bool:
    print("The value which be checking: ", i)
    return i > 0


test_list = [random.randrange(-10, 10) for _ in range(10)]

print("test_list: ", test_list)

print("+ all +")
all_result = all(map(chk_non_zero, test_list))
print("+ any +")
any_result = any(map(chk_non_zero, test_list))

print("all_result: ", all_result)
print("any_result: ", any_result)

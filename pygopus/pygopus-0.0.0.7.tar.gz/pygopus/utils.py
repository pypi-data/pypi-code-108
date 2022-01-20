# def int_to_colname(num: int) -> str:
#     ans = []

#     while columnNumber > 0:
#         a0 = (columnNumber - 1) % 26 + 1
#         ans.append(chr(a0 - 1 + ord("A")))
#         columnNumber = (columnNumber - a0) // 26
#     return "".join(ans[::-1])


# def colname_to_int(name: str):
#     ret = 0
#     for i in name:
#         ret = ret * 26 + ord(i) - 64
#     return ret


def int_to_colname(num: int) -> str:
    if num == 0:
        # return ""
        return "A"
    seq = []

    while num > 0:
        a0 = (num - 1) % 26 + 1
        seq.append(chr(a0 - 1 + ord("A")))
        num = (num - a0) // 26
    return "".join(seq[::-1])


def colname_to_int(name: str):
    if name == "":
        # return 0
        return 1
    ret = 0
    for i in name:
        ret = ret * 26 + ord(i) - 64
    return ret


def get_row_cells_axis(row_axis: int, length: int):
    return [f"{int_to_colname(i+1)}{row_axis}" for i in range(length)]


def get_col_cell_axis(col_axis: int, length: int):
    return [f"{int_to_colname(col_axis)}{i+1}" for i in range(length)]


# print(int_to_colname(56))
# print(colname_to_int("BD"))

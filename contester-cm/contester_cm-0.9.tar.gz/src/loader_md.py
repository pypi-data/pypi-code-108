import os


def load_md(statement_file):

    if not os.path.exists(statement_file):
        return False

    file = open(statement_file, "r", encoding="utf-8")
    lines = file.readlines()
    isOpenComment = False
    data = ""

    for line in lines:
        temp = ""

        # открывающий комментарий
        if line.__contains__("<!--"):
            isOpenComment = True

        if isOpenComment is False:
            data += line

            # закрывающий комментарий
        if line.__contains__("-->"):
            isOpenComment = False

    return data

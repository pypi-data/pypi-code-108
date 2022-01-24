def __read_header(index, data):

    result = ""

    if index < len(data) and data[index] != "#":
        return index, result

    index += 1
    result = "<b>"

    while index < len(data) and data[index] != '\n':
        result += data[index]

        index += 1

    result += "</b>"

    return index, result


def __read_sup(index, data):
    result = ""

    if index < len(data) and data[index] != "^":
        return index, result

    index += 2
    result = "<sup>"

    while index < len(data) and data[index] != "]":

        ans = __read_sup(index, data)

        index = ans[0]
        result += ans[1]

        if index < len(data) and data[index] != "]":
            result += data[index]
            index += 1

    result += "</sup>"
    index += 1

    return index, result


def __read_sub(index, data):
    result = ""

    if index < len(data) and data[index] != "@":
        return index, result

    index += 2
    result = "<sub>"

    while index < len(data) and data[index] != "]":

        ans = __read_sup(index, data)

        index = ans[0]
        result += ans[1]

        if index < len(data) and data[index] != "]":
            result += data[index]
            index += 1

    result += "</sub>"
    index += 1

    return index, result


def __read_italic(index, data):
    result = ""

    if index < len(data) and data[index] != "_":
        return index, result

    index += 1
    result = "<i>"

    while index < len(data) and data[index] != "_":

        ans = __read_bold(index, data)

        index = ans[0]
        result += ans[1]

        ans = __read_sup(index, data)

        index = ans[0]
        result += ans[1]

        ans = __read_sub(index, data)

        index = ans[0]
        result += ans[1]

        if index < len(data) and data[index] != "_":
            result += data[index]
            index += 1

    result += "</i>"
    index += 1

    return index, result


def __read_bold(index, data):
    result = ""

    if index < len(data) and data[index] != "$":
        return index, result

    index += 1
    result = "<b>"

    while index < len(data) and data[index] != "$":

        ans = __read_italic(index, data)

        index = ans[0]
        result += ans[1]

        ans = __read_sup(index, data)

        index = ans[0]
        result += ans[1]

        ans = __read_sub(index, data)

        index = ans[0]
        result += ans[1]

        if index < len(data) and data[index] != "$":
            result += data[index]
            index += 1

    result += "</b>"
    index += 1

    return index, result


def __read_text(index, data):
    result = ""

    while index < len(data) and data[index] != '`':

        # попытка прочитать заголовок
        ans = __read_header(index, data)

        index = ans[0]
        result += ans[1]

        # попытка прочитать курсив
        ans = __read_italic(index, data)

        index = ans[0]
        result += ans[1]

        # попытка прочитать жирный текст
        ans = __read_bold(index, data)

        index = ans[0]
        result += ans[1]

        # попытка прочитать степень
        ans = __read_sup(index, data)

        index = ans[0]
        result += ans[1]

        # попытка прочитать индекс
        ans = __read_sub(index, data)

        index = ans[0]
        result += ans[1]

        # читаем обычный текст

        if index < len(data):
            result += data[index]

        index += 1

    return index, result


def prepare_md(data):
    index = 0

    special_smb = [
        ["<=", " &#8804 "],
        [">=", " &#8805 "],
        ["!=", " &#8800 "],
        ["~=", " &#8776 "],
        ["+-", " &#177 "],
        ["<~", " &#8712 "],
        ["*", " &#183 "]
    ]

    # подготовка html условия задачи
    ans = __read_text(0, data)

    index = ans[0]
    html = ans[1]

    # замена специальных символов
    for smb in special_smb:
        html = html.replace(smb[0], smb[1])

    # вставка переносов строк
    html = html.replace("\n", "<br/>")
    data = data.replace("\n", "<br/>")

    # чтение тестов
    test_data = data[index:-1]
    test_data = test_data.replace("`input`", "---")
    test_data = test_data.replace("`output`", "---")
    test_data = test_data.replace("`end`", "---")

    test_data = test_data.split('---')

    i = 1
    tests = []

    while i < len(test_data):
        test_data[i] = test_data[i][5:-1]
        test_data[i + 1] = test_data[i + 1][5:-1]

        tests.append([test_data[i], test_data[i + 1]])

        i += 3

    return html, tests

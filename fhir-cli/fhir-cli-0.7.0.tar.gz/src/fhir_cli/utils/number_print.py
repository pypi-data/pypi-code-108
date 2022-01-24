def number_print(text: str):
    lines = text.split("\n")
    for index, line in enumerate(lines):
        lines[index] = f"{index + 1}. {line}"
    print("\n".join(lines))

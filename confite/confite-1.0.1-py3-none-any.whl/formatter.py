def format_multiline_string(
        text: str,
        break_line_character: str):
    lines_list: list[str] = text.split(
        break_line_character
    )
    multiline_text: str
    if len(lines_list) > 0:
        for index in range(len(lines_list) - 1):
            lines_list[index] += '\n'
    return lines_list

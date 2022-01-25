def snake_to_camel(string: str) -> str:
    string_array = string.split('_')
    result = []
    for idx, word in enumerate(string_array):
        if idx == 0:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    return ''.join(result)

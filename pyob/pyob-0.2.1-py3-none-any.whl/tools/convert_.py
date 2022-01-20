# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ CONVERT STRING TO PASCAL CASE
# └─────────────────────────────────────────────────────────────────────────────────────


def convert_string_to_pascal_case(string):
    """ Converts a strong to Pascal case """

    # Split string
    string = [s.strip() for s in string.split(" ")]

    # Capitalize each word
    string = [s[0].upper() + s[1:] for s in string if s]

    # Join string
    string = "".join(string)

    # Return string
    return string

def read_file_as_lines(s_file, s_encoding='utf-8'):
    """
    This method reads the file in text with the encodinf specified: ascii, utf-8 format.
    Note: Python3 will try to UTF-8 Decode binary and return "UnicodeDecodeError: 'utf-8' codec can't decode byte"
    :param s_file: The file path for the file to read
    :type s_file: str
    :return: b_result: Indicate success reading, a_s_result: The text of the file as an Array of lines
    :rtype boolean, String
    """
    a_s_result = []
    b_success = True

    try:

        with open(s_file, "r", encoding=s_encoding) as fp:
            for cnt, s_line in enumerate(fp):
                a_s_result.append(s_line)

    except FileNotFoundError:
        print("File not found")
    except IOError:
        print("IOError")
        b_success = False

    return b_success, a_s_result

b_success, a_s_result = read_file_as_lines("nonexisting")
print(b_success)
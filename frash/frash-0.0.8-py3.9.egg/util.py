import sys


def normalize_to_hex(input):
    if input in [".0", "0."]:
        return "0x0"
    elif (
        ("e" in input or "E" in input)
        and (float(input) >= 1 or float(input) == 0)
        and not ("e0" in input or "E0" in input)
    ):
        try:
            return hex(int(float(input)))
        except ValueError as ve:
            print(ve)
            sys.exit(-1)
    else:
        try:
            return hex(int(input))
        except ValueError:
            try:
                output = float.hex(float(input))
                out_arr = output.split("p")
                out_arr[0] = out_arr[0].rstrip("0")
                out_arr[1] = out_arr[1].lstrip("+")
                output = out_arr[0] + "p" + out_arr[1]
                return output
            except ValueError as ve:
                print(ve)
                sys.exit(-1)


def from_hex(input):
    try:
        output = float.fromhex(input)
        return f"{output:f}".rstrip("0").rstrip(".")
    except ValueError as ve:
        print(ve)
        sys.exit(-1)
    except OverflowError as oe:
        print(oe)
        sys.exit(-1)


def from_oct(input):
    try:
        return str(int(input, 0o10))
    except ValueError as ve:
        print(ve)
        sys.exit(-1)


def normalize_to_oct(input):
    try:
        return oct(int(input))
    except ValueError as ve:
        print(ve)
        sys.exit(-1)

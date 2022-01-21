import sys


def normalize_to_hex(input):
    if input in [".0", "0."]:
        return "0x0"
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
            except ValueError:
                print("Wrong input!")
                sys.exit(-1)


def from_hex(input):
    try:
        output = float.fromhex(input)
        return f"{output:f}".rstrip("0").rstrip(".")
    except ValueError:
        sys.exit(-1)

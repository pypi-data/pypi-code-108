import argparse


def main():
    parser = argparse.ArgumentParser(description="XOR any file")
    parser.add_argument("input", help="Input file")
    parser.add_argument("-k", default="0x00", action="store", help="key")
    parser.add_argument("-o", default="system.out", action="store", help="output file")
    args = parser.parse_args()

    try:
        key = int(args.k, 0x10)
        if key > 255:
            print("Key must be [0x00..0xff]")
        else:
            with open(args.input, "rb") as f:
                f2 = open(args.o, "wb")
                while True:
                    current_byte = f.read(1)
                    if not current_byte:
                        break
                    hexa = hex(current_byte[0] ^ key)[2:]
                    f2.write(bytes.fromhex(hexa if len(hexa) > 1 else "0" + hexa))
                f2.close()
    except ValueError as ve:
        print(ve)


if __name__ == "__main__":
    main()

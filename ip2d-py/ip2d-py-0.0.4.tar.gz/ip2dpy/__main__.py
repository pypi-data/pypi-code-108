from ipy2d import fun
import argparse


def main():
    parser = argparse.ArgumentParser(description="Convert some IPs to integers")
    parser.add_argument("ip", help="IP to convert")
    parser.add_argument("-i", action="store_true", help="Integer to convert")
    parser.add_argument("--hex", action="store_true", help="IPv6 Mode")
    parser.add_argument("-c", action="store_true", help="Compress IPv6 addresses")
    parser.add_argument(
        "-o", type=str, required=False, help="Output format: (b)in, (o)ct or (h)ex"
    )
    args = parser.parse_args()

    try:
        if args.hex:
            if args.i and args.c:
                try:
                    print(fun.to_6(int(args.ip), compressed=True))
                except ValueError:
                    try:
                        print(fun.to_6(int(args.ip, 0x10), compressed=True))
                    except ValueError:
                        print(fun.to_6(int(args.ip, 0o10), compressed=True))
            elif args.i:
                try:
                    print(fun.to_6(int(args.ip)))
                except ValueError:
                    try:
                        print(fun.to_6(int(args.ip, 0x10)))
                    except ValueError:
                        print(fun.to_6(int(args.ip, 0o10)))
            else:
                if args.o == "o" or args.o == "oct":
                    print(oct(fun.from_6(args.ip)))
                elif args.o == "h" or args.o == "x" or args.o == "hex":
                    print(hex(fun.from_6(args.ip)))
                elif args.o == "b" or args.o == "bin":
                    print(bin(fun.from_6(args.ip)))
                else:
                    print(fun.from_6(args.ip))
        else:
            if args.i:
                try:
                    print(fun.to_4(int(args.ip)))
                except ValueError:
                    try:
                        print(fun.to_4(int(args.ip, 0x10)))
                    except ValueError:
                        print(fun.to_4(int(args.ip, 0o10)))
            else:
                if args.o == "o" or args.o == "oct":
                    print(oct(fun.from_4(args.ip)))
                elif args.o == "h" or args.o == "x" or args.o == "hex":
                    print(hex(fun.from_4(args.ip)))
                elif args.o == "b" or args.o == "bin":
                    print(bin(fun.from_4(args.ip)))
                else:
                    print(fun.from_4(args.ip))
    except IndexError:
        parser.print_help()


if __name__ == "__main__":
    main()

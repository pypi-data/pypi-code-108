from ipy2d import fun
import argparse


def main():
    parser = argparse.ArgumentParser(description="Convert some IPs to integers")
    parser.add_argument("x")
    parser.add_argument("-i", action="store_true")
    parser.add_argument("--hex", action="store_true")
    parser.add_argument("-c", action="store_true")
    args = parser.parse_args()

    if args.hex:
        if args.i and args.c:
            try:
                print(fun.to_6(int(args.x), compressed=True))
            except ValueError:
                print(fun.to_6(int(args.x, 0x10), compressed=True))
        elif args.i:
            try:
                print(fun.to_6(int(args.x)))
            except ValueError:
                print(fun.to_6(int(args.x, 0x10)))
        else:
            print(fun.from_6(args.x))
    else:
        if args.i:
            try:
                print(fun.to_4(int(args.x)))
            except ValueError:
                print(fun.to_4(int(args.x, 0x10)))
        else:
            print(fun.from_4(args.x))


if __name__ == "__main__":
    main()

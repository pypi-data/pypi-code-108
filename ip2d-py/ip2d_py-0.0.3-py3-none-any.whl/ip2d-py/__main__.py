from ipy2d import fun
import argparse


def main():
    parser = argparse.ArgumentParser(description="Convert some IPs to integers")
    parser.add_argument("x")
    parser.add_argument("-i", action="store_true")
    parser.add_argument("--six", action="store_true")
    parser.add_argument("-c", action="store_true")
    args = parser.parse_args()

    if args.six:
        if args.i and args.c:
            print(fun.to_6(int(args.x), compressed=True))
        elif args.i:
            print(fun.to_6(int(args.x)))
        else:
            print(fun.from_6(args.x))
    else:
        if args.i:
            print(fun.to_4(int(args.x)))
        else:
            print(fun.from_4(args.x))


if __name__ == "__main__":
    main()

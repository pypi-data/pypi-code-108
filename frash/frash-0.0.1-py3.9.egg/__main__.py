import argparse


def main():
    parser = argparse.ArgumentParser(description="Juggling with hex")
    parser.add_argument("input", help="Input")
    parser.add_argument("-r", action="store_true", help="reverse")
    args = parser.parse_args()

    print(float.hex(args.input))


if __name__ == "__main__":
    main()

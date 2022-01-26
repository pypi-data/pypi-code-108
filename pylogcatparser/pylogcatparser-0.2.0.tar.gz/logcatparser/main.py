import argparse

from logcatparser.logCatParser import LogCatParser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='path', type=str, help='filepath')
    parser.add_argument("-f", "--format", type=str, help="provide log format", default="threadtime",
                        choices=['threadtime'])
    parser.add_argument("-o", "--output", type=str, help="output format", choices=["json"])
    args = parser.parse_args()
    parser = LogCatParser(args.format, args.path)
    parser.parse_file()

if __name__ == "__main__":
    main()

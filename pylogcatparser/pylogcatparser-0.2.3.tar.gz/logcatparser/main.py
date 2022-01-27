import argparse, json

from logcatparser.logCatParser import LogCatParser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='path', type=str, help='filepath')
    parser.add_argument("-o", '--output_filepath', type=str, help='output filepath', default=None)
    parser.add_argument("-f", "--log_format", type=str, help="provide log format", default="threadtime",
                        choices=['threadtime'])
    parser.add_argument("-of", "--output_format", type=str, help="output file format", choices=["json"])
    args = parser.parse_args()
    parser = LogCatParser(args.log_format)
    parser.parse_file(args.path)
    if args.output_filepath:
        parser.save_results(args.output_filepath)
    else:
        print(json.dumps(parser.get_parser_resume(), indent=1))


if __name__ == "__main__":
    main()

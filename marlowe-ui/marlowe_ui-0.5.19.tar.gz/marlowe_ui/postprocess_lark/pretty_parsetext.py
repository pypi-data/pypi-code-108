'''apply suitable parser according to filename
    when a filename is 
        .../00.(parser-name).txt

    mui_postprocess_lark.(parser-name).parser is apply
'''

import sys
import argparse
import pathlib
import re
import importlib
import json

def main(inputpath):
    m = re.compile(r'00\.(?P<parser>\w+)\.txt$').match(inputpath.name)

    if m is None:
        raise 'error in the type of filenam (00.(parser-name).txt)'

    parser_module = importlib.import_module('.'+m.group('parser'), 'marlowe_ui.postprocess_lark')

    with inputpath.open('rt') as f:
        obj = parser_module.parse(f.read(), debug=True)
        json.dump(obj, sys.stdout, indent=2)

if __name__ == '__main__':

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input', type=str, help='input block text, .../00.(parser-name).txt')

    args = argparser.parse_args()

    inputpath = pathlib.Path(args.input)

    main(inputpath)


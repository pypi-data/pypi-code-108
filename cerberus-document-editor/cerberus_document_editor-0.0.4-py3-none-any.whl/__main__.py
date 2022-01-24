import sys
import os
import argparse
import json
import cerberus_document_editor as cde
from cerberus_document_editor import yaml_parser

APP_NAME = 'Cerberus Document Editor'
DESCRIPTION='Document Editor for Cerberus Schema.'
parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('-v', '--version', action='version', version=cde.__version__)
parser.add_argument('-s', '--schema', metavar='JSON_FILENAME', type=str, default='.schema.yaml', help='Select external schema file.')
parser.add_argument('document', metavar='FILENAME', type=str, help='Filename to edit.')

def exit_with_message(message, exitcode=1):
    print(message, file=sys.stderr)
    sys.exit(exitcode)

def main():
    args = parser.parse_args()
    if not os.path.exists(args.schema):
        exit_with_message('Cannot find schema file. [args.schema]')
    schema_ext = os.path.splitext(args.schema)[1]

    with open(args.schema) as f:
        if schema_ext.lower() in ['.yaml', '.yml']:
            schema = yaml_parser.load(f)
        elif schema_ext.lower() == '.json':
            schema = json.load(f)
        else:
            exit_with_message('Not support schema file type.')

    doc_ext = os.path.splitext(args.document)[1]
    if not doc_ext.lower() in ['.yaml', '.yml', '.json']:
        exit_with_message('Not support document file type.')
    if os.path.exists(args.document):
        with open(args.document) as f:
            if doc_ext.lower() in ['.yaml', '.yml']:
                document = yaml_parser.load(f)
            elif doc_ext.lower() == '.json':
                document = json.load(f)
            else:
                exit_with_message('Cannot support schema file type.')
    else:
        document = {}

    if False:
        from cerberus_document_editor.validator import Validator
        from cerberus_kind import utils
        
        validator = Validator(schema, purge_unknown=True)
        import time

        b = time.time()
        print('validate:', validator.validate(document, normalize=False))
        print(utils.parse_error(validator.errors, with_path=True))
        print(json.dumps(validator.normalized(document), indent=2))
        #print(json.dumps(dict(validator.schema), indent=2))
        #validator.normalized_by_order()
        #print(json.dumps(validator.normalized_by_order(document), indent=2))
        #print(json.dumps(validator.normalized(document, ordered=True), indent=2))
        #print(json.dumps(validator.document, indent=2))
        print(f"{time.time()-b}s")
    else:
        app = cde.MainWindow(APP_NAME, pagestack=True)
        modified = app.run(cde.EditorPage(os.path.basename(args.document), schema, document))
        if modified:
            if doc_ext in ['.yaml', '.yml', '.json']:
                with open(args.document, 'wt') as f:
                    if doc_ext in ['.yaml', '.yml']:
                        f.write(yaml_parser.dump(modified))
                    elif doc_ext in ['.json']:
                        f.write(json.dumps(modified, indent=2))
            else:
                print(f'Cannot support file format.', file=sys.stderr)

if __name__ == '__main__':
    main()
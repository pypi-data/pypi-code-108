import sys
import argparse
from . import run_transform_inline
import json
from mlflow import start_run

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', help='infinstor|isstage?|isdemo?')
    parser.add_argument('--input_data_spec', help='input data spec')
    parser.add_argument('--xformname', help='name of transformation')
    args, unknown_args = parser.parse_known_args()
    print(str(unknown_args))
    kwa = dict()
    for ou in unknown_args:
        if (ou.startswith('--')):
            oup = ou[2:].split('=')
            if (len(oup) == 2):
                kwa[oup[0]] = oup[1]
    print(str(kwa))
    input_data_spec = json.loads(args.input_data_spec)
    if (len(kwa.items()) > 0):
        with start_run() as run:
            return run_transform_inline(args.service, run.info.run_id,
                input_data_spec, args.xformname, **kwa)
    else:
        with start_run() as run:
            return run_transform_inline(args.service, run.info.run_id,
                input_data_spec, args.xformname)

if __name__ == "__main__":
    main()

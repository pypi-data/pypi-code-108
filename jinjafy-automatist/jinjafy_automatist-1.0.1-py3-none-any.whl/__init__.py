import argparse, sys, json, time, os
from jinja2 import Template, DictLoader, Environment, FileSystemLoader


def main ():
    ap = argparse.ArgumentParser("jinjafy!")
    ap.add_argument("template")
    ap.add_argument("--columns", type=int, default=None, help="treat incoming data as text in this many columns and not json (the default behaviour)")
    ap.add_argument("--data", type=argparse.FileType('r'), default=sys.stdin)
    ap.add_argument("--nodata", default=False, action="store_true")
    ap.add_argument("--listkey", default="items", help="if incoming data is a list, give it this name for the template, default: items")
    ap.add_argument("--output", type=argparse.FileType('w'), default=sys.stdout)
    ap.add_argument("--set", nargs=2, default=None, action="append")
    args = ap.parse_args()
    # 2021-05-13: added nodata argument
    if not args.nodata:
        if args.columns:
            data = []
            for line in args.data:
                line = line.split(None, args.columns-1)
                if line:
                    data.append(line)
        else:
            data = json.load(args.data)
    else:
        data = {}

    tpath, tname = os.path.split(args.template)
    env = Environment(loader=FileSystemLoader(tpath))

    import jinjafy.filters
    for name, fn in jinjafy.filters.all.items():
        env.filters[name] = fn

    template = env.get_template(tname)
    if type(data) == list:
        # print ("Detected list, adding as {0}".format(args.listkey), file=sys.stderr)
        data = {
            args.listkey: data
        }

    if args.set:
        for key, value in args.set:
            # print ("Setting {0}={1}".format(key, value), file=sys.stderr)
            data[key] = value

    print (template.render(**data), file=args.output)

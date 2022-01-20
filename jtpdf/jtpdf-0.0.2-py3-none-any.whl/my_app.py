import argparse
import pdfkit

import os
from ._version import __version__
from .jtpscraper import getPage


def main(parser=argparse.ArgumentParser()):

    # print("Executing 'main()' from my app!")
    parser.add_argument("-v",
                        "--version",
                        action="store_true",
                        help="Shows the app version.")
    parser.add_argument("-u",
                        "--url",
                        type=str,
                        required=False,
                        help="url to scrape")
    parser.add_argument("-o",
                        "--output",
                        type=str,
                        required=False,
                        help="Name of output pdf file",
                        default="out.pdf")
    args = parser.parse_args()

    if args.version:
        return __version__
    elif args.url:
        return fetch(args.output, args.url)
    else:
        return "use -u to get url"


def fetch(out: str, url: str):
    dirname = os.path.dirname(os.path.abspath(__file__))
    filename = dirname + '/link.css'
    p = getPage(url)
    p.init()
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }
    pdfkit.from_file('temp.html', out,options=options)
    print("PDF Successfully Generated.")

from pathlib import Path
import argparse
import sys

from etap2pcap import etap
from etap2pcap import libusb
from etap2pcap import pcap


vendor_id = 0x326F
product_id = 0x0003


def main():
    args = _get_argparser().parse_args()
    with pcap.Writer(args.path) as writer:
        with libusb.Lib() as usb:
            with usb.open_device(vendor_id, product_id) as device:
                reader = etap.Reader(device)
                while True:
                    data = reader.read()
                    writer.write(data)


def _get_argparser():
    parser = argparse.ArgumentParser(
        prog='etap2pcap', description='Tibbo Ethernet Tap pcap logger')
    parser.add_argument(
        'path', metavar='PATH', type=Path, help='output .pcap path')
    return parser


if __name__ == '__main__':
    sys.exit(main())

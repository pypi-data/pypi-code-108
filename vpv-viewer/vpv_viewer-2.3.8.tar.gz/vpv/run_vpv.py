#! /usr/bin/env python3

import sys

if sys.version_info[0] < 3:
    sys.exit("VPV must me run with Python3. Exiting")

from PyQt5 import QtGui
from vpv.vpv_temp import Vpv
from vpv.common import log_path
from vpv import __version__
import logging
import traceback


def excepthook_overide(exctype, value, traceback_):
    """
    USed to override sys.xcepthook so we can log any ancaught Exceptions
    """
    logging.exception("""{} VPV encountered an uncaught erorr {}\n. Please email this log file to bit@har.mrc.ac.uk
    {}\n{}\n{}""".format('#' * 10, '#' * 10, exctype, value,
                         ''.join(traceback.format_tb(traceback_))))
    print(exctype, value, ''.join(traceback.format_tb(traceback_)))


def main():
    import argparse
    parser = argparse.ArgumentParser("Volume Phenptype Viewer")
    parser.add_argument('-v', '-volumes', dest='volumes', nargs='*', help='Volume paths seperated by spaces',
                        default=False)
    parser.add_argument('-hm', '-heatmaps', dest='heatmaps', nargs='*', help='Heatmap paths seperated by spaces',
                        default=False)
    parser.add_argument('-an', '-analysis', dest='analysis_zips', help='Analysis zip path',
                        default=False)
    # parser.add_argument('-l', '-loader', dest='loader_file', help='Pass in a loder toml file created by utils.data_loader.py',
    #                     default=False)
    args = parser.parse_args()

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(format='%(asctime)s: - %(module)s:%(lineno)d  - %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S %p',
                        level=logging.DEBUG, filename=log_path)

    logging.info('VPV v{} starting'.format(__version__))

    app = QtGui.QApplication(sys.argv)

    # Log all uncaught exceptions
    sys.excepthook = excepthook_overide

    ex = Vpv()

    if args.volumes:
        ex.load_volumes(args.volumes, 'vol')
        # Can't have heatmaps loaded without any volumes loaded first

        if args.heatmaps:
            ex.load_volumes(args.heatmaps, 'heatmap')

    if args.analysis_zips:
        ex.load_impc_analysis(args.analysis_zips)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



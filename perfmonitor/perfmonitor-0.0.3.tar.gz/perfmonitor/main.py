import sys
import time
import os
import signal

from perfmonitor.gpu_stats import get_gpu_state
from perfmonitor.gui import pretty_print_data
from perfmonitor.libstats import get_all_stats
import argparse

def signal_handler(sig, frame):
    """
    Clear screen and exit
    """
    os.system("CLS")
    sys.exit(0)

def run():
    args = parse_args()
    main(args.time, args.disable_gpu, args.clear_every)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Windows Performance Monitor CLI')
    parser.add_argument(
        '-t', '--time', help='Refresh every -t seconds.', type=int, default=2)
    parser.add_argument(
        '-d','--disable_gpu', help='Disable GPU stats.', action='store_true')
    parser.add_argument(
        '-c', '--clear_every', help='Clear screen every -c prints.', type=int, default=5)

    return parser.parse_args()

def main(resfresh_time=2, disable_gpu_stats=False, clear_every=5):
    signal.signal(signal.SIGINT, signal_handler)

    if sys.platform != "win32":
        print("ONLY WINDOWS SUPPORTED")
        exit(1)

    os.system("CLS")

    p_index = 0
    while 1:
        t = time.time()
        stats, loading_time = get_all_stats()
        min_rows = len(stats["cpu_percs"])//2 + 9

        if not disable_gpu_stats:
            gpu_state, gpu_load_time = get_gpu_state()
            min_rows += 8 if gpu_state is not None else 0
        else:
            gpu_state, gpu_load_time = None, None

        if p_index > clear_every:
            p_index = 0
            os.system("CLS")

        pretty_print_data(stats, gpu_state, loading_time, gpu_load_time, t, min_rows,
                          final_line=f"Press Ctrl+C to exit. Refreshing every {resfresh_time} seconds",
                          disable_gpu_stat=disable_gpu_stats)

        time.sleep(resfresh_time)
        p_index += 1

if __name__ == '__main__':
    run()

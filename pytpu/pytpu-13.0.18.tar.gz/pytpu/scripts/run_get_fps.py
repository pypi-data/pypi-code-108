import argparse
from pytpu.tools import get_fps


def main():
    parser = argparse.ArgumentParser(prog='run_get_fps',
                                     description='TPU performance measurement tool')

    parser.add_argument('program', nargs='?', help='Path to the program.tpu', type=str)
    parser.add_argument('-raw', nargs='?', help='Enable RAW mode without pre- and post-processing (default = False)',
                        type=int, default=False)
    parser.add_argument('-n_queries', nargs='?', help='Number of queries (default = 1000)', type=int, default=1000)
    parser.add_argument('-n_proc', nargs='?', help='Number of processes (default = 4)', type=int, default=4)

    args = parser.parse_args()

    get_fps(args.program, raw=bool(args.raw), n_queries=args.n_queries, n_proc=args.n_proc)

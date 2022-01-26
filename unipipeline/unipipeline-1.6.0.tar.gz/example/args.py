import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--type', dest='type', choices=('mem', 'kafka', 'rmq'), type=str)
parser.add_argument('--count', dest='produce_count', type=int, required=False, default=3)
parser.add_argument('--worker', dest='worker', type=str, required=False, default=None)

args = parser.parse_args()

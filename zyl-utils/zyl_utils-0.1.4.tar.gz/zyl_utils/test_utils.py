
import pandas as pd


def use_cmd_argument():
    import argparse

    parser = argparse.ArgumentParser(description='set some parameters')

    parser.add_argument('--', type=str, help='传入的数字',default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')

    args = parser.parse_args()

    # 获得integers参数
    print(args.integers)
    return args

    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print(args.accumulate(args.integers))
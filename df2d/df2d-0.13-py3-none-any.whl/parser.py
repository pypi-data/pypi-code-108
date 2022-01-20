import argparse
import os


def add_arguments(parser):
    parser.add_argument(
        "-j",
        "--workers",
        default=8,
        type=int,
        metavar="N",
        help="number of data loading workers (default: 4)",
    )
    parser.add_argument(
        "--epochs",
        default=200,
        type=int,
        metavar="N",
        help="number of total epochs to run",
    )
    # hyper-parameters
    parser.add_argument(
        "--train-batch",
        default=6,
        type=int,
        metavar="N",
        help="train batchsize",
        dest="train_batch",
    )
    parser.add_argument(
        "--test-batch",
        default=96,
        type=int,
        metavar="N",
        dest="test_batch",
        help="test batchsize",
    )
    parser.add_argument(
        "--lr",
        "--learning-rate",
        default=2.5e-4,
        type=float,
        metavar="LR",
        help="initial learning rate",
    )
    parser.add_argument(
        "--momentum", default=0, type=float, metavar="M", help="momentum"
    )
    parser.add_argument(
        "--weight-decay",
        "--wd",
        default=0,
        type=float,
        metavar="W",
        help="weight decay (default: 0)",
    )
    parser.add_argument(
        "--schedule",
        type=int,
        nargs="+",
        default=[25, 40, 70],
        help="Decrease learning rate at these epochs.",
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.1,
        help="LR is multiplied by gamma on schedule.",
    )

    parser.add_argument(
        "--num_classes", type=int, default=19,
    )

    parser.add_argument(
        "-s",
        "--stacks",
        default=2,
        type=int,
        metavar="N",
        help="Number of hourglasses to stack",
    )
    parser.add_argument(
        "--features",
        default=128,
        type=int,
        metavar="N",
        help="Number of features in the hourglass",
    )
    parser.add_argument(
        "-b",
        "--blocks",
        default=1,
        type=int,
        metavar="N",
        help="Number of residual modules at each location in the hourglass",
    )
    parser.add_argument("--inplanes", default=64, type=int, metavar="N")
    parser.add_argument("--stride", default=2, type=int, metavar="N")
    return parser


def create_parser():
    parser = argparse.ArgumentParser(description="DF3D Training")
    return add_arguments(parser)

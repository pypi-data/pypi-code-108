import os
import sys
import argparse

from localization_checker.parser import actualize_languages


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path')
    parser.add_argument('-m', '--main_lang', default='en')

    return parser


if __name__ == '__main__':
    parser = create_parser()
    arguments = parser.parse_args(sys.argv[1:])
    if not arguments.path:
        raise AttributeError('Path to source directory (-p or --path argument) is required')
    if not os.path.exists(arguments.path):
        raise AttributeError('Path to source directory does not exist')

    actualize_languages(arguments.path, arguments.main_lang)

    print('Compare and complete all languages is done.')

#! /usr/bin/env python3
def version() -> str:
    from sonusai import __version__
    return __version__


def main():
    from sonusai import logger
    logger.info('SonusAI {}'.format(version()))


if __name__ == '__main__':
    main()

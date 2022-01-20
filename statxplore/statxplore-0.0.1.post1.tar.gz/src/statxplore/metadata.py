import logging
import argparse

import statxplore.http_session
import statxplore.utils
import statxplore.objects

LOGGER = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Define arguments
    parser.add_argument('-k', '--api_key', help='API key')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-i', '--info', action='store_true',
                        help='Provides general information about the Stat-Xplore instance you are connecting to.')
    parser.add_argument('-r', '--rate_limit', action='store_true',
                        help='Show information about the limit that applies to you, how many requests you have remaining, and the length of time before the rate limit will be reset.')
    parser.add_argument('-s', '--schema',
                        help='Provides information about all the Stat-Xplore datasets that are available to you, and their fields and measures.')

    return parser.parse_args()


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = statxplore.http_session.StatSession(
        api_key=args.api_key or statxplore.utils.load_api_key())

    if args.rate_limit:
        statxplore.utils.jprint(session.rate_limit)
    elif args.schema:
        statxplore.utils.jprint(
            statxplore.objects.Schema(args.schema).get(session))
    else:
        statxplore.utils.jprint(session.info)


if __name__ == '__main__':
    main()

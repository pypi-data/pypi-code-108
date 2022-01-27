import argparse

from efemarai import Session

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-file",
        "-c",
        default=None,
        help="Path where to store SDK configuration.",
    )
    args = parser.parse_args()

    Session._user_setup(config_file=args.config_file)

if __name__ == "__main__":
    main()

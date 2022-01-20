import fire

from superannotate_schemas.bin.interface import CLIInterface


def main():
    fire.Fire(CLIInterface)


if __name__ == "__main__":
    main()

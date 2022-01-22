def version() -> str:
    from sonusai import __version__
    return __version__


def main():
    print(version())


if __name__ == '__main__':
    main()

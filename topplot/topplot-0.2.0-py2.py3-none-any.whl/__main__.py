import pkg_resources

from .app import App


def main():
    try:
        version = pkg_resources.require("topplot")[0].version
    except pkg_resources.DistributionNotFound:
        version = "unknown (dev?)"

    topplot = App(version=version)
    topplot.run()


if __name__ == "__main__":
    main()

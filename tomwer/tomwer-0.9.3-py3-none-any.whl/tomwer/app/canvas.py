import sys
from tomwer.app.canvas_launcher.mainwindow import OMain as QMain
from tomwer.core.utils.resource import increase_max_number_file


def main(argv=None):
    increase_max_number_file()
    return QMain().run(argv)


if __name__ == "__main__":
    sys.exit(main())

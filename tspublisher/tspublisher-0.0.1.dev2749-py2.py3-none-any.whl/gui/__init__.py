
import sys
from Qt import QtWidgets

from publisher.gui.channel_editor import ChannelEditor


def channel_editor():
    app = QtWidgets.QApplication(sys.argv)
    dialog = ChannelEditor()
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    channel_editor()

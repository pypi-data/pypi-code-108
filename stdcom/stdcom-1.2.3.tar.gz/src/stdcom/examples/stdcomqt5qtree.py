import sys, os

from PyQt5.QtWidgets import QDialog, QApplication

if __name__ == "__main__":

    current = os.path.dirname(os.path.realpath(__file__))

    # Getting the parent directory name
    # where the current directory is present.
    parent = os.path.dirname(current)

    # adding the parent directory to
    # the sys.path.
    sys.path.append(parent)

    import stdcomqt5widget

    def callBack(selected):
        print("Selected ", selected)

    L = "//Ball/oo", "One.ttt",  "One.123", "Two.ccc", "Three.uuu", "Four.ggg", "Five.123", "Five.444"

    app = QApplication(sys.argv)
    w = stdcomqt5widget.stdcomqt5qtree(None, callBack)
    w.AddNames(L)
    w.show()
    sys.exit(app.exec_())

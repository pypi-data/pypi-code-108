from fakts import Fakts
from qtpy import QtCore, QtWidgets
from koil.qt import FutureWrapper


class QtFakts(QtWidgets.QDialog, Fakts):
    loaded_signal = QtCore.Signal()
    deleted_signal = QtCore.Signal()
    error_signal = QtCore.Signal(Exception)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle("Retrieval Wizard")

        self.showf = FutureWrapper()
        self.showf.wire(self.handle_show)
        self.showfref = None

        self.hidef = FutureWrapper()
        self.hidef.wire(self.handle_hide)

        self.title = QtWidgets.QLabel("Konfig Wizard")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title)
        self.subtitle = QtWidgets.QLabel("These are the grants we are able to use")
        self.layout.addWidget(self.subtitle)

        for grant in self.grants:
            grant_title = QtWidgets.QLabel(grant.__class__.__name__)
            self.layout.addWidget(grant_title)

        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.clicked.connect(self.on_start)
        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)

    def handle_show(self, ref, *args, **kwargs):
        self.show()
        self.showfref = ref

    def handle_hide(self, ref, *args, **kwargs):
        self.close()
        self.hidef.resolve(ref, None)

    def on_start(self):
        self.showf.resolve(self.showfref, None)

    async def aload(self):
        await self.showf.acall()  # await user starts
        try:
            nana = await super().aload()
            self.loaded_signal.emit()
            await self.hidef.acall()
            return nana
        except Exception as e:
            self.error_signal.emit(e)
            await self.hidef.acall()
            raise e

    async def adelete(self):
        nana = await super().adelete()
        self.deleted_signal.emit()
        return nana

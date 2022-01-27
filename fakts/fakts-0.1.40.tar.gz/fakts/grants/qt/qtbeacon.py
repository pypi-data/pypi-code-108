from qtpy.QtCore import Signal
from fakts.grants.beacon import BeaconGrant
from koil.koil import get_current_koil
from fakts.beacon.beacon import FaktsEndpoint
from fakts.grants.base import GrantException, FaktsGrant
from fakts.beacon import EndpointDiscovery, FaktsRetriever
from qtpy import QtWidgets
import asyncio
import logging


logger = logging.getLogger(__name__)


class RetrieveDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Check your Broswer")
        self.button = QtWidgets.QPushButton("Cancel")
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)


class SelfScanWidget(QtWidgets.QWidget):
    user_endpoint = Signal(FaktsEndpoint)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.lineEdit = QtWidgets.QLineEdit()
        self.addButton = QtWidgets.QPushButton("Scan")

        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.addButton)
        self.addButton.clicked.connect(self.on_add)
        self.setLayout(self.layout)

    def on_add(self):
        host = self.lineEdit.text()
        url = f"http://{host}/setupapp"
        endpoint = FaktsEndpoint(url=url, name="Self Added")
        self.user_endpoint.emit(endpoint)


class UserCancelledException(GrantException):
    pass


class QtSelectableBeaconGrant(BeaconGrant, QtWidgets.QDialog):
    new_endpoint = Signal(FaktsEndpoint)
    show_signal = Signal()
    hide_signal = Signal()

    retrieve_start = Signal()
    retrieve_end = Signal()

    def __init__(self, *args, timeout=6000, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Search Endpoints...")

        self.retrieve_dialog = RetrieveDialog(parent=self)
        self.retrieve_dialog.button.clicked.connect(self.on_cancel_retrieval)

        self.timeout = timeout
        self.new_endpoint.connect(self.on_new_endpoint)
        self.show_signal.connect(self.on_show)
        self.hide_signal.connect(self.on_hide)

        self.retrieve_start.connect(self.show_retrieve_dialog)
        self.retrieve_end.connect(self.hide_retrieve_dialog)

        self.endpoints = []
        self.layout = QtWidgets.QVBoxLayout()
        self.listWidget = QtWidgets.QListWidget()

        self.scanWidget = SelfScanWidget()
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.scanWidget.user_endpoint.connect(self.on_endpoint_selected)
        self.cancelButton.clicked.connect(self.on_cancel)

        self.select_endpoint = None
        self.retrieving_task = None

        self.layout.addWidget(self.listWidget)
        self.layout.addWidget(self.scanWidget)
        self.layout.addWidget(self.cancelButton)
        self.setLayout(self.layout)

    def on_endpoint_clicked(self, item):
        index = self.listWidget.indexFromItem(item).row()
        return self.on_endpoint_selected(self.endpoints[index])

    def on_endpoint_selected(self, endpoint):
        self.loop.call_soon_threadsafe(self.select_endpoint.set_result, endpoint)

    def on_cancel(self, endpoint):
        self.loop.call_soon_threadsafe(
            self.select_endpoint.set_exception,
            UserCancelledException("User cancelled the Selection"),
        )
        self.hide()

    def on_cancel_retrieval(self, endpoint):
        self.loop.call_soon_threadsafe(
            self.retrieving_task.set_exception,
            UserCancelledException("User cancelled the Retrieval"),
        )
        self.hide()

    def on_show(self):
        self.show()

    def on_hide(self):
        self.hide()

    def show_retrieve_dialog(self):
        self.retrieve_dialog.show()

    def hide_retrieve_dialog(self):
        self.retrieve_dialog.hide()

    def closeEvent(self, event):
        # do stuff
        if self.select_endpoint:
            self.loop.call_soon_threadsafe(
                self.select_endpoint.set_exception,
                UserCancelledException("User cancelled the Selection"),
            )
        if self.retrieving_task:
            self.loop.call_soon_threadsafe(
                self.select_endpoint.set_exception,
                UserCancelledException("User cancelled the Selection"),
            )

        event.accept()  # let the window close

    def on_new_endpoint(self, config):
        self.listWidget.clear()

        self.endpoints.append(config)

        for endpoint in self.endpoints:
            self.listWidget.addItem(f"{endpoint.name} at {endpoint.url}")

        self.listWidget.itemClicked.connect(self.on_endpoint_clicked)

    async def emit_endpoints(self):

        async for endpoint in self._discov.ascan_gen():
            self.new_endpoint.emit(endpoint)

    async def aload(self, previous={}, **kwargs):
        self.loop = asyncio.get_event_loop()
        self.show_signal.emit()
        emitting_task = self.loop.create_task(self.emit_endpoints())
        self.select_endpoint = self.loop.create_future()

        konfik = None
        try:
            endpoint = await self.select_endpoint

            self.retrieve_start.emit()
            self.retrieving_task = self.loop.create_task(
                self._retriev.aretrieve(endpoint, previous=previous)
            )

            konfik = await asyncio.wait_for(self.retrieving_task, timeout=self.timeout)

            self.retrieving_task.cancel()

            try:
                await self.retrieving_task
            except asyncio.CancelledError as e:
                pass

            self.retrieve_end.emit()
            self.hide_signal.emit()

            return konfik

        finally:
            emitting_task.cancel()
            try:
                await emitting_task
            except asyncio.CancelledError as e:
                logger.info("Cancelled the Discovery task")

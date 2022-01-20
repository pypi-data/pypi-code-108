
import glob
import os
import shutil
from Qt import QtWidgets, QtCore, QtGui

from publisher.gui.delegates import CheckBoxDelegate, ComboBoxDelegate
from publisher.procedure_content import build_channel_list, save_channel_changes
from publisher.processing.data_sources.organisation import get_data_from_channel
from publisher.processing.procedure import update_channel, build_channel
from publisher.settings import CHANNEL_TYPES, CHANNELS_ASSET_DIRECTORY, ASSET_NAME_PREFIX

from .models import ChannelTableModel
from .ui.channel_editor import Ui_channel_editor
from .widgets import SpinnerOverlay


class ChannelEditor(QtWidgets.QWidget, Ui_channel_editor):

    def __init__(self, parent=None):
        super(ChannelEditor, self).__init__(parent)
        self.new_images = {}
        self.channel_model = ChannelTableModel(self)
        self.channel_model.validation_error.connect(self._display_error)
        self.setupUi(self)
        self.channel_tbl.addAction(self.add_row)
        self.channel_tbl.addAction(self.delete_row)
        self.channel_tbl.setModel(self.channel_model)
        self.channel_tbl.setItemDelegateForColumn(self.channel_model.header.index('eula_required'),
                                                  CheckBoxDelegate(self))
        self.channel_tbl.setItemDelegateForColumn(self.channel_model.header.index('type'),
                                                  ComboBoxDelegate(self, CHANNEL_TYPES))
        self.loading_overlay = SpinnerOverlay(self.channel_tbl)
        # Pyside vs PySide2 incompatability not managed correctly by Qt Shim
        if 'setSectionResizeMode' in dir(self.channel_tbl.horizontalHeader()):
            self.channel_tbl.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        else:
            self.channel_tbl.horizontalHeader().setResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self._display_badge_banner_widget()
        self.load_channel_data()
        self._connect_signals()

    @QtCore.Slot()
    def on_submit_btn_clicked(self):
        data = self.channel_model.edited_channels
        errors = self._validate_submit(data)
        if errors:
            self._display_error(errors)
            return
        message = self.msg.toPlainText()
        self.data_saver = SaveChannelDataWorker(data, message, self.new_images)
        self.data_saver.done.connect(self._on_write_completed)
        self.data_saver.error.connect(self._display_error)
        self.loading_overlay.show()
        self.data_saver.start()

    @QtCore.Slot()
    def on_add_row_triggered(self):
        data = {'code': '', 'name': '', 'type': CHANNEL_TYPES[0], 'eula_required': False, 'new': True}
        row = self.channel_tbl.selectedIndexes()[0].row()
        self.channel_model.add_channel(data, row)

    @QtCore.Slot()
    def on_delete_row_triggered(self):
        row = self.channel_tbl.selectedIndexes()[0].row()
        self.channel_model.delete_row(row)

    def load_channel_data(self):
        self._enable_input(False)
        self.loading_overlay.show()
        self.data_loader = LoadChannelDataWorker()
        self.data_loader.channel_data.connect(self.channel_model.add_channel)
        self.data_loader.done.connect(self._on_data_loaded)
        self.data_loader.start()

    def resizeEvent(self, event):
        self._display_channel_images()
        super(ChannelEditor, self).resizeEvent(event)

    def _connect_signals(self):
        self.display_images.clicked.connect(self._display_badge_banner_widget)
        sel_model = self.channel_tbl.selectionModel()  # store in variable, otherwise application crashes
        sel_model.selectionChanged.connect(self._display_channel_images)
        self.badge.image_dropped.connect(self._change_image)
        self.banner.image_dropped.connect(self._change_image)

    def _change_image(self, image):
        row = self.channel_tbl.currentIndex().row()
        if row >= 0:
            name = self.sender().objectName()
            code = self.channel_model.mylist[row]['code']
            new_name = ASSET_NAME_PREFIX + code + name
            new_image = os.path.join(CHANNELS_ASSET_DIRECTORY, new_name + '.*')
            if glob.glob(new_image):
                reply = QtWidgets.QMessageBox.question(self, 'Overwrite?', '\nOverwrite existing {n}?\n'.format(n=name),
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.No:
                    return
            if not self.new_images.get(code):
                self.new_images[code] = {'badge': '', 'banner': ''}
            self.new_images[code][name] = image
            self._show_image_in_graphics_view(image, eval('self.' + name))
            self.channel_model.mylist[row]['changed'] = True

    def _display_badge_banner_widget(self):
        if self.display_images.isChecked():
            self.badge_banner_widget.show()
            self._expand_window(True)
            if self.channel_tbl.selectedIndexes():
                self._display_channel_images()
        else:
            self._expand_window(False)
            self.badge_banner_widget.hide()

    def _expand_window(self, expand=True):
        top_margin = self.layout().getContentsMargins()[1]
        if expand:
            height = self.height() + self.badge_banner_widget.height() * 2 + top_margin
        else:
            height = self.height() - self.badge_banner_widget.height() - top_margin / 2
        self.resize(self.width(), height)

    def _display_channel_images(self):
        row = self.channel_tbl.currentIndex().row()
        if row >= 0 and self.badge_banner_widget.isVisible():
            code = self.channel_model.mylist[row]['code']
            assets = self._unpack_asset_data(row)
            badge = self._get_asset_path(assets, 'badge')
            banner = self._get_asset_path(assets, 'banner')
            if code in self.new_images.keys():
                badge = self.new_images[code]['badge'] if self.new_images[code]['badge'] else badge
                banner = self.new_images[code]['banner'] if self.new_images[code]['banner'] else badge
            self._show_image_in_graphics_view(badge, self.badge)
            self._show_image_in_graphics_view(banner, self.banner)

    def _unpack_asset_data(self, row):
        asset_list = self.channel_model.mylist[row]['assets']
        assets = {}
        for item in asset_list:
            for key, val in item.iteritems():
                assets[key] = val
        return assets

    def _get_asset_path(self, asset_data, asset_name):
        if asset_data.get(asset_name):
            path = glob.glob(os.path.join(CHANNELS_ASSET_DIRECTORY, asset_data[asset_name]['name'] + '.*'))
            if path:
                return path[0].replace(r'/', os.sep)
        return None

    def _show_image_in_graphics_view(self, image, view):
        scene = QtWidgets.QGraphicsScene()
        if image:
            item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(image))
            scene.addItem(item)
        view.setScene(scene)
        view.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def _on_data_loaded(self):
        self.loading_overlay.hide()
        self._enable_input()

    def _on_write_completed(self):
        self.loading_overlay.hide()
        self._enable_input()

    def _display_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Error", "Error: {}".format(message))
        self.loading_overlay.hide()
        self._enable_input()

    def _enable_input(self, state=True):
        self.msg.setEnabled(state)
        self.channel_tbl.setEnabled(state)
        self.submit_btn.setEnabled(state)
        self.display_images.setEnabled(state)

    def _validate_submit(self, data):
        if self.msg.toPlainText() == '':
            return "Submit comment must not be blank"
        for item in data:
            if not item.get('name'):
                return "Name is blank for channel with code {}".format(item.get('code'))
            if not item.get('code'):
                return "Code is blank for channel with name {}".format(item.get('name'))


class LoadChannelDataWorker(QtCore.QThread):

    channel_data = QtCore.Signal(dict)
    done = QtCore.Signal()

    def run(self):
        for channel in build_channel_list():
            data = get_data_from_channel(channel)
            self.channel_data.emit(data)
        self.done.emit()


class SaveChannelDataWorker(QtCore.QThread):

    done = QtCore.Signal()
    error = QtCore.Signal(str)

    def __init__(self, data, msg, new_images):
        try:
            self.data = data
            self.message = msg
            self.new_images = new_images
            super(SaveChannelDataWorker, self).__init__()
        except Exception as e:
            message = str(e)
            self.error.emit(message)

    def run(self):
        try:
            for channel in self.data:
                if channel['code'] in self.new_images.keys():
                    self._copy_and_rename_assets(channel['code'], self.new_images[channel['code']])
                if channel.get('new', False):
                    channel_data = {'code': channel['code'], 'name': channel['name'], 'type': channel['type'],
                                    'eula': channel['eula_required']}
                    build_channel(channel_data)
                else:
                    updates = {'name': channel['name'], 'type': channel['type'], 'eula': channel['eula_required']}
                    update_channel(channel['code'], updates)
            save_channel_changes(self.message)
            self.done.emit()
        except Exception as e:
            message = str(e)
            self.error.emit(message)

    def _copy_and_rename_assets(self, code, assets):
        for name, asset in assets.iteritems():
            if asset:
                new_name = ASSET_NAME_PREFIX + code + name
                new_asset = os.path.join(CHANNELS_ASSET_DIRECTORY, new_name + os.path.splitext(asset)[-1])
                existing_assets = glob.glob(os.path.join(CHANNELS_ASSET_DIRECTORY, new_name + '.*'))
                for file in existing_assets:
                    os.remove(file)
                shutil.copy(asset, new_asset)

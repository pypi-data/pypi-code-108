import os
import re
import timeago
from datetime import datetime
from kabaret.app import resources
from kabaret.app.ui.gui.widgets.widget_view import DockedView, QtWidgets, QtGui, QtCore


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    '''Sort a string in a natural way
    https://stackoverflow.com/a/16090640'''
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]


def timeago_format(time):
    dt = datetime.fromtimestamp(time)
    dt = timeago.format(dt, datetime.now())
    return dt


def custom_format(time, format):
    dt = datetime.fromtimestamp(time)
    dt = dt.astimezone().strftime(format)
    return dt


class OutputHeader(QtWidgets.QWidget):
    
    def __init__(self, view, parent=None):
        super(OutputHeader, self).__init__(parent)
        self.view = view
        
        self.setFixedHeight(80)
        
        # Define widgets to display current runner data
        self._label_index = QtWidgets.QLabel()
        self._label_name = QtWidgets.QLabel()
        self._label_description = QtWidgets.QLabel()
        self._label_update_time = QtWidgets.QLabel()
        self._label_pid = QtWidgets.QLabel()
        self._textedit_cmd = QtWidgets.QPlainTextEdit()
        self._button_copy_cmd = QtWidgets.QPushButton(
            resources.get_icon(('icons.libreflow', 'clipboard')), ''
        )
        
        # Labels
        font = self._label_index.font()
        font.setPointSize(15)
        font.setWeight(QtGui.QFont.DemiBold)
        self._label_description.setFont(font)
        self._label_name.setFont(font)
        font.setPointSize(8)
        font.setWeight(QtGui.QFont.Normal)
        self._label_update_time.setFont(font)
        self._label_update_time.setStyleSheet("QLabel { color : #aaa; }")
        self._label_index.setFont(font)
        self._label_index.setStyleSheet("QLabel { color : #aaa; }")
        self._label_index.setToolTip('Index/PID')
        self._label_pid.setFont(font)
        self._label_pid.setStyleSheet("QLabel { color : #aaa; }")
        self._textedit_cmd.setStyleSheet((
            "QPlainTextEdit { "
            "background-color: #3e4041; "
            "color: #717476; "
            "border-style: none; }"
        ))
        
        # Command text edit
        self._textedit_cmd.setReadOnly(True)
        self._textedit_cmd.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._textedit_cmd.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )
        self._textedit_cmd.setFixedHeight(25)
        self._textedit_cmd.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        
        # Copy to clipboard button
        self._button_copy_cmd.setFixedSize(42, 28)
        self._button_copy_cmd.setToolTip('Copy command to clipboard')
        self._button_copy_cmd.setStyleSheet((
            "QPushButton { border-color: #666; }"
            "QPushButton:pressed { border-color: #999; }"
        ))

        self._button_copy_cmd.clicked.connect(self.copy_cmd_to_clipboard)

        # Setup layout
        glo = QtWidgets.QGridLayout()
        glo.setSpacing(1)
        glo.setContentsMargins(0, 0, 0, 0)
        glo.setColumnStretch(1, 1)
        glo.setAlignment(QtCore.Qt.AlignVCenter)
        glo.addWidget(self._label_description, 0, 0, 2, 1)
        glo.addWidget(self._label_pid, 0, 1, QtCore.Qt.AlignRight)
        glo.addWidget(self._label_update_time, 1, 1, QtCore.Qt.AlignRight)
        
        line = QtWidgets.QFrame()
        line.setGeometry(QtCore.QRect(320, 150, 118, 1))
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("QFrame { color: #555 }")
        
        glo.addWidget(line, 2, 0, 1, 3)
        
        hlo = QtWidgets.QHBoxLayout()
        hlo.setAlignment(QtCore.Qt.AlignHCenter)
        hlo.setContentsMargins(0, 0, 0, 0)
        hlo.setSpacing(0)
        hlo.addWidget(self._textedit_cmd, 0)
        hlo.addWidget(self._button_copy_cmd, 1)
        
        glo.addLayout(hlo, 3, 0, 3, 3)
        self.setLayout(glo)
    
    def update(self):
        current_item = self.view.current_item()
        
        if current_item is None:
            self._label_update_time.clear()
        else:
            time = custom_format(
                os.path.getmtime(current_item.log_path()),
                '%A %d-%m-%Y, %H:%M:%S'
            )
            self._label_update_time.setText('Last update: ' + time)
    
    def refresh(self):
        current_item = self.view.current_item()
        
        if current_item is None:
            self._label_description.clear()
            self._label_update_time.clear()
            self._label_pid.clear()
            self._textedit_cmd.clear()
        else:
            self._label_description.setText('%s - %s' % (
                current_item.name(),
                current_item.label()
            ))
            time = custom_format(
                os.path.getmtime(current_item.log_path()),
                '%A %d-%m-%Y, %H:%M:%S'
            )
            self._label_update_time.setText('Last modification: ' + time)
            self._label_pid.setText('PID: ' + str(current_item.pid()))
            self._textedit_cmd.setPlainText(current_item.command())

    def copy_cmd_to_clipboard(self):
        cmd = self._textedit_cmd.toPlainText()
        app = QtWidgets.QApplication.instance()
        clip = app.clipboard()
        clip.setText(cmd)


class OutputTextEdit(QtWidgets.QPlainTextEdit):
    
    def __init__(self, view, parent=None):
        super(OutputTextEdit, self).__init__(parent)
        self.view = view
        self._log_mtime = 0
        
        self.setReadOnly(True)
    
    def _write(self, text):
        doc = self.document()
        cursor = QtGui.QTextCursor(doc)
        cursor.clearSelection()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ensureCursorVisible()
    
    def update(self):
        self.clear()
        
        current_item = self.view.current_item()
        if current_item is None:
            return
        
        log_path = current_item.log_path()
        if log_path is None:
            return
        
        with open(log_path, 'r') as log_file:
            log = log_file.read()
            self._write(log)
    
    def refresh(self):
        current_item = self.view.current_item()
        if current_item is None:
            return
        
        log_path = current_item.log_path()
        if log_path is None:
            return

        # Check if log file has been modified
        mtime = os.path.getmtime(log_path)
        
        if mtime > self._log_mtime:
            self.update()
            self._log_mtime = mtime


class SubprocessOutput(QtWidgets.QWidget):
    
    def __init__(self, parent, view):
        super(SubprocessOutput, self).__init__(parent)
        self.view = view
        
        self._header = OutputHeader(view)
        self._output = OutputTextEdit(view)
        
        self._output.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        
        vlo = QtWidgets.QVBoxLayout()
        vlo.addWidget(self._header)
        vlo.addWidget(self._output)
        vlo.setContentsMargins(0, 0, 0, 0)
        vlo.setSpacing(1)
        self.setLayout(vlo)
        
        # Set up timer to periodically update
        # running process output
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.setInterval(10)
    
    def update(self):
        self._header.refresh()
        self._output.update()
    
    def refresh(self):
        self._header.update()
        self._output.refresh()


class SubprocessListItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tree, process):
        super(SubprocessListItem, self).__init__(tree)
        self.process = None
        # self.args = ()
        # self.kwargs = {}
        self._match_str = ''
        self.set_process(process)
    
    def set_process(self, process):
        self.process = process
        self._match_str = ''
        self._update()
    
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        if column == 3:
            mtime = os.path.getmtime(self.log_path())
            other_mtime = os.path.getmtime(other.log_path())
            return mtime < other_mtime
        elif column == 4:
            return self.last_run_time() < other.last_run_time()
        else:
            key1 = self.text(column)
            key2 = other.text(column)
            return natural_sort_key(key1) < natural_sort_key(key2)
    
    def _update(self):
        self.setText(0, str(self.id()))
        self.setText(1, self.name())
        self.setText(2, self.label())
        mtime = os.path.getmtime(self.log_path())
        self.setText(3, timeago_format(mtime))
        self.setText(4, timeago_format(self.last_run_time()))
        self.setText(5, str(self.pid()))
        
        if self.is_running():
            color = QtGui.QColor(185, 194, 200)
        else:
            color = QtGui.QColor(110, 110, 110)
        
        for i in range(self.treeWidget().columnCount()):
            self.setForeground(i, QtGui.QBrush(color))

    def id(self):
        return self.process['id']
    
    def name(self):
        return self.process['name']
    
    def version(self):
        return self.process['version']
    
    def label(self):
        return self.process['label']
    
    def pid(self):
        return self.process['pid']
    
    def is_running(self):
        return self.process['is_running']
    
    def log_path(self):
        return self.process['log_path']
    
    def command(self):
        return self.process['command']

    def last_run_time(self):
        return self.process['last_run_time']

    def matches(self, filter):
        return filter in self._match_str


class SubprocessList(QtWidgets.QTreeWidget):
    
    def __init__(self, parent, view, session):
        super(SubprocessList, self).__init__(parent)
        self.view = view
        self.session = session
        
        columns = (
            'ID', 'Application',
            'Description', 'Last update',# 'Version',
            'Started', 'PID',
        )
        self.setHeaderLabels(columns)
        
        self.itemSelectionChanged.connect(self.view.update_output)

        # Periodically update runner infos
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        
        self.setSortingEnabled(True)
        self.sortByColumn(4, QtCore.Qt.DescendingOrder)
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_popup_menu_request)

        self._popup_menu = QtWidgets.QMenu(self)

        self._filter = None
        self._rid_to_item = {}
        
        self.header().resizeSection(0, 60)
        self.header().resizeSection(1, 140)
        self.header().resizeSection(3, 100)
        self.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.header().setStretchLastSection(False)
    
    def set_show_running_only(self, b):
        self._show_running_only = b
        self.refresh()
    
    def refresh(self):
        #TODO: intelligent refresh: remove deleted runners, add created runners
        self.clear()
        self._rid_to_item.clear()
        for sp in self.session.cmds.SubprocessManager.list_runner_infos():
            item = SubprocessListItem(self, sp)
            self._rid_to_item[item.id()] = item
            # TODO: manage item filtering
            if self.view.show_running_only():
                item.setHidden(not item.is_running())

    def update(self):
        for sp in self.session.cmds.SubprocessManager.list_runner_infos():
            rid = sp['id']
            item = self._rid_to_item.get(rid, None)
            
            if item is None:
                # Create item for new runner instance
                item = SubprocessListItem(self, sp)
                self._rid_to_item[rid] = item
                # TODO: manage item filtering
                if self.view.show_running_only():
                    item.setHidden(not item.is_running())
            else:
                # Update info of existing runner instance
                item.set_process(sp)

    def update_runner(self, rid):
        item = self._rid_to_item[rid]
        if item is not None:
            process = self.session.cmds.SubprocessManager.get_runner_info(
                rid
            )
            item.set_process(process)
    
    def clear_completed_runners(self):
        # self.refresh()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            
            if not item.is_running():
                self.session.cmds.SubprocessManager.delete_runner_instance(
                    item.id()
                )
        
        self.refresh()
    
    def _on_popup_menu_request(self, pos):
        item = self.itemAt(pos)
        
        if item is None:
            m = self._popup_menu
            m.clear()
            m.addAction(
                QtGui.QIcon(resources.get_icon(('icons.libreflow', 'refresh'))),
                'Refresh',
                self.view.refresh
            )
            m.addAction(
                QtGui.QIcon(resources.get_icon(('icons.libreflow', 'clean'))),
                'Clean completed',
                self.view.clear_completed_runners
            )
        else:
            # item = item.job_item()
            m = self._popup_menu
            m.clear()
            if not item.is_running():
                m.addAction(
                    QtGui.QIcon(resources.get_icon(('icons.libreflow', 'run'))),
                    'Relaunch',
                    lambda item=item: self._launch(item)
                )
                m.addAction(
                    QtGui.QIcon(resources.get_icon(('icons.libreflow', 'delete'))),
                    'Delete',
                    lambda item=item: self._delete(item)
                )
            else:
                m.addAction(
                    QtGui.QIcon(resources.get_icon(('icons.libreflow', 'stop'))),
                    'Terminate',
                    lambda item=item: self._terminate(item)
                )

        self._popup_menu.popup(self.viewport().mapToGlobal(pos))
    
    def _launch(self, item):
        self.session.cmds.SubprocessManager.launch_runner_instance(
            item.id()
        )
        self.update_runner(item.id())
        self.view.update_output()
    
    def _terminate(self, item):
        self.session.cmds.SubprocessManager.terminate_runner_instance(
            item.id()
        )
        self.update_runner(item.id())

    def _kill(self, item):
        self.session.cmds.SubprocessManager.kill_runner_instance(
            item.id()
        )
        self.update_runner(item.id())
    
    def _delete(self, item):
        self.session.cmds.SubprocessManager.delete_runner_instance(
            item.id()
        )
        self.view.refresh()


class SubprocessView(DockedView):
    
    def __init__(self, session, view_id=None, hidden=False, area=None):
        super(SubprocessView, self).__init__(session, view_id, hidden=hidden, area=area)

    def _build(self, top_parent, top_layout, main_parent, header_parent, header_layout):
        self.splitter = QtWidgets.QSplitter(main_parent)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        
        self._subprocess_list = SubprocessList(self.splitter, self, self.session)
        self._subprocess_output = SubprocessOutput(self.splitter, self)
        
        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        lo.addWidget(self.splitter)

        main_parent.setLayout(lo)
        
        self.view_menu.setTitle('Options')
        self.view_menu.addAction(
            QtGui.QIcon(resources.get_icon(('icons.libreflow', 'refresh'))),
            'Refresh',
            self.refresh
        )
        self.view_menu.addAction(
            QtGui.QIcon(resources.get_icon(('icons.libreflow', 'clean'))),
            'Clean completed',
            self.clear_completed_runners
        )
        self._show_running_action = self.view_menu.addAction(
            'Show running only',
            self.on_show_running_change
        )
        self._show_running_action.setCheckable(True)
        self._show_running_action.setChecked(False)
        
        self.set_view_title('Processes')

    def refresh(self):
        self.refresh_list()
        self._subprocess_output.update()

    def refresh_list(self):
        self._subprocess_list.refresh()
    
    def update_output(self):
        current_item = self.current_item()
        
        if current_item is None:
            # Clear output if no runner is selected
            self._subprocess_output.timer.stop()
            self._subprocess_output.refresh()
        else:
            # Update stopped runner only if its output
            # isn't already displayed
            self._subprocess_output.timer.stop()
            self._subprocess_output.update()
            
            if current_item.is_running():
                self._subprocess_output.timer.start()
    
        # self._subprocess_output.update()
    
    def current_item(self):
        selection = self._subprocess_list.selectedItems()
        if not selection:
            return None
        else:
            return selection[0]
    
    def clear_completed_runners(self):
        self._subprocess_list.clear_completed_runners()
        self._subprocess_output.update()
    
    def on_show(self):
        self.refresh_list()

    def show_running_only(self):
        return self._show_running_action.isChecked()

    def on_show_running_change(self):
        self._subprocess_list.set_show_running_only(
            self._show_running_action.isChecked()
        )

    def receive_event(self, event_type, data):
        # TODO: Manage events sent from actor
        # (e.g. when a runner is instanciated ?)
        pass

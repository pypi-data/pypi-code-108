from kabaret.app.ui.gui.widgets.flow.flow_view import (
    CustomPageWidget,
    QtWidgets,
    QtCore,
    QtGui,
)
from fnmatch import fnmatch
from collections import defaultdict


class TaskFileItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, task_item, tree, file):
        super(TaskFileItem, self).__init__(task_item)
        self._tree = tree
        self._task_item = task_item
        self.file = None
        
        self.combo_box_revisions = QtWidgets.QComboBox()
        self._tree.setItemWidget(self, 1, self.combo_box_revisions)
        
        self.set_file(file)
    
    def set_file(self, file):
        self.file = file
        self._update()
    
    def on_checkstate_toggled(self, column):
        pass
    
    def submit_blender_playblast_job(self):
        f = self.file
        kwargs = dict(
            shot_name=f['shot'],
            dept_name=f['department'],
            file_name=f['name'],
            revision_name=self.combo_box_revisions.currentText(),
        )
        extension = f['name'].split('.')[1]
        
        if extension == 'blend':
            kwargs['use_simplify'] = (self.checkState(2) == QtCore.Qt.Checked)
            kwargs['reduce_textures'] = (self.checkState(3) == QtCore.Qt.Checked)
        
        return self._tree.parentWidget().submit_blender_playblast_job(extension, **kwargs)
    
    def _update(self):
        f = self.file
        self.setText(0, f['name'])
        
        names, statuses = zip(*f['revisions'])
        self.combo_box_revisions.addItems(names)
        self.combo_box_revisions.setCurrentText(f['default_revision'])
        
        for i, status in enumerate(statuses):
            if status != 'Available':
                self.combo_box_revisions.setItemData(i, False, QtGui.Qt.UserRole-1)


class ShotTaskItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, shot_item, tree, task):
        super(ShotTaskItem, self).__init__(shot_item)
        self._shot_item = shot_item
        self._tree = tree
        self.task = None
        
        self.set_task(task)
    
    def set_task(self, task):
        self.task = task
        self._update()
    
    def on_checkstate_toggled(self, column):
        for i in range(self.childCount()):
            self.child(i).setCheckState(column, self.checkState(column))
    
    def _update(self):
        d = self.task
        self.setText(0, d['name'])
        
        file_item_type = self._tree.file_item_type()
        
        # Loop over task files
        for file in d['files']:
            file_item_type(self, self._tree, file)


class ShotItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, shots_item, tree, shot):
        super(ShotItem, self).__init__(shots_item)
        self._tree = tree
        self.shot = None
        
        self.set_shot(shot)
    
    def set_shot(self, shot):
        self.shot = shot
        self._update()
    
    def on_checkstate_toggled(self, column):
        # Uncheck all tasks if shot is unchecked
        if self.checkState(column) == QtCore.Qt.Unchecked:
            for i in range(self.childCount()):
                self.child(i).setCheckState(column, QtCore.Qt.Unchecked)
            
            return
        
        # Otherwise, check tasks according to global tasks checkstates
        for i in range(self.childCount()):
            check_state = self._tree.get_task_item_checkstate(column, i)
            self.child(i).setCheckState(column, check_state)
    
    def _update(self):
        s = self.shot
        self.setText(0, s['name'])
        
        for i in range(self._tree.header().count()):
            self.setBackgroundColor(i, QtGui.QColor(60, 60, 60))
        
        # Loop over shot tasks
        for task in s['tasks']:
            task_item = ShotTaskItem(self, self._tree, task)


class TaskItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tasks_item, tree, task_name):
        super(TaskItem, self).__init__(tasks_item)
        self._tree = tree
        self.tasks_item = tasks_item
        
        self.setText(0, task_name)
        
        for i in range(self._tree.header().count()):
            self.setBackgroundColor(i, QtGui.QColor(60, 60, 60))
    
    def on_checkstate_toggled(self, column):
        index = self.tasks_item.indexOfChild(self)
        self._tree.set_task_items_checkstate(self.checkState(column), column, index)


class TasksItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tree):
        super(TasksItem, self).__init__(tree)
        self._tree = tree
        
        self._update()
    
    def on_checkstate_toggled(self, column):
        for i in range(self.childCount()):
            self.child(i).setCheckState(column, self.checkState(column))
    
    def _update(self):
        self.setText(0, 'Tasks')
        
        for i in range(self._tree.header().count()):
            self.setBackgroundColor(i, QtGui.QColor(76, 80, 82))
            font = self.font(i)
            font.setWeight(QtGui.QFont.DemiBold)
            self.setFont(i, font)
        
        task_names = self._tree.parentWidget().get_shot_task_names()
        for task_name in task_names:
            task_item = TaskItem(self, self._tree, task_name)
        
        self.setExpanded(True)


class ShotsItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tree):
        super(ShotsItem, self).__init__(tree)
        self._tree = tree
        
        self._update()
    
    def on_checkstate_toggled(self, column):
        for i in range(self.childCount()):
            self.child(i).setCheckState(column, self.checkState(column))
    
    def _update(self):
        self.setText(0, 'Shots')
        
        for i in range(self._tree.header().count()):
            self.setBackgroundColor(i, QtGui.QColor(76, 80, 82))
            font = self.font(i)
            font.setWeight(QtGui.QFont.DemiBold)
            self.setFont(i, font)
        
        shot_files_data = self._tree.parentWidget().get_shots_data()
        for shot in shot_files_data:
            shot_item = ShotItem(self, self._tree, shot)
        
        self.setExpanded(True)


class ShotSelector(QtWidgets.QTreeWidget):
    
    @classmethod
    def file_item_type(cls):
        return TaskFileItem
    
    def __init__(self, parent, session):
        super(ShotSelector, self).__init__(parent)
        self.session = session

        self.setHeaderLabels(self.get_columns())
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.header().setStretchLastSection(False)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setFixedHeight(350)
        
        self.tasks = None
        self.shots = None
        self.task_name_to_index = {}
        self.refresh()
        
        # self.setMinimumHeight(self.sizeHintForRow(0) * (self.shots.childCount() + self.tasks.childCount()))
        
        self.itemChanged.connect(self.on_item_changed)
    
    def get_columns(self):
        return ('Name', 'Revision', 'Use simplify', 'Reduce textures')
    
    def on_item_changed(self, item, column):
        item.on_checkstate_toggled(column)
    
    def set_task_items_checkstate(self, state, column, index):
        for i in range(self.shots.childCount()):
            shot_item = self.shots.child(i)
            
            if shot_item.checkState(0) == QtCore.Qt.Checked:
                task_item = shot_item.child(index)
                task_item.setCheckState(column, state)
    
    def get_task_item_checkstate(self, column, index):
        return self.tasks.child(index).checkState(column)
    
    def _do_refresh(self, item):
        item.setCheckState(0, QtCore.Qt.Unchecked)
        item.setCheckState(2, QtCore.Qt.Unchecked)
        item.setCheckState(3, QtCore.Qt.Unchecked)
    
    def refresh_child(self, item):
        self._do_refresh(item)
        
        if item.childCount() == 0:
            return
        
        for i in range(item.childCount()):
            self.refresh_child(item.child(i))
    
    def refresh(self):
        self.clear()
        
        self.tasks = TasksItem(self)
        self.shots = ShotsItem(self)
        
        for i in range(self.topLevelItemCount()):
            self.refresh_child(self.topLevelItem(i))


class ProcessSequenceFilesWidget(CustomPageWidget):

    def get_shots_data(self):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='ensure_files_data',
            args={}, kwargs={}
        )
    
    def get_shot_task_names(self):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='get_shot_task_names',
            args={}, kwargs={}
        )

    def _close_view(self):
        view = self.parentWidget().page.view
        view.close()


class PlayblastItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, task_item, tree, file):
        super(PlayblastItem, self).__init__(task_item)
        self._tree = tree
        self._task_item = task_item
        self.file = None
        
        self.combo_box_revision = QtWidgets.QComboBox()
        self.combo_box_target_status = QtWidgets.QComboBox()
        self.combo_box_task_type = QtWidgets.QComboBox()
        self.lineedit_comment = QtWidgets.QLineEdit()
        self.lineedit_comment.setPlaceholderText('...')
        
        self._tree.setItemWidget(self, 1, self.combo_box_revision)
        self._tree.setItemWidget(self, 2, self.combo_box_task_type)
        self._tree.setItemWidget(self, 4, self.combo_box_target_status)
        self._tree.setItemWidget(self, 5, self.lineedit_comment)
        
        self.set_file(file)
    
    def set_file(self, file):
        self.file = file
        self._update()
    
    def on_checkstate_toggled(self, column):
        pass
    
    def update_target_status(self, target_status):
        self.combo_box_target_status.setCurrentText(target_status)
    
    def _update(self):
        f = self.file
        self.setText(0, f['name'])
        self.setText(3, f['current_task_status'])
        
        names, revision_statutes = zip(*f['revisions'])
        self.combo_box_revision.addItems(names)
        self.combo_box_revision.setCurrentText(f['default_revision'])
        self.combo_box_task_type.addItems(f['task_types'])
        self.combo_box_task_type.setCurrentText(f['default_task_type'])
        task_statutes = self._tree.parentWidget().get_task_statutes()
        self.combo_box_target_status.addItems(task_statutes)
        # self.combo_box_target_status.setCurrentText(f['default_task_status'])
        self.combo_box_target_status.setCurrentText(task_statutes[0])
        
        for i, status in enumerate(revision_statutes):
            if status != 'Available':
                self.combo_box_revision.setItemData(i, False, QtGui.Qt.UserRole-1)
    
    def upload_to_kitsu(self):
        comment = self.lineedit_comment.text()
        task_name = self.parent().text(0)
        task_comment = self._tree.get_task_comment(task_name)
        
        if task_comment:
            comment = task_comment + '\n\n' + comment
        
        self._tree.parentWidget().upload_playblast_to_kitsu(
            file_oid=self.file['oid'],
            revision_name=self.combo_box_revision.currentText(),
            task_type=self.combo_box_task_type.currentText(),
            target_task_status=self.combo_box_target_status.currentText(),
            comment=comment
        )


class UploadPlayblastTaskItem(TaskItem):
    
    def __init__(self, tasks_item, tree, task_name, kitsu_task_type):
        super(UploadPlayblastTaskItem, self).__init__(tasks_item, tree, task_name)
        
        self.combo_box_target_status = QtWidgets.QComboBox()
        self.lineedit_comment = QtWidgets.QLineEdit()
        self.lineedit_comment.setPlaceholderText('...')
        
        self._tree.setItemWidget(self, 4, self.combo_box_target_status)
        self._tree.setItemWidget(self, 5, self.lineedit_comment)
        
        self.setText(2, kitsu_task_type)
        self._update()
        
        self.combo_box_target_status.currentTextChanged.connect(self.on_target_status_changed)
    
    def get_comment(self):
        return self.lineedit_comment.text()
    
    def on_target_status_changed(self, target_status):
        self._tree.update_target_statutes(self.text(0), target_status)
    
    def _update(self):
        task_statutes = self._tree.parentWidget().get_task_statutes()
        self.combo_box_target_status.addItems(task_statutes)
        self.combo_box_target_status.setCurrentText(task_statutes[0])


class UploadPlayblastTasksItem(TasksItem):
    
    def _update(self):
        self.setText(0, 'Tasks')
        
        for i in range(self._tree.header().count()):
            self.setBackgroundColor(i, QtGui.QColor(76, 80, 82))
            font = self.font(i)
            font.setWeight(QtGui.QFont.DemiBold)
            self.setFont(i, font)
        
        task_names = self._tree.parentWidget().get_shot_task_names()
        for task_name in task_names:
            kitsu_task_type = self._tree.parentWidget().get_kitsu_task_type(task_name)
            task_item = UploadPlayblastTaskItem(self, self._tree, task_name, kitsu_task_type)
        
        self.setExpanded(True)


class UploadPlayblastSelector(ShotSelector):
    
    @classmethod
    def file_item_type(cls):
        return PlayblastItem
    
    def get_columns(self):
        return ('Shot', 'Revision', 'Kitsu task', 'Current status', 'Target status', 'Comment')
    
    def get_task_comment(self, task_name):
        task_index = self.task_name_to_index[task_name]
        return self.tasks.child(task_index).get_comment()
    
    def update_target_statutes(self, task_name, target_status):
        task_index = self.task_name_to_index[task_name]
        
        for i in range(self.shots.childCount()):
            shot_item = self.shots.child(i)
            task_item = shot_item.child(task_index)
            
            for j in range(task_item.childCount()):
                file_item = task_item.child(j)
                file_item.update_target_status(target_status)
    
    def _do_refresh(self, item):
        item.setCheckState(0, QtCore.Qt.Unchecked)
    
    def refresh(self):
        self.clear()
        self.task_name_to_index.clear()
        
        self.tasks = UploadPlayblastTasksItem(self)
        self.shots = ShotsItem(self)
        
        for i in range(self.topLevelItemCount()):
            self.refresh_child(self.topLevelItem(i))
        
        for i in range(self.tasks.childCount()):
            task_name = self.tasks.child(i).text(0)
            self.task_name_to_index[task_name] = i
        
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(True)


class UploadSequencePlayblastsWidget(ProcessSequenceFilesWidget):
    
    def build(self):
        self.playblast_selector = UploadPlayblastSelector(self, self.session)
        self.button_upload = QtWidgets.QPushButton('Upload')
        self.button_cancel = QtWidgets.QPushButton('Cancel')
        
        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.playblast_selector, 0, 0, 3, 1)
        glo.addWidget(self.button_upload, 0, 1)
        glo.addWidget(self.button_cancel, 1, 1)
        glo.setSpacing(0)
        self.setLayout(glo)

        self.button_upload.clicked.connect(self.on_upload_button_clicked)
        self.button_cancel.clicked.connect(self.on_cancel_button_clicked)
    
    def get_task_statutes(self):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='get_task_statutes',
            args={}, kwargs={}
        )
    
    def get_kitsu_task_type(self, task_name):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='get_kitsu_task_type',
            args=[task_name], kwargs={}
        )
    
    def upload_playblast_to_kitsu(self, file_oid, revision_name, task_type, target_task_status, comment):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='upload_playblast_to_kitsu',
            args=[file_oid, revision_name, task_type, target_task_status, comment],
            kwargs={}
        )

    def on_upload_button_clicked(self):
        shots = self.playblast_selector.shots
        
        for i in range(shots.childCount()):
            shot_item = shots.child(i)
            
            for j in range(shot_item.childCount()):
                task_item = shot_item.child(j)
                
                for k in range(task_item.childCount()):
                    file_item = task_item.child(k)
                    
                    if file_item.checkState(0) == QtCore.Qt.Checked:
                        file_item.upload_to_kitsu()
        
        self._close_view()
    
    def on_cancel_button_clicked(self):
        self._close_view()


class RenderSequencePlayblastsWidget(ProcessSequenceFilesWidget):
    
    def build(self):
        self.shot_selector = ShotSelector(self, self.session)
        self.button_submit = QtWidgets.QPushButton('Submit playblasts')
        self.checkbox_select_all = QtWidgets.QCheckBox('Select all')
        self.combobox_pool = QtWidgets.QComboBox()
        self.lineedit_priority = QtWidgets.QLineEdit()
        
        self.button_submit.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button_submit.setMaximumWidth(150)
        font = self.button_submit.font()
        font.setPointSize(11)
        font.setWeight(QtGui.QFont.DemiBold)
        self.button_submit.setFont(font)
        
        validator = QtGui.QIntValidator(1, 1000)
        self.lineedit_priority.setValidator(validator)
        self.lineedit_priority.setText('10')
        self.lineedit_priority.setFixedWidth(50)
        self.lineedit_priority.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        self.combobox_pool.addItems(self.get_job_pool_names())
        self.combobox_pool.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.combobox_pool.setFixedWidth(50)
        
        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.shot_selector, 0, QtCore.Qt.AlignTop)
        
        vlo = QtWidgets.QVBoxLayout()
        label_settings = QtWidgets.QLabel('Global settings')
        label_settings.setFont(font)
        vlo.addWidget(label_settings, 0)
        vlo.addWidget(QtWidgets.QLabel('Priority'), 1)
        vlo.addWidget(self.lineedit_priority, 2)
        vlo.addWidget(QtWidgets.QLabel('Job pool'), 3)
        vlo.addWidget(self.combobox_pool, 4)
        vlo.addWidget(self.button_submit, 5)
        
        for i in range(5):
            vlo.setStretch(i, 0)
        vlo.insertStretch(5, 10)
        
        hlo.addLayout(vlo, 1)
        
        self.setLayout(hlo)

        self.button_submit.clicked.connect(self.on_submit_button_clicked)
    
    def get_job_pool_names(self):
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name='get_job_pool_names',
            args={}, kwargs={}
        )
    
    def submit_blender_playblast_job(self, file_extension, **kwargs):
        kwargs['pool_name'] = self.combobox_pool.currentText()
        kwargs['priority'] = int(self.lineedit_priority.text())
        
        if file_extension == 'blend':
            method_name = 'submit_blender_playblast_job'
        elif file_extension == 'aep':
            method_name = 'submit_afterfx_playblast_job'
        else:
            pass
        
        return self.session.cmds.Flow.call(
            oid=self.oid,
            method_name=method_name,
            args={}, kwargs=kwargs
        )
    
    def on_submit_button_clicked(self):
        shots = self.shot_selector.shots
        
        for i in range(shots.childCount()):
            shot_item = shots.child(i)
            
            for j in range(shot_item.childCount()):
                task_item = shot_item.child(j)
                
                for k in range(task_item.childCount()):
                    file_item = task_item.child(k)
                    
                    if file_item.checkState(0) == QtCore.Qt.Checked:
                        file_item.submit_blender_playblast_job()
        
        self._close_view()
    

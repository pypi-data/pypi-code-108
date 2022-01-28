
from __future__ import print_function

import six
import time
import json
import os

from qtpy import QtWidgets, QtCore

try:
    from kabaret.app.ui.gui.widgets.widget_view import DockedView
except ImportError:
    raise RuntimeError('Your kabaret version is too old, for the JobView. Please update !')

from kabaret.app import resources

class JobListParamItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, job_item, v, k=None):
        super(JobListParamItem, self).__init__(job_item)
        self._job_item = job_item
        self.k = k
        self.v = v 

        if k is not None:
            self.setText(0, '{}={}'.format(k, v))
        else:
            self.setText(0, v)

        self.setIcon(0, resources.get_icon(('icons.gui', 'tag-black-shape')))

    def job_item(self):
        return self._job_item

class JobListItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, tree, job):
        super(JobListItem, self).__init__(tree)
        self.job = None
        self.args = ()
        self.kwargs = {}
        self._match_str = ''
        self.set_job(job)

    def job_item(self):
        return self

    def set_job(self, job):
        nb = self.childCount()
        for i in range(nb):
            child = self.takeChild(i)
            # Destroy it ?

        self.job = job
        self.args = ()
        self.kwargs = {}
        self._match_str = ''
        self._update()

    def _update(self):
        j = self.job
        self.setText(1, j['job_type'])
        self.setText(2, str(j['job_params']))
        self.setText(3, j['job_label'])
        self.setText(4, j['owner'])
        self.setText(5, j['pool'])
        self.setText(6, str(j['priority']))
        self.setText(7, j.get('node', ''))

        # self.setText(7, str(j['paused']))
        # self.setText(8, str(j['in_progress']))
        # self.setText(9, str(j['done']))

        self.setText(8, j['creator'])
        
        ts = j['created_on']
        date_str = time.ctime(ts)

        self.setText(9, date_str)
        self.setText(10, str(ts))
        self.setText(11, j['jid'])

        status = j['status']
        self.setIcon(0, resources.get_icon(j['icon_ref']))
        self.setText(0, '')
        
        matchers = [
            j['jid'],
            j['owner'], status, j['job_type'],
            j['pool'],
            j['creator'], date_str
        ]
        try:
            self.args, self.kwargs = json.loads(str(j['job_params']))
        except json.JSONDecodeError:
            pass
        else:
            for v in self.args:
                child = JobListParamItem(self, v)
                matchers.append(v)

            for k, v in self.kwargs.items():
                child = JobListParamItem(self, v, k)
                matchers.append('{}={}'.format(k,v))

        self._match_str = '^'.join(matchers)

    def jid(self):
        return self.job['jid']

    def paused(self):
        return self.job['paused']

    def in_progress(self):
        return self.job['in_progress']

    def done(self):
        return self.job['done']

    def matches(self, filter):
        return filter in self._match_str


class JobListHeaderView(QtWidgets.QHeaderView):

    def __init__(self, parent, orientation=QtCore.Qt.Horizontal):
        super(JobListHeaderView, self).__init__(orientation, parent)

        self.setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.setSectionsMovable(True)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_column_selection_requested)

        self._popup_menu = QtWidgets.QMenu(self)

        column_names, columns_visible = self.get_columns()
        for col_i, (col_name, col_visible) in enumerate(zip(column_names, columns_visible)):
            a = self._popup_menu.addAction(col_name, lambda i=col_i: self._on_column_visible_toggled(i))
            a.setCheckable(True)
            a.setChecked(col_visible)

    def get_columns(self):
        names = (
            'Status',
            'Type', 'Params', 'Label',
            'Owner', 
            'Pool', 'Priority', 
            'Node', 

            # 'Paused', 'In Progress', 'Done', 
            
            'Creator',
            'Created On', 

            'TIMESTAMP', 'ID'
        )
        visible = (
            True,                   # Status
            False,  False, True,    # Type, params, label
            False, False, False,    # Owner, pool, priority
            True,                   # Node
            # False, False, False,    # Paused, In progress, Done
            True,  True,            # Creator, created on
            False, False            # Timestamp, ID
        )

        return names, visible
    
    def _on_column_selection_requested(self, pos):
        self._popup_menu.popup(self.viewport().mapToGlobal(pos))
    
    def _on_column_visible_toggled(self, column):
        hidden = self.isSectionHidden(column)

        if column == 3:
            self.setStretchLastSection(not hidden)
        
        self.setSectionHidden(column, not hidden)


class JobList(QtWidgets.QTreeWidget):

    def __init__(self, parent, session):
        super(JobList, self).__init__(parent)
        self.session = session

        self.setHeader(JobListHeaderView(self))
        column_names, columns_visible = self.header().get_columns()
        self.setHeaderLabels(column_names)

        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.header().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        
        for col_i, col_visible in enumerate(columns_visible):
            self.setColumnHidden(col_i, not col_visible)

        self.setSortingEnabled(True)
        self.sortByColumn(len(column_names)-2, QtCore.Qt.DescendingOrder)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_popup_menu_request)

        self._popup_menu = QtWidgets.QMenu(self)

        self._filter = None
        self._jid_to_item = {}

    def set_item_filter(self, filter):
        self._filter = filter
        self.apply_filter()

    def refresh(self):
        #TODO: intelligent refresh: remove deleted jids, add created jids
        self._jid_to_item.clear()
        self.clear()
        for job in self.session.cmds.Jobs.list_jobs():
            item = JobListItem(self, job)
            self._jid_to_item[item.jid()] = item
            if self._filter and not item.matches(self._filter):
                item.setHidden(True)

    def apply_filter(self):
        root = self.invisibleRootItem()
        nb = root.childCount()
        for i in range(nb):
            item = root.child(i)
            if not self._filter:
                item.setHidden(False)
            else:
                item.setHidden(
                    not item.matches(self._filter)
                )

    def refresh_job(self, jid):
        item = self._jid_to_item.get(jid)
        if item is not None:
            job = self.session.cmds.Jobs.get_job_info(jid)
            item.set_job(job)
    
    def create_job(self, jid):
        job = self.session.cmds.Jobs.get_job_info(jid)
        item = JobListItem(self, job)
        self._jid_to_item[jid] = item
        if self._filter and not item.matches(self._filter):
            item.setHidden(True)
    
    def delete_job(self, jid):
        job_index = self.indexOfTopLevelItem(self._jid_to_item[jid])
        self.takeTopLevelItem(job_index)

    def _on_popup_menu_request(self, pos):
        item = self.itemAt(pos)
        if item is None:
            m = self._popup_menu
            m.clear()
            m.addAction('Refresh', self.refresh)

        else:
            item = item.job_item()
            m = self._popup_menu
            m.clear()
            if item.paused():
                m.addAction('Un-Pause', lambda item=item: self._unpause(item))
            if 'oid' in item.kwargs:
                oid = item.kwargs['oid']
                name = os.path.basename(oid)
                m.addAction('Goto "{}"'.format(name), lambda item=item: self._goto(item))
            m.addAction('Delete', lambda item=item: self._delete(item))

        self._popup_menu.popup(self.viewport().mapToGlobal(pos))

    def _unpause(self, item):
        self.session.cmds.Jobs.set_job_paused(item.jid(), False)

    def _delete(self, item):
        self.session.cmds.Jobs.delete_job(item.jid())

    def _goto(self, item):
        if not self.session.is_gui():
            return

        oid = str(item.kwargs['oid'])
        view = self.session.add_view('Flow', area=None, oid=oid)
        # ensure visible if tabbed:
        view.show()

class JobsView(DockedView):

    @classmethod
    def view_type_name(cls):
        return 'Jobs'

    def __init__(self, *args, **kwargs):
        super(JobsView, self).__init__(*args, **kwargs)

    def _build(self, top_parent, top_layout, main_parent, header_parent, header_layout):
        self.add_header_tool('*', '*', 'Duplicate View', self.duplicate_view)

        self._filter_le = QtWidgets.QLineEdit(main_parent)
        self._filter_le.setPlaceholderText('Filter Jobs...')
        self._filter_le.textChanged.connect(self._on_filter_change)

        self._job_list = JobList(main_parent, self.session)
        self._job_list_refreshed = False

        # Set job filter to default if defined
        # in environment (may be at session startup)
        if "JOBS_DEFAULT_FILTER" in os.environ:
            self._filter_le.setText(os.environ["JOBS_DEFAULT_FILTER"] + '_')

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        lo.addWidget(self._filter_le)
        lo.addWidget(self._job_list)

        main_parent.setLayout(lo)


        self.view_menu.setTitle('Jobs')

        a = self.view_menu.addAction('Refresh', self.refresh)
        self.view_menu.addSeparator()
        a = self.view_menu.addAction('Create Test Job', self.create_test_job)

    def _on_filter_change(self):
        self._job_list.set_item_filter(self._filter_le.text())

    def refresh(self):
        self._job_list.refresh()

    def create_test_job(self):
        jid = self.session.cmds.Jobs.create_flow_job(
            oid='/project/path/to/the/job_object',
            pool='test', 
            priority=50,
            paused=True,
        )
        print('NEW JOB ID:', jid)

    def on_show(self):
        if not self._job_list_refreshed:
            self.refresh()
            self._job_list_refreshed = True

    def receive_event(self, event, data):
        # Is it really a good thing to update job list items in background,
        # even if the view is not shown ?
        if event == 'joblist_touched':
            if self.isVisible():
                self._job_list.refresh() 

        elif event == 'job_touched':
            jid = data['jid']
            self._job_list.refresh_job(jid)
        elif event == 'job_created':
            jid = data['jid']
            self._job_list.create_job(jid)
        elif event == 'job_deleted':
            jid = data['jid']
            self._job_list.delete_job(jid)